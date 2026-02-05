"""
Content Analytics Platform - Database Queries
=============================================
Repository pattern implementation for database operations.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy import func, desc, and_, or_, text
from sqlalchemy.orm import Session

from .models import (
    YouTubeChannel, YouTubeVideo, YouTubeVideoSnapshot,
    YouTubeChannelSnapshot, YouTubeComment,
    InstagramAccount, InstagramPost, InstagramAccountSnapshot,
    MLPrediction, AnalyticsCache
)
from .connection import get_db_session
from loguru import logger


class YouTubeRepository:
    """Repository for YouTube data operations."""
    
    @staticmethod
    def upsert_channel(session: Session, data: Dict[str, Any]) -> YouTubeChannel:
        """Insert or update a YouTube channel."""
        channel = session.query(YouTubeChannel).filter_by(
            channel_id=data['channel_id']
        ).first()
        
        if channel:
            for key, value in data.items():
                if hasattr(channel, key) and value is not None:
                    setattr(channel, key, value)
            channel.updated_at = datetime.utcnow()
        else:
            channel = YouTubeChannel(**data)
            session.add(channel)
        
        session.flush()
        return channel
    
    @staticmethod
    def upsert_video(session: Session, data: Dict[str, Any]) -> YouTubeVideo:
        """Insert or update a YouTube video."""
        video = session.query(YouTubeVideo).filter_by(
            video_id=data['video_id']
        ).first()
        
        if video:
            for key, value in data.items():
                if hasattr(video, key) and value is not None:
                    setattr(video, key, value)
            video.updated_at = datetime.utcnow()
        else:
            video = YouTubeVideo(**data)
            session.add(video)
        
        session.flush()
        return video
    
    @staticmethod
    def create_video_snapshot(
        session: Session,
        video_id: str,
        views: int,
        likes: int,
        comments: int
    ) -> YouTubeVideoSnapshot:
        """Create a snapshot of video metrics."""
        # Get previous snapshot for delta calculation
        prev_snapshot = session.query(YouTubeVideoSnapshot).filter_by(
            video_id=video_id
        ).order_by(desc(YouTubeVideoSnapshot.snapshot_date)).first()
        
        snapshot = YouTubeVideoSnapshot(
            video_id=video_id,
            views=views,
            likes=likes,
            comments=comments,
            views_delta=views - prev_snapshot.views if prev_snapshot else None,
            likes_delta=likes - prev_snapshot.likes if prev_snapshot else None,
            comments_delta=comments - prev_snapshot.comments if prev_snapshot else None
        )
        session.add(snapshot)
        session.flush()
        return snapshot
    
    @staticmethod
    def create_channel_snapshot(
        session: Session,
        channel_id: str,
        subscribers: int,
        total_views: int,
        total_videos: int
    ) -> YouTubeChannelSnapshot:
        """Create a snapshot of channel metrics."""
        prev_snapshot = session.query(YouTubeChannelSnapshot).filter_by(
            channel_id=channel_id
        ).order_by(desc(YouTubeChannelSnapshot.snapshot_date)).first()
        
        snapshot = YouTubeChannelSnapshot(
            channel_id=channel_id,
            subscribers=subscribers,
            total_views=total_views,
            total_videos=total_videos,
            subscribers_delta=subscribers - prev_snapshot.subscribers if prev_snapshot else None,
            views_delta=total_views - prev_snapshot.total_views if prev_snapshot else None,
            videos_delta=total_videos - prev_snapshot.total_videos if prev_snapshot else None
        )
        session.add(snapshot)
        session.flush()
        return snapshot
    
    @staticmethod
    def get_channel(session: Session, channel_id: str) -> Optional[YouTubeChannel]:
        """Get channel by ID."""
        return session.query(YouTubeChannel).filter_by(channel_id=channel_id).first()
    
    @staticmethod
    def get_all_channels(session: Session, active_only: bool = True) -> List[YouTubeChannel]:
        """Get all tracked channels."""
        query = session.query(YouTubeChannel)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(desc(YouTubeChannel.subscribers)).all()
    
    @staticmethod
    def get_channel_videos(
        session: Session,
        channel_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[YouTubeVideo]:
        """Get videos for a channel."""
        return session.query(YouTubeVideo).filter_by(
            channel_id=channel_id
        ).order_by(desc(YouTubeVideo.published_at)).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_top_videos(
        session: Session,
        channel_id: str,
        metric: str = 'views',
        limit: int = 10
    ) -> List[YouTubeVideo]:
        """Get top performing videos by metric."""
        order_col = getattr(YouTubeVideo, metric, YouTubeVideo.views)
        return session.query(YouTubeVideo).filter_by(
            channel_id=channel_id
        ).order_by(desc(order_col)).limit(limit).all()
    
    @staticmethod
    def get_channel_growth(
        session: Session,
        channel_id: str,
        days: int = 30
    ) -> List[YouTubeChannelSnapshot]:
        """Get channel growth history."""
        since = datetime.utcnow() - timedelta(days=days)
        return session.query(YouTubeChannelSnapshot).filter(
            and_(
                YouTubeChannelSnapshot.channel_id == channel_id,
                YouTubeChannelSnapshot.snapshot_date >= since
            )
        ).order_by(YouTubeChannelSnapshot.snapshot_date).all()
    
    @staticmethod
    def get_video_performance(
        session: Session,
        video_id: str
    ) -> List[YouTubeVideoSnapshot]:
        """Get video performance history."""
        return session.query(YouTubeVideoSnapshot).filter_by(
            video_id=video_id
        ).order_by(YouTubeVideoSnapshot.snapshot_date).all()
    
    @staticmethod
    def get_recent_comments(
        session: Session,
        video_id: str,
        limit: int = 100
    ) -> List[YouTubeComment]:
        """Get recent comments for a video."""
        return session.query(YouTubeComment).filter_by(
            video_id=video_id
        ).order_by(desc(YouTubeComment.published_at)).limit(limit).all()
    
    @staticmethod
    def get_channel_stats_summary(session: Session, channel_id: str) -> Dict[str, Any]:
        """Get aggregated statistics for a channel."""
        result = session.query(
            func.count(YouTubeVideo.id).label('video_count'),
            func.sum(YouTubeVideo.views).label('total_views'),
            func.sum(YouTubeVideo.likes).label('total_likes'),
            func.sum(YouTubeVideo.comments).label('total_comments'),
            func.avg(YouTubeVideo.views).label('avg_views'),
            func.avg(YouTubeVideo.engagement_rate).label('avg_engagement')
        ).filter(YouTubeVideo.channel_id == channel_id).first()
        
        return {
            'video_count': result.video_count or 0,
            'total_views': int(result.total_views or 0),
            'total_likes': int(result.total_likes or 0),
            'total_comments': int(result.total_comments or 0),
            'avg_views': float(result.avg_views or 0),
            'avg_engagement': float(result.avg_engagement or 0)
        }

    @staticmethod
    def get_channels_count(session: Session) -> int:
        """Get total number of tracked channels."""
        return session.query(func.count(YouTubeChannel.id)).scalar() or 0

    @staticmethod
    def get_global_stats_summary(session: Session) -> Dict[str, Any]:
        """Get aggregated stats across ALL channels."""
        result = session.query(
            func.sum(YouTubeChannel.subscribers).label('total_subs'),
            func.sum(YouTubeChannel.total_views).label('total_views'),
            func.avg(YouTubeVideo.engagement_rate).label('avg_engagement')
        ).select_from(YouTubeChannel).outerjoin(YouTubeVideo).first()
        
        return {
            'total_subscribers': int(result.total_subs or 0),
            'total_views': int(result.total_views or 0),
            'avg_engagement': float(result.avg_engagement or 0)
        }


class InstagramRepository:
    """Repository for Instagram data operations."""
    
    @staticmethod
    def upsert_account(session: Session, data: Dict[str, Any]) -> InstagramAccount:
        """Insert or update an Instagram account."""
        account = session.query(InstagramAccount).filter_by(
            instagram_id=data['instagram_id']
        ).first()
        
        if account:
            for key, value in data.items():
                if hasattr(account, key) and value is not None:
                    setattr(account, key, value)
            account.updated_at = datetime.utcnow()
        else:
            account = InstagramAccount(**data)
            session.add(account)
        
        session.flush()
        return account
    
    @staticmethod
    def upsert_post(session: Session, data: Dict[str, Any]) -> InstagramPost:
        """Insert or update an Instagram post."""
        post = session.query(InstagramPost).filter_by(
            post_id=data['post_id']
        ).first()
        
        if post:
            for key, value in data.items():
                if hasattr(post, key) and value is not None:
                    setattr(post, key, value)
            post.updated_at = datetime.utcnow()
        else:
            post = InstagramPost(**data)
            session.add(post)
        
        session.flush()
        return post
    
    @staticmethod
    def create_account_snapshot(
        session: Session,
        instagram_id: str,
        followers: int,
        follows: int,
        media_count: int
    ) -> InstagramAccountSnapshot:
        """Create a snapshot of account metrics."""
        prev = session.query(InstagramAccountSnapshot).filter_by(
            instagram_id=instagram_id
        ).order_by(desc(InstagramAccountSnapshot.snapshot_date)).first()
        
        snapshot = InstagramAccountSnapshot(
            instagram_id=instagram_id,
            followers_count=followers,
            follows_count=follows,
            media_count=media_count,
            followers_delta=followers - prev.followers_count if prev else None,
            follows_delta=follows - prev.follows_count if prev else None
        )
        session.add(snapshot)
        session.flush()
        return snapshot
    
    @staticmethod
    def get_account(session: Session, instagram_id: str) -> Optional[InstagramAccount]:
        """Get account by ID."""
        return session.query(InstagramAccount).filter_by(instagram_id=instagram_id).first()
    
    @staticmethod
    def get_account_posts(
        session: Session,
        instagram_id: str,
        limit: int = 50
    ) -> List[InstagramPost]:
        """Get posts for an account."""
        return session.query(InstagramPost).filter_by(
            instagram_id=instagram_id
        ).order_by(desc(InstagramPost.timestamp)).limit(limit).all()
    
    @staticmethod
    def get_account_growth(
        session: Session,
        instagram_id: str,
        days: int = 30
    ) -> List[InstagramAccountSnapshot]:
        """Get account growth history."""
        since = datetime.utcnow() - timedelta(days=days)
        return session.query(InstagramAccountSnapshot).filter(
            and_(
                InstagramAccountSnapshot.instagram_id == instagram_id,
                InstagramAccountSnapshot.snapshot_date >= since
            )
        ).order_by(InstagramAccountSnapshot.snapshot_date).all()

    @staticmethod
    def get_accounts_count(session: Session) -> int:
        """Get total number of tracked accounts."""
        return session.query(func.count(InstagramAccount.id)).scalar() or 0

    @staticmethod
    def get_global_stats_summary(session: Session) -> Dict[str, Any]:
        """Get aggregated stats across ALL accounts."""
        # Note: This is an approximation since we don't store aggregate engagement in Account model
        # Real impl would join posts or use cache
        result = session.query(
            func.sum(InstagramAccount.followers_count).label('total_followers'),
            func.sum(InstagramAccount.media_count).label('total_media')
        ).first()
        
        # Get avg engagement from posts
        avg_eng = session.query(func.avg(InstagramPost.like_count)).scalar() or 0
        # Normalize arbitrarily for now if needed, or just return raw
        
        return {
            'total_followers': int(result.total_followers or 0),
            'total_reach': int(result.total_followers or 0) * 0.2, # Est reach
            'avg_engagement': float(avg_eng) / 1000 # Rough estimate
        }


class MLRepository:
    """Repository for ML predictions and model metrics."""
    
    @staticmethod
    def save_prediction(session: Session, data: Dict[str, Any]) -> MLPrediction:
        """Save an ML prediction."""
        prediction = MLPrediction(**data)
        session.add(prediction)
        session.flush()
        return prediction
    
    @staticmethod
    def get_predictions(
        session: Session,
        content_id: str,
        prediction_type: str = None
    ) -> List[MLPrediction]:
        """Get predictions for a content item."""
        query = session.query(MLPrediction).filter_by(content_id=content_id)
        if prediction_type:
            query = query.filter_by(prediction_type=prediction_type)
        return query.order_by(desc(MLPrediction.prediction_date)).all()


class CacheRepository:
    """Repository for analytics cache."""
    
    @staticmethod
    def get_cached(session: Session, cache_key: str) -> Optional[Dict]:
        """Get cached data if not expired."""
        cache = session.query(AnalyticsCache).filter(
            and_(
                AnalyticsCache.cache_key == cache_key,
                AnalyticsCache.expires_at > datetime.utcnow()
            )
        ).first()
        return cache.data if cache else None
    
    @staticmethod
    def set_cached(
        session: Session,
        cache_key: str,
        data: Dict,
        ttl_hours: int = 1,
        **kwargs
    ) -> AnalyticsCache:
        """Set cached data."""
        existing = session.query(AnalyticsCache).filter_by(cache_key=cache_key).first()
        
        if existing:
            existing.data = data
            existing.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            existing.created_at = datetime.utcnow()
            return existing
        
        cache = AnalyticsCache(
            cache_key=cache_key,
            data=data,
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours),
            **kwargs
        )
        session.add(cache)
        session.flush()
        return cache
    
    @staticmethod
    def clear_expired(session: Session) -> int:
        """Clear expired cache entries."""
        deleted = session.query(AnalyticsCache).filter(
            AnalyticsCache.expires_at < datetime.utcnow()
        ).delete()
        return deleted
