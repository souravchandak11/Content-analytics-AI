"""Database Query Classes for Content Analytics Tool."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import (
    YouTubeChannel, YouTubeChannelSnapshot, YouTubeVideo, YouTubeComment,
    InstagramAccount, InstagramAccountSnapshot, InstagramPost
)


class YouTubeQueries:
    """Query class for YouTube data operations."""
    
    def __init__(self, db: Session):
        """Initialize with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def save_channel(self, channel_data: Dict[str, Any]) -> YouTubeChannel:
        """Save or update a YouTube channel.
        
        Args:
            channel_data: Dictionary with channel information
            
        Returns:
            YouTubeChannel instance
        """
        channel = self.db.query(YouTubeChannel).filter(
            YouTubeChannel.channel_id == channel_data['channel_id']
        ).first()
        
        if channel:
            channel.title = channel_data.get('title', channel.title)
            channel.description = channel_data.get('description', channel.description)
            channel.thumbnail_url = channel_data.get('thumbnail_url', channel.thumbnail_url)
            channel.updated_at = datetime.utcnow()
        else:
            channel = YouTubeChannel(
                channel_id=channel_data['channel_id'],
                title=channel_data['title'],
                description=channel_data.get('description', ''),
                thumbnail_url=channel_data.get('thumbnail_url', '')
            )
            self.db.add(channel)
        
        # Create snapshot
        snapshot = YouTubeChannelSnapshot(
            channel_id=channel_data['channel_id'],
            subscriber_count=channel_data.get('subscriber_count', 0),
            video_count=channel_data.get('video_count', 0),
            view_count=channel_data.get('view_count', 0)
        )
        self.db.add(snapshot)
        
        try:
            self.db.commit()
            self.db.refresh(channel)
        except Exception as e:
            self.db.rollback()
            raise e
        
        return channel
    
    def save_video(self, video_data: Dict[str, Any]) -> YouTubeVideo:
        """Save or update a YouTube video.
        
        Args:
            video_data: Dictionary with video information
            
        Returns:
            YouTubeVideo instance
        """
        video = self.db.query(YouTubeVideo).filter(
            YouTubeVideo.video_id == video_data['video_id']
        ).first()
        
        published_at = video_data.get('published_at')
        if isinstance(published_at, str):
            try:
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except ValueError:
                published_at = None
        
        if video:
            video.title = video_data.get('title', video.title)
            video.description = video_data.get('description', video.description)
            video.thumbnail_url = video_data.get('thumbnail_url', video.thumbnail_url)
            video.view_count = video_data.get('view_count', video.view_count)
            video.like_count = video_data.get('like_count', video.like_count)
            video.comment_count = video_data.get('comment_count', video.comment_count)
            video.updated_at = datetime.utcnow()
        else:
            video = YouTubeVideo(
                video_id=video_data['video_id'],
                channel_id=video_data['channel_id'],
                title=video_data['title'],
                description=video_data.get('description', ''),
                thumbnail_url=video_data.get('thumbnail_url', ''),
                published_at=published_at,
                view_count=video_data.get('view_count', 0),
                like_count=video_data.get('like_count', 0),
                comment_count=video_data.get('comment_count', 0)
            )
            self.db.add(video)
        
        try:
            self.db.commit()
            self.db.refresh(video)
        except Exception as e:
            self.db.rollback()
            raise e
        
        return video
    
    def save_comment(self, comment_data: Dict[str, Any], sentiment_score: Optional[float] = None) -> YouTubeComment:
        """Save a YouTube comment.
        
        Args:
            comment_data: Dictionary with comment information
            sentiment_score: Optional sentiment score (-1 to 1)
            
        Returns:
            YouTubeComment instance
        """
        comment = self.db.query(YouTubeComment).filter(
            YouTubeComment.comment_id == comment_data['comment_id']
        ).first()
        
        published_at = comment_data.get('published_at')
        if isinstance(published_at, str):
            try:
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            except ValueError:
                published_at = None
        
        if not comment:
            comment = YouTubeComment(
                comment_id=comment_data['comment_id'],
                video_id=comment_data['video_id'],
                author=comment_data.get('author', ''),
                text=comment_data.get('text', ''),
                like_count=comment_data.get('like_count', 0),
                sentiment_score=sentiment_score,
                published_at=published_at
            )
            self.db.add(comment)
            
            try:
                self.db.commit()
                self.db.refresh(comment)
            except Exception as e:
                self.db.rollback()
                raise e
        
        return comment
    
    def get_channel_history(self, channel_id: str, limit: int = 30) -> List[YouTubeChannelSnapshot]:
        """Get channel snapshot history.
        
        Args:
            channel_id: YouTube channel ID
            limit: Maximum number of snapshots to return
            
        Returns:
            List of YouTubeChannelSnapshot instances
        """
        return self.db.query(YouTubeChannelSnapshot).filter(
            YouTubeChannelSnapshot.channel_id == channel_id
        ).order_by(desc(YouTubeChannelSnapshot.snapshot_date)).limit(limit).all()
    
    def get_top_videos(self, channel_id: str, limit: int = 10) -> List[YouTubeVideo]:
        """Get top videos by view count.
        
        Args:
            channel_id: YouTube channel ID
            limit: Maximum number of videos to return
            
        Returns:
            List of YouTubeVideo instances
        """
        return self.db.query(YouTubeVideo).filter(
            YouTubeVideo.channel_id == channel_id
        ).order_by(desc(YouTubeVideo.view_count)).limit(limit).all()
    
    def get_comments_with_sentiment(self, video_id: str) -> List[YouTubeComment]:
        """Get comments for a video with sentiment scores.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of YouTubeComment instances
        """
        return self.db.query(YouTubeComment).filter(
            YouTubeComment.video_id == video_id
        ).all()
    
    def get_all_channels(self) -> List[YouTubeChannel]:
        """Get all tracked YouTube channels.
        
        Returns:
            List of YouTubeChannel instances
        """
        return self.db.query(YouTubeChannel).all()


