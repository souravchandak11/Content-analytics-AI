"""
Content Analytics Platform - Analytics API Routes
=================================================
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger
import os
from seed_data.real_world_creators import MRBEAST_DATA

from src.database import get_db_session
from src.database.queries import YouTubeRepository, InstagramRepository
from src.analytics import YouTubeMetrics, InstagramMetrics, TrendAnalyzer
from seed_data.real_world_creators import MRBEAST_DATA, ALL_YOUTUBE_CREATORS, ALL_INSTAGRAM_CREATORS
import random

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview():
    """Get aggregated overview metrics for the main dashboard."""
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        # Use MrBeast Data
        return {
            "audience": {
                "total": MRBEAST_DATA['subscribers'] + 50000000,
                "youtube": MRBEAST_DATA['subscribers'],
                "instagram": 50000000,
                "delta": "+5.2%"
            },
            "reach": {
                "total": MRBEAST_DATA['total_views'],
                "delta": "+12.8%"
            },
            "engagement": {
                "average": MRBEAST_DATA.get('engagement_rate', 5.6),
                "delta": "+0.4%"
            },
            "platforms": {
                "youtube_active": 1,
                "instagram_active": 1
            }
        }

    with get_db_session() as session:
        # Get count of channels and accounts
        yt_count = YouTubeRepository.get_channels_count(session)
        ig_count = InstagramRepository.get_accounts_count(session)
        
        # Aggregate YouTube stats
        yt_stats = YouTubeRepository.get_global_stats_summary(session)
        # Aggregate Instagram stats
        ig_stats = InstagramRepository.get_global_stats_summary(session)
        
        total_subscribers = yt_stats['total_subscribers']
        total_followers = ig_stats['total_followers']
        
        return {
            "audience": {
                "total": total_subscribers + total_followers,
                "youtube": total_subscribers,
                "instagram": total_followers,
                "delta": "+5.2%" # Hardcoded for now without historical snapshots
            },
            "reach": {
                "total": yt_stats['total_views'] + ig_stats['total_reach'],
                "delta": "-1.8%"
            },
            "engagement": {
                "average": round((yt_stats['avg_engagement'] + ig_stats['avg_engagement']) / 2, 2),
                "delta": "+0.4%"
            },
            "platforms": {
                "youtube_active": yt_count,
                "instagram_active": ig_count
            }
        }


@router.get("/youtube/{channel_id}/metrics")
async def get_youtube_metrics(
    channel_id: str,
    days: int = Query(30, le=365)
):
    """Get comprehensive YouTube channel metrics."""
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        # Find creator by channel_id, default to MrBeast if not found or if checking main dashboard
        creator = next((data for name, data in ALL_YOUTUBE_CREATORS.items() if data['channel_id'] == channel_id), MRBEAST_DATA)
        
        return {
            "channel_id": channel_id,
            "title": creator['channel_name'],
            "subscribers": creator['subscribers'],
            "stats": {
                'avg_views': creator.get('avg_views_per_video', 0),
                'avg_likes': creator.get('avg_likes_per_video', 0),
                'avg_comments': creator.get('avg_comments_per_video', 0),
                'avg_engagement': creator.get('engagement_rate', 0)
            },
            "health_score": random.uniform(8.5, 9.9), # Dynamic healthy score
            "period_days": days
        }

    with get_db_session() as session:
        channel = YouTubeRepository.get_channel(session, channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        
        stats = YouTubeRepository.get_channel_stats_summary(session, channel_id)
        videos = YouTubeRepository.get_channel_videos(session, channel_id, limit=100)
        
        # Calculate health score
        upload_frequency = len([v for v in videos if v.published_at]) / max(days / 7, 1)
        
        health = YouTubeMetrics.channel_health_score(
            subscriber_growth_rate=2.0,  # Would need historical data
            avg_engagement_rate=stats['avg_engagement'],
            upload_frequency=upload_frequency,
            avg_views_per_video=stats['avg_views'],
            subscribers=channel.subscribers
        )
        
        return {
            "channel_id": channel_id,
            "title": channel.title,
            "subscribers": channel.subscribers,
            "stats": stats,
            "health_score": health,
            "period_days": days
        }


@router.get("/youtube/{channel_id}/trends")
async def get_youtube_trends(
    channel_id: str,
    days: int = Query(30, le=365)
):
    """Get trend analysis for YouTube channel."""
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        creator = next((data for name, data in ALL_YOUTUBE_CREATORS.items() if data['channel_id'] == channel_id), MRBEAST_DATA)
        base_subs = creator.get('subscribers', 1000000)
        base_views = creator.get('total_views', 100000000)
        
        return {
            "channel_id": channel_id,
            "period_days": days,
            "subscriber_trend": {
                'trend': 'up',
                'percentage': 12.5,
                'history': [int(base_subs * (0.9 + i*0.02)) for i in range(4)]
            },
            "views_trend": {
                'trend': 'up',
                'percentage': 8.4,
                'history': [int(base_views * (0.95 + i*0.01)) for i in range(4)]
            }
        }

    with get_db_session() as session:
        snapshots = YouTubeRepository.get_channel_growth(session, channel_id, days)
        
        if len(snapshots) < 3:
            raise HTTPException(status_code=400, detail="Insufficient data for trend analysis")
        
        # Prepare data for trend analysis
        data = [
            {'date': s.snapshot_date, 'subscribers': s.subscribers, 'views': s.total_views}
            for s in snapshots
        ]
        
        subscriber_trend = TrendAnalyzer.calculate_trend(data, 'subscribers')
        views_trend = TrendAnalyzer.calculate_trend(data, 'views')
        
        return {
            "channel_id": channel_id,
            "period_days": days,
            "subscriber_trend": subscriber_trend,
            "views_trend": views_trend
        }


@router.get("/youtube/{channel_id}/viral-videos")
async def get_viral_videos(
    channel_id: str,
    threshold: float = Query(2.0, ge=1.0, le=10.0)
):
    """Identify viral videos for a channel."""
    """Identify viral videos for a channel."""
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        creator = next((data for name, data in ALL_YOUTUBE_CREATORS.items() if data['channel_id'] == channel_id), MRBEAST_DATA)
        recent_viral = creator.get('recent_viral_videos', [])
        
        avg_views = creator.get('avg_views_per_video', 1000000)
        
        return {
            "channel_id": channel_id,
            "avg_views": int(avg_views),
            "threshold": threshold,
            "threshold_views": int(avg_views * threshold),
            "viral_count": len(recent_viral),
            "viral_videos": [
                {
                    "video_id": v.get('video_id', 'v1'),
                    "title": v.get('title', 'Viral Video'),
                    "views": v.get('views', 0),
                    "virality_factor": round(v.get('views', 0) / avg_views, 2) if avg_views > 0 else 0
                } for v in recent_viral
            ]
        }

    with get_db_session() as session:
        from src.database.models import YouTubeVideo
        
        videos = session.query(YouTubeVideo).filter_by(channel_id=channel_id).all()
        
        if not videos:
            raise HTTPException(status_code=404, detail="No videos found")
        
        avg_views = sum(v.views for v in videos) / len(videos)
        threshold_views = avg_views * threshold
        
        viral = [v for v in videos if v.views > threshold_views]
        viral.sort(key=lambda x: x.views, reverse=True)
        
        return {
            "channel_id": channel_id,
            "avg_views": int(avg_views),
            "threshold": threshold,
            "threshold_views": int(threshold_views),
            "viral_count": len(viral),
            "viral_videos": [
                {
                    "video_id": v.video_id,
                    "title": v.title,
                    "views": v.views,
                    "virality_factor": round(v.views / avg_views, 2)
                }
                for v in viral[:20]
            ]
        }


@router.get("/instagram/{instagram_id}/metrics")
async def get_instagram_metrics(
    instagram_id: str,
    days: int = Query(30, le=365)
):
    """Get comprehensive Instagram account metrics."""
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        # Find account by ID or just return MrBeast's IG data if not found (or if UC ID passed)
        account = next((data for name, data in ALL_INSTAGRAM_CREATORS.items() if data.get('instagram_id') == instagram_id), None)
        
        # If no direct match (e.g. UC ID passed), try to find by cross-referencing name or just use MrBeast
        if not account:
             # Just use MrBeast IG as fallback for any unknown ID in mock mode to keep UI alive
             account = next(iter(ALL_INSTAGRAM_CREATORS.values()))

        return {
            "instagram_id": instagram_id,
            "username": account['username'],
            "followers": account['followers'],
            "posts_analyzed": 50,
            "total_likes": int(account.get('avg_likes_per_post', 100000) * 50),
            "total_comments": int(account.get('avg_likes_per_post', 100000) * 0.01 * 50),
            "avg_engagement_rate": account.get('engagement_rate', 3.5),
            "period_days": days
        }

    with get_db_session() as session:
        account = InstagramRepository.get_account(session, instagram_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        posts = InstagramRepository.get_account_posts(session, instagram_id, limit=50)
        
        total_likes = sum(p.like_count for p in posts)
        total_comments = sum(p.comments_count for p in posts)
        
        avg_engagement = sum(
            InstagramMetrics.engagement_rate(p.like_count, p.comments_count, account.followers_count)
            for p in posts
        ) / len(posts) if posts else 0
        
        return {
            "instagram_id": instagram_id,
            "username": account.username,
            "followers": account.followers_count,
            "posts_analyzed": len(posts),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "avg_engagement_rate": round(avg_engagement, 4),
            "period_days": days
        }


@router.get("/instagram/{instagram_id}/best-times")
async def get_best_posting_times(instagram_id: str):
    """Analyze best posting times for Instagram account."""
    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        return {
            "instagram_id": instagram_id,
            "posts_analyzed": 50,
            "best_day": "Wednesday",
            "best_time": "18:00",
            "heatmap": [
                {"day": "Monday", "hour": 18, "engagement": 4.5},
                {"day": "Wednesday", "hour": 18, "engagement": 5.2},
                {"day": "Friday", "hour": 12, "engagement": 4.8}
            ]
        }

    with get_db_session() as session:
        posts = InstagramRepository.get_account_posts(session, instagram_id, limit=100)
        
        if len(posts) < 10:
            raise HTTPException(status_code=400, detail="Need at least 10 posts for analysis")
        
        account = InstagramRepository.get_account(session, instagram_id)
        
        posts_data = [
            {
                'timestamp': p.timestamp,
                'like_count': p.like_count,
                'comments_count': p.comments_count,
                'engagement_rate': InstagramMetrics.engagement_rate(
                    p.like_count, p.comments_count, account.followers_count
                )
            }
            for p in posts if p.timestamp
        ]
        
        analysis = InstagramMetrics.best_posting_time(posts_data)
        
        return {
            "instagram_id": instagram_id,
            "posts_analyzed": len(posts_data),
            **analysis
        }


@router.get("/compare")
async def compare_channels(
    platform: str = Query(..., regex="^(youtube|instagram)$"),
    ids: str = Query(..., description="Comma-separated IDs")
):
    """Compare multiple channels/accounts."""
    id_list = [i.strip() for i in ids.split(',')]
    
    if len(id_list) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 IDs to compare")
    
    if len(id_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 IDs allowed")
    
    results = []

    if os.getenv('USE_MOCK_DATA', 'False').lower() == 'true':
        # Generate mock comparison
        for i, cid in enumerate(id_list):
            if platform == 'youtube':
                creator = next((data for name, data in ALL_YOUTUBE_CREATORS.items() if data['channel_id'] == cid), MRBEAST_DATA)
                results.append({
                    "id": cid,
                    "name": creator.get('channel_name', f"Channel {i}"),
                    "subscribers": creator.get('subscribers', 1000000 * (i+1)),
                    "total_views": creator.get('total_views', 100000000 * (i+1)),
                    "avg_views": creator.get('avg_views_per_video', 500000),
                    "avg_engagement": creator.get('engagement_rate', 3.5 + (i * 0.5))
                })
            else:
                creator = next((data for name, data in ALL_INSTAGRAM_CREATORS.items() if data.get('instagram_id') == cid), None) or next(iter(ALL_INSTAGRAM_CREATORS.values()))
                results.append({
                    "id": cid,
                    "name": creator.get('username', f"User {i}"),
                    "followers": creator.get('followers', 500000),
                    "media_count": creator.get('posts', 100),
                    "avg_engagement": creator.get('engagement_rate', 2.5)
                })
        
        return {
            "platform": platform,
            "compared_count": len(results),
            "data": results
        }
    
    with get_db_session() as session:
        if platform == 'youtube':
            for channel_id in id_list:
                channel = YouTubeRepository.get_channel(session, channel_id)
                if channel:
                    stats = YouTubeRepository.get_channel_stats_summary(session, channel_id)
                    results.append({
                        "id": channel_id,
                        "name": channel.title,
                        "subscribers": channel.subscribers,
                        "total_views": channel.total_views,
                        "avg_views": stats['avg_views'],
                        "avg_engagement": stats['avg_engagement']
                    })
        else:
            for instagram_id in id_list:
                account = InstagramRepository.get_account(session, instagram_id)
                if account:
                    results.append({
                        "id": instagram_id,
                        "name": account.username,
                        "followers": account.followers_count,
                        "media_count": account.media_count,
                        "avg_engagement": account.avg_engagement_rate or 0
                    })
    
    return {
        "platform": platform,
        "compared_count": len(results),
        "data": results
    }
