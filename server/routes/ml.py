"""
Content Analytics Platform - ML API Routes
==========================================
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

from src.database import get_db_session
from src.database.queries import YouTubeRepository
from src.ml import ViralPredictor, GrowthForecaster, SentimentAnalyzer

router = APIRouter()


# Pydantic models
class VideoForPrediction(BaseModel):
    title: str
    description: str = ""
    tags: List[str] = []
    duration_seconds: int = 0
    channel_subscribers: int = 0
    channel_avg_views: float = 0
    published_at: Optional[str] = None


class TrainRequest(BaseModel):
    channel_id: str
    viral_threshold: float = 2.0


# Lazy loaded ML models
_viral_predictor: Optional[ViralPredictor] = None
_forecaster: Optional[GrowthForecaster] = None
_sentiment_analyzer: Optional[SentimentAnalyzer] = None


def get_viral_predictor() -> ViralPredictor:
    """Lazy load viral predictor."""
    global _viral_predictor
    if _viral_predictor is None:
        _viral_predictor = ViralPredictor()
    return _viral_predictor


def get_forecaster() -> GrowthForecaster:
    """Lazy load forecaster."""
    global _forecaster
    if _forecaster is None:
        _forecaster = GrowthForecaster()
    return _forecaster


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Lazy load sentiment analyzer."""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = SentimentAnalyzer()
    return _sentiment_analyzer


@router.post("/predict/viral")
async def predict_viral(video: VideoForPrediction):
    """Predict viral potential for a video."""
    viral_predictor = get_viral_predictor()
    prediction = viral_predictor.predict(video.model_dump())
    return prediction


@router.post("/train/viral")
async def train_viral_model(request: TrainRequest):
    """Train viral prediction model on channel data."""
    with get_db_session() as session:
        videos = YouTubeRepository.get_channel_videos(
            session, request.channel_id, limit=500
        )
        
        if len(videos) < 50:
            raise HTTPException(
                status_code=400, 
                detail=f"Need at least 50 videos. Found: {len(videos)}"
            )
        
        channel = YouTubeRepository.get_channel(session, request.channel_id)
        
        # Prepare training data
        videos_data = [
            {
                'video_id': v.video_id,
                'title': v.title,
                'description': v.description or '',
                'tags': v.tags or [],
                'duration_seconds': v.duration_seconds or 0,
                'views': v.views,
                'published_at': v.published_at,
                'channel_subscribers': channel.subscribers if channel else 0,
                'channel_avg_views': sum(x.views for x in videos) / len(videos)
            }
            for v in videos
        ]
        
        viral_predictor = get_viral_predictor()
        metrics = viral_predictor.train(videos_data, viral_threshold=request.viral_threshold)
        return metrics


@router.get("/forecast/subscribers/{channel_id}")
async def forecast_subscribers(
    channel_id: str,
    periods: int = Query(30, ge=7, le=90)
):
    """Forecast subscriber growth."""
    with get_db_session() as session:
        snapshots = YouTubeRepository.get_channel_growth(session, channel_id, days=90)
        
        if len(snapshots) < 7:
            raise HTTPException(
                status_code=400,
                detail="Need at least 7 days of historical data"
            )
        
        historical = [
            {'date': s.snapshot_date, 'subscribers': s.subscribers}
            for s in snapshots
        ]
        
        forecaster = get_forecaster()
        forecast = forecaster.forecast_subscribers(historical, periods=periods)
        return forecast


@router.get("/forecast/views/{channel_id}")
async def forecast_views(
    channel_id: str,
    periods: int = Query(30, ge=7, le=90)
):
    """Forecast total views growth."""
    with get_db_session() as session:
        snapshots = YouTubeRepository.get_channel_growth(session, channel_id, days=90)
        
        if len(snapshots) < 7:
            raise HTTPException(
                status_code=400,
                detail="Need at least 7 days of historical data"
            )
        
        historical = [
            {'date': s.snapshot_date, 'views': s.total_views}
            for s in snapshots
        ]
        
        forecaster = get_forecaster()
        forecast = forecaster.forecast_views(historical, periods=periods)
        return forecast


@router.get("/sentiment/{video_id}")
async def analyze_video_sentiment(
    video_id: str,
    limit: int = Query(100, le=500)
):
    """Analyze sentiment of video comments."""
    with get_db_session() as session:
        comments = YouTubeRepository.get_recent_comments(session, video_id, limit=limit)
        
        if not comments:
            return {
                "video_id": video_id,
                "error": "No comments found"
            }
        
        comments_data = [{'text': c.text} for c in comments]
        sentiment_analyzer = get_sentiment_analyzer()
        analysis = sentiment_analyzer.get_sentiment_summary(comments_data)
        
        return {
            "video_id": video_id,
            **analysis
        }


@router.post("/sentiment/analyze")
async def analyze_text_sentiment(texts: List[str]):
    """Analyze sentiment of provided texts."""
    if not texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    results = []
    sentiment_analyzer = get_sentiment_analyzer()
    for text in texts[:100]:  # Limit to 100 texts
        result = sentiment_analyzer.analyze_text(text)
        results.append({
            "text": text[:100] + "..." if len(text) > 100 else text,
            **result
        })
    
    # Aggregate
    avg_score = sum(r['score'] for r in results) / len(results)
    distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
    for r in results:
        distribution[r['label']] += 1
    
    return {
        "analyzed_count": len(results),
        "avg_sentiment": round(avg_score, 4),
        "distribution": distribution,
        "results": results
    }


@router.get("/model/status")
async def get_model_status():
    """Get status of ML models."""
    """Get status of ML models."""
    viral_predictor = get_viral_predictor()
    forecaster = get_forecaster()
    
    return {
        "viral_predictor": {
            "loaded": viral_predictor.model is not None,
            "version": viral_predictor.MODEL_VERSION
        },
        "forecaster": {
            "prophet_available": forecaster.__class__.__name__ == "GrowthForecaster"
        },
        "sentiment_analyzer": {
            "loaded": True,
            "type": "VADER"
        }
    }