class InstagramQueries:
    """Query class for Instagram data operations."""
    
    def __init__(self, db: Session):
        """Initialize with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def save_account(self, account_data: Dict[str, Any]) -> InstagramAccount:
        """Save or update an Instagram account.
        
        Args:
            account_data: Dictionary with account information
            
        Returns:
            InstagramAccount instance
        """
        account = self.db.query(InstagramAccount).filter(
            InstagramAccount.account_id == account_data['account_id']
        ).first()
        
        if account:
            account.username = account_data.get('username', account.username)
            account.name = account_data.get('name', account.name)
            account.biography = account_data.get('biography', account.biography)
            account.profile_picture_url = account_data.get('profile_picture_url', account.profile_picture_url)
            account.updated_at = datetime.utcnow()
        else:
            account = InstagramAccount(
                account_id=account_data['account_id'],
                username=account_data['username'],
                name=account_data.get('name', ''),
                biography=account_data.get('biography', ''),
                profile_picture_url=account_data.get('profile_picture_url', '')
            )
            self.db.add(account)
        
        # Create snapshot
        snapshot = InstagramAccountSnapshot(
            account_id=account_data['account_id'],
            followers_count=account_data.get('followers_count', 0),
            follows_count=account_data.get('follows_count', 0),
            media_count=account_data.get('media_count', 0)
        )
        self.db.add(snapshot)
        
        try:
            self.db.commit()
            self.db.refresh(account)
        except Exception as e:
            self.db.rollback()
            raise e
        
        return account
    
    def save_post(self, post_data: Dict[str, Any], account_id: str) -> InstagramPost:
        """Save or update an Instagram post.
        
        Args:
            post_data: Dictionary with post information
            account_id: Instagram account ID
            
        Returns:
            InstagramPost instance
        """
        post = self.db.query(InstagramPost).filter(
            InstagramPost.post_id == post_data['post_id']
        ).first()
        
        timestamp = post_data.get('timestamp')
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                timestamp = None
        
        if post:
            post.caption = post_data.get('caption', post.caption)
            post.media_url = post_data.get('media_url', post.media_url)
            post.thumbnail_url = post_data.get('thumbnail_url', post.thumbnail_url)
            post.like_count = post_data.get('like_count', post.like_count)
            post.comments_count = post_data.get('comments_count', post.comments_count)
            post.updated_at = datetime.utcnow()
        else:
            post = InstagramPost(
                post_id=post_data['post_id'],
                account_id=account_id,
                caption=post_data.get('caption', ''),
                media_type=post_data.get('media_type', ''),
                media_url=post_data.get('media_url', ''),
                thumbnail_url=post_data.get('thumbnail_url', ''),
                permalink=post_data.get('permalink', ''),
                like_count=post_data.get('like_count', 0),
                comments_count=post_data.get('comments_count', 0),
                timestamp=timestamp
            )
            self.db.add(post)
        
        try:
            self.db.commit()
            self.db.refresh(post)
        except Exception as e:
            self.db.rollback()
            raise e
        
        return post
    
    def get_account_history(self, account_id: str, limit: int = 30) -> List[InstagramAccountSnapshot]:
        """Get account snapshot history.
        
        Args:
            account_id: Instagram account ID
            limit: Maximum number of snapshots to return
            
        Returns:
            List of InstagramAccountSnapshot instances
        """
        return self.db.query(InstagramAccountSnapshot).filter(
            InstagramAccountSnapshot.account_id == account_id
        ).order_by(desc(InstagramAccountSnapshot.snapshot_date)).limit(limit).all()
    
    def get_recent_posts(self, account_id: str, limit: int = 20) -> List[InstagramPost]:
        """Get recent posts for an account.
        
        Args:
            account_id: Instagram account ID
            limit: Maximum number of posts to return
            
        Returns:
            List of InstagramPost instances
        """
        return self.db.query(InstagramPost).filter(
            InstagramPost.account_id == account_id
        ).order_by(desc(InstagramPost.timestamp)).limit(limit).all()
    
    def get_all_accounts(self) -> List[InstagramAccount]:
        """Get all tracked Instagram accounts.
        
        Returns:
            List of InstagramAccount instances
        """
        return self.db.query(InstagramAccount).all()
