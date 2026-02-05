"""
Content Analytics Platform - Database Models
============================================
SQLAlchemy ORM models for YouTube and Instagram analytics data.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey, 
    Index, Integer, String, Text, JSON, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

Base = declarative_base()


# =============================================================================
# YOUTUBE MODELS
# =============================================================================

class YouTubeChannel(Base):
    """YouTube Channel data model."""
    __tablename__ = 'youtube_channels'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    custom_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Current metrics (updated regularly)
    subscribers: Mapped[int] = mapped_column(BigInteger, default=0)
    total_views: Mapped[int] = mapped_column(BigInteger, default=0)
    total_videos: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    banner_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    keywords: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Tracking
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    videos: Mapped[List["YouTubeVideo"]] = relationship(
        "YouTubeVideo", 
        back_populates="channel", 
        cascade="all, delete-orphan"
    )
    snapshots: Mapped[List["YouTubeChannelSnapshot"]] = relationship(
        "YouTubeChannelSnapshot", 
        back_populates="channel", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<YouTubeChannel(id={self.id}, title='{self.title}', subscribers={self.subscribers})>"


class YouTubeVideo(Base):
    """YouTube Video data model."""
    __tablename__ = 'youtube_videos'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    channel_id: Mapped[str] = mapped_column(String(100), ForeignKey('youtube_channels.channel_id'), nullable=False)
    
    # Content metadata
    title: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    duration: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # ISO 8601 duration
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Categorization
    category_id: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    default_language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Current metrics
    views: Mapped[int] = mapped_column(BigInteger, default=0, index=True)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    dislikes: Mapped[int] = mapped_column(Integer, default=0)  # Historical, may be 0
    comments: Mapped[int] = mapped_column(Integer, default=0)
    
    # Engagement metrics (calculated)
    engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    like_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    comment_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Media
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status
    privacy_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    made_for_kids: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # ML predictions
    viral_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_views_7d: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Tracking
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    channel: Mapped["YouTubeChannel"] = relationship("YouTubeChannel", back_populates="videos")
    snapshots: Mapped[List["YouTubeVideoSnapshot"]] = relationship(
        "YouTubeVideoSnapshot", 
        back_populates="video", 
        cascade="all, delete-orphan"
    )
    comments_list: Mapped[List["YouTubeComment"]] = relationship(
        "YouTubeComment", 
        back_populates="video", 
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_video_channel_published', 'channel_id', 'published_at'),
        Index('idx_video_views_desc', 'views'),
    )
    
    def __repr__(self) -> str:
        return f"<YouTubeVideo(id={self.id}, title='{self.title[:50] if self.title else ''}...', views={self.views})>"


class YouTubeVideoSnapshot(Base):
    """Historical snapshots of video metrics for trend analysis."""
    __tablename__ = 'youtube_video_snapshots'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String(50), ForeignKey('youtube_videos.video_id'), nullable=False)
    
    # Metrics at snapshot time
    views: Mapped[int] = mapped_column(BigInteger, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    
    # Growth metrics (calculated from previous snapshot)
    views_delta: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    likes_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comments_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    video: Mapped["YouTubeVideo"] = relationship("YouTubeVideo", back_populates="snapshots")
    
    __table_args__ = (
        Index('idx_snapshot_video_date', 'video_id', 'snapshot_date'),
        UniqueConstraint('video_id', 'snapshot_date', name='uq_video_snapshot_date'),
    )


class YouTubeChannelSnapshot(Base):
    """Historical snapshots of channel metrics."""
    __tablename__ = 'youtube_channel_snapshots'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(100), ForeignKey('youtube_channels.channel_id'), nullable=False)
    
    # Metrics at snapshot time
    subscribers: Mapped[int] = mapped_column(BigInteger, default=0)
    total_views: Mapped[int] = mapped_column(BigInteger, default=0)
    total_videos: Mapped[int] = mapped_column(Integer, default=0)
    
    # Growth metrics
    subscribers_delta: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    views_delta: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    videos_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    channel: Mapped["YouTubeChannel"] = relationship("YouTubeChannel", back_populates="snapshots")
    
    __table_args__ = (
        Index('idx_channel_snapshot_date', 'channel_id', 'snapshot_date'),
    )


class YouTubeComment(Base):
    """YouTube video comments for sentiment analysis."""
    __tablename__ = 'youtube_comments'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    video_id: Mapped[str] = mapped_column(String(50), ForeignKey('youtube_videos.video_id'), nullable=False)
    
    # Comment content
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_channel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metrics
    likes: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Sentiment analysis results
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # -1.0 to 1.0
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # positive/negative/neutral
    sentiment_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # NLP extracted data
    topics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    entities: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    video: Mapped["YouTubeVideo"] = relationship("YouTubeVideo", back_populates="comments_list")


# =============================================================================
# INSTAGRAM MODELS
# =============================================================================

class InstagramAccount(Base):
    """Instagram Business/Creator account data model."""
    __tablename__ = 'instagram_accounts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instagram_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    
    # Profile info
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Account type
    account_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # BUSINESS, CREATOR, PERSONAL
    
    # Current metrics
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    follows_count: Mapped[int] = mapped_column(Integer, default=0)
    media_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Engagement averages
    avg_likes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_comments: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Tracking
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts: Mapped[List["InstagramPost"]] = relationship(
        "InstagramPost", 
        back_populates="account", 
        cascade="all, delete-orphan"
    )
    snapshots: Mapped[List["InstagramAccountSnapshot"]] = relationship(
        "InstagramAccountSnapshot", 
        back_populates="account", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<InstagramAccount(id={self.id}, username='{self.username}', followers={self.followers_count})>"


class InstagramPost(Base):
    """Instagram post/media data model."""
    __tablename__ = 'instagram_posts'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    instagram_id: Mapped[str] = mapped_column(String(100), ForeignKey('instagram_accounts.instagram_id'), nullable=False)
    
    # Content
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_type: Mapped[str] = mapped_column(String(50), nullable=True)  # IMAGE, VIDEO, CAROUSEL_ALBUM
    media_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    permalink: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timing
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    # Engagement metrics
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Insights (requires Instagram Business/Creator account)
    engagement: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    impressions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reach: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    saved: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    shares: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Video-specific metrics
    video_views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Calculated metrics
    engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Hashtag analysis
    hashtags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    mentions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # ML predictions
    viral_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Tracking
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account: Mapped["InstagramAccount"] = relationship("InstagramAccount", back_populates="posts")
    
    __table_args__ = (
        Index('idx_post_account_timestamp', 'instagram_id', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<InstagramPost(id={self.id}, type='{self.media_type}', likes={self.like_count})>"


class InstagramAccountSnapshot(Base):
    """Historical snapshots of Instagram account metrics."""
    __tablename__ = 'instagram_account_snapshots'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instagram_id: Mapped[str] = mapped_column(String(100), ForeignKey('instagram_accounts.instagram_id'), nullable=False)
    
    # Metrics at snapshot time
    followers_count: Mapped[int] = mapped_column(Integer, default=0)
    follows_count: Mapped[int] = mapped_column(Integer, default=0)
    media_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Growth metrics
    followers_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    follows_delta: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Daily insights
    impressions: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reach: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    profile_views: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    account: Mapped["InstagramAccount"] = relationship("InstagramAccount", back_populates="snapshots")
    
    __table_args__ = (
        Index('idx_ig_snapshot_date', 'instagram_id', 'snapshot_date'),
    )


# =============================================================================
# ML PREDICTION MODELS
# =============================================================================

class MLPrediction(Base):
    """Store ML model predictions for tracking and evaluation."""
    __tablename__ = 'ml_predictions'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Identification
    platform: Mapped[str] = mapped_column(String(20), nullable=False)  # youtube, instagram
    content_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # viral, engagement, sentiment, views
    
    # Prediction details
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    actual_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Filled later for evaluation
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Model metadata
    model_version: Mapped[str] = mapped_column(String(50), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    features_used: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Evaluation
    error: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # actual - predicted
    error_percentage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timing
    prediction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    evaluation_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # When the prediction is for
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_prediction_content_type', 'content_id', 'prediction_type'),
        Index('idx_prediction_date', 'prediction_date'),
    )


class ModelMetrics(Base):
    """Track ML model performance over time."""
    __tablename__ = 'model_metrics'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Performance metrics
    mae: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Mean Absolute Error
    mse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Mean Squared Error
    rmse: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Root Mean Squared Error
    mape: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Mean Absolute Percentage Error
    r2_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Classification metrics (for viral prediction)
    accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precision: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recall: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    f1_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Dataset info
    train_samples: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    test_samples: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_model_performance', 'model_name', 'evaluated_at'),
    )


# =============================================================================
# ANALYTICS CACHE
# =============================================================================

class AnalyticsCache(Base):
    """Cache computed analytics results for quick access."""
    __tablename__ = 'analytics_cache'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Cached data
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    # Time range for the cached data
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Cache management
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cache_expiry', 'expires_at'),
    )
