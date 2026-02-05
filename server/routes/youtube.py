"""
Content Analytics Platform - YouTube API Routes
================================================
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from loguru import logger

from src.database import get_db_session
from src.database.queries import YouTubeRepository
from src.api import YouTubeClient, QuotaExceededError
from src.etl import DataPipeline

router = APIRouter()


# Pydantic models
class ChannelResponse(BaseModel):
    channel_id: str
    title: str
    subscribers: int
    total_views: int
    total_videos: int
    thumbnail_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class VideoResponse(BaseModel):
    video_id: str
    title: str
    views: int
    likes: int
    comments: int
    engagement_rate: Optional[float] = None
    published_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class CollectionRequest(BaseModel):
    channel_id: str
    max_videos: int = 50
    collect_comments: bool = True


# Endpoints
@router.get("/channels", response_model=List[ChannelResponse])
async def list_channels():
    """Get all tracked YouTube channels."""
    with get_db_session() as session:
        channels = YouTubeRepository.get_all_channels(session)
        return [ChannelResponse.model_validate(c) for c in channels]


@router.get("/channels/{channel_id}", response_model=ChannelResponse)
async def get_channel(channel_id: str):
    """Get YouTube channel details."""
    with get_db_session() as session:
        channel = YouTubeRepository.get_channel(session, channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        return ChannelResponse.model_validate(channel)


@router.get("/channels/{channel_id}/videos", response_model=List[VideoResponse])
async def get_channel_videos(
    channel_id: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get videos for a channel."""
    with get_db_session() as session:
        videos = YouTubeRepository.get_channel_videos(
            session, channel_id, limit=limit, offset=offset
        )
        return [VideoResponse.model_validate(v) for v in videos]


@router.get("/channels/{channel_id}/top-videos", response_model=List[VideoResponse])
async def get_top_videos(
    channel_id: str,
    metric: str = Query("views", regex="^(views|likes|comments|engagement_rate)$"),
    limit: int = Query(10, le=50)
):
    """Get top performing videos by metric."""
    with get_db_session() as session:
        videos = YouTubeRepository.get_top_videos(
            session, channel_id, metric=metric, limit=limit
        )
        return [VideoResponse.model_validate(v) for v in videos]


@router.get("/channels/{channel_id}/stats")
async def get_channel_stats(channel_id: str):
    """Get aggregated channel statistics."""
    with get_db_session() as session:
        channel = YouTubeRepository.get_channel(session, channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        stats = YouTubeRepository.get_channel_stats_summary(session, channel_id)
        
        return {
            "channel_id": channel_id,
            "title": channel.title,
            "subscribers": channel.subscribers,
            **stats
        }


@router.get("/channels/{channel_id}/growth")
async def get_channel_growth(
    channel_id: str,
    days: int = Query(30, le=365)
):
    """Get channel growth history."""
    with get_db_session() as session:
        snapshots = YouTubeRepository.get_channel_growth(session, channel_id, days)
        
        return {
            "channel_id": channel_id,
            "period_days": days,
            "snapshots": [
                {
                    "date": s.snapshot_date.isoformat(),
                    "subscribers": s.subscribers,
                    "total_views": s.total_views,
                    "total_videos": s.total_videos,
                    "subscribers_delta": s.subscribers_delta,
                    "views_delta": s.views_delta
                }
                for s in snapshots
            ]
        }


@router.post("/channels/collect")
async def collect_channel_data(request: CollectionRequest):
    """Trigger data collection for a channel."""
    try:
        pipeline = DataPipeline()
        result = pipeline.collect_youtube_channel(
            request.channel_id,
            max_videos=request.max_videos,
            collect_comments=request.collect_comments
        )
        return result
    except QuotaExceededError:
        raise HTTPException(status_code=429, detail="API quota exceeded")
    except Exception as e:
        logger.error(f"Collection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_channels(q: str = Query(..., min_length=2)):
    """Search for YouTube channels."""
    try:
        client = YouTubeClient()
        results = client.search_channels(q, max_results=10)
        return {"results": results, "quota_used": client.quota_used}
    except QuotaExceededError:
        raise HTTPException(status_code=429, detail="API quota exceeded")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
