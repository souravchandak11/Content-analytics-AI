"""
Content Analytics Platform - Analytics API Routes
=================================================
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

from src.database import get_db_session
from src.database.queries import YouTubeRepository, InstagramRepository
from src.analytics import YouTubeMetrics, InstagramMetrics, TrendAnalyzer

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview():
    """Get aggregated overview metrics for the main dashboard."""
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
