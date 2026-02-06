"""
Content Analytics Platform - Instagram API Routes
=================================================
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from loguru import logger

from src.database import get_db_session
from src.database.queries import InstagramRepository
from src.api import InstagramClient, InstagramAPIError
from src.etl import DataPipeline
import os
import random
from seed_data.real_world_creators import ALL_INSTAGRAM_CREATORS, INSTAGRAM_THUMBNAILS

router = APIRouter()


# Pydantic models
class AccountResponse(BaseModel):
    instagram_id: str
    username: str
    followers_count: int
    follows_count: int
    media_count: int
    avg_engagement_rate: Optional[float] = None
    
    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    post_id: str
    caption: Optional[str] = None
    media_type: str
    like_count: int
    comments_count: int
    engagement_rate: Optional[float] = None
    timestamp: Optional[datetime] = None
    permalink: Optional[str] = None
    
    class Config:
        from_attributes = True


class CollectionRequest(BaseModel):
    user_id: str = "me"
    max_posts: int = 50
    collect_insights: bool = True


# Endpoints
@router.get("/accounts")
async def list_accounts():
    """Get all tracked Instagram accounts."""
    with get_db_session() as session:
        from src.database.models import InstagramAccount
        accounts = session.query(InstagramAccount).filter_by(is_active=True).all()
        return [AccountResponse.model_validate(a) for a in accounts]


@router.get("/accounts/{instagram_id}", response_model=AccountResponse)
async def get_account(instagram_id: str):
    """Get Instagram account details."""
    with get_db_session() as session:
        account = InstagramRepository.get_account(session, instagram_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return AccountResponse.model_validate(account)


@router.get("/accounts/{instagram_id}/posts", response_model=List[PostResponse])
async def get_account_posts(
    instagram_id: str,
    limit: int = Query(50, le=100)
):
    """Get posts for an account."""
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        # Generate mock posts
        mock_posts = []
        for i in range(min(limit, 12)):
            mock_posts.append({
                "post_id": f"rec{i}",
                "caption": f"Always pushing the boundaries! 🚀 #{i}",
                "media_type": random.choice(["IMAGE", "VIDEO", "CAROUSEL_ALBUM"]),
                "like_count": random.randint(100000, 5000000),
                "comments_count": random.randint(1000, 50000),
                "engagement_rate": random.uniform(2.5, 8.0),
                "timestamp": datetime.now(),
                "thumbnail_url": list(INSTAGRAM_THUMBNAILS)[i % len(INSTAGRAM_THUMBNAILS)] if INSTAGRAM_THUMBNAILS else None,
                "media_url": list(INSTAGRAM_THUMBNAILS)[i % len(INSTAGRAM_THUMBNAILS)] if INSTAGRAM_THUMBNAILS else None
            })
        return mock_posts

    with get_db_session() as session:
        posts = InstagramRepository.get_account_posts(
            session, instagram_id, limit=limit
        )
        return [PostResponse.model_validate(p) for p in posts]


@router.get("/accounts/{instagram_id}/growth")
async def get_account_growth(
    instagram_id: str,
    days: int = Query(30, le=365)
):
    """Get account growth history."""
    with get_db_session() as session:
        snapshots = InstagramRepository.get_account_growth(session, instagram_id, days)
        
        return {
            "instagram_id": instagram_id,
            "period_days": days,
            "snapshots": [
                {
                    "date": s.snapshot_date.isoformat(),
                    "followers_count": s.followers_count,
                    "follows_count": s.follows_count,
                    "media_count": s.media_count,
                    "followers_delta": s.followers_delta
                }
                for s in snapshots
            ]
        }


@router.get("/accounts/{instagram_id}/stats")
async def get_account_stats(instagram_id: str):
    """Get account statistics."""
    from src.analytics import InstagramMetrics
    
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        account = next((data for name, data in ALL_INSTAGRAM_CREATORS.items() if data.get('instagram_id') == instagram_id), next(iter(ALL_INSTAGRAM_CREATORS.values())))
        likes = account.get('avg_likes_per_post', 500000)
        return {
            "instagram_id": instagram_id,
            "username": account['username'],
            "followers_count": account['followers'],
            "posts_analyzed": 50,
            "total_likes": likes * 50,
            "total_comments": likes * 0.02 * 50,
            "avg_likes_per_post": likes,
            "avg_comments_per_post": likes * 0.02,
            "avg_engagement_rate": account.get('engagement_rate', 4.5)
        }
    
    with get_db_session() as session:
        account = InstagramRepository.get_account(session, instagram_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        posts = InstagramRepository.get_account_posts(session, instagram_id, limit=50)
        
        total_likes = sum(p.like_count for p in posts)
        total_comments = sum(p.comments_count for p in posts)
        avg_engagement = account.avg_engagement_rate or 0
        
        return {
            "instagram_id": instagram_id,
            "username": account.username,
            "followers_count": account.followers_count,
            "posts_analyzed": len(posts),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_likes_per_post": total_likes / len(posts) if posts else 0,
            "avg_comments_per_post": total_comments / len(posts) if posts else 0,
            "avg_engagement_rate": round(avg_engagement, 4)
        }


@router.post("/accounts/collect")
async def collect_account_data(request: CollectionRequest):
    """Trigger data collection for an account."""
    try:
        pipeline = DataPipeline()
        result = pipeline.collect_instagram_account(
            request.user_id,
            max_posts=request.max_posts,
            collect_insights=request.collect_insights
        )
        return result
    except InstagramAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Collection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
