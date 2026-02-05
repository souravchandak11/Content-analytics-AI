"""SQLAlchemy Models for Content Analytics Tool."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, BigInteger
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ============================================
# YouTube Models
# ============================================

class YouTubeChannel(Base):
    """YouTube Channel model."""
    
    __tablename__ = 'youtube_channels'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    snapshots = relationship("YouTubeChannelSnapshot", back_populates="channel", cascade="all, delete-orphan")
    videos = relationship("YouTubeVideo", back_populates="channel", cascade="all, delete-orphan")


class YouTubeChannelSnapshot(Base):
    """YouTube Channel Snapshot for tracking metrics over time."""
    
    __tablename__ = 'youtube_channel_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(50), ForeignKey('youtube_channels.channel_id'), nullable=False, index=True)
    subscriber_count = Column(BigInteger, default=0)
    video_count = Column(Integer, default=0)
    view_count = Column(BigInteger, default=0)
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    channel = relationship("YouTubeChannel", back_populates="snapshots")


class YouTubeVideo(Base):
    """YouTube Video model."""
    
    __tablename__ = 'youtube_videos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(50), unique=True, nullable=False, index=True)
    channel_id = Column(String(50), ForeignKey('youtube_channels.channel_id'), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    published_at = Column(DateTime, nullable=True)
    view_count = Column(BigInteger, default=0)
    like_count = Column(BigInteger, default=0)
    comment_count = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    channel = relationship("YouTubeChannel", back_populates="videos")
    comments = relationship("YouTubeComment", back_populates="video", cascade="all, delete-orphan")


class YouTubeComment(Base):
    """YouTube Comment model."""
    
    __tablename__ = 'youtube_comments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_id = Column(String(100), unique=True, nullable=False, index=True)
    video_id = Column(String(50), ForeignKey('youtube_videos.video_id'), nullable=False, index=True)
    author = Column(String(255), nullable=True)
    text = Column(Text, nullable=True)
    like_count = Column(Integer, default=0)
    sentiment_score = Column(Float, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    video = relationship("YouTubeVideo", back_populates="comments")


# ============================================
# Instagram Models
# ============================================

class InstagramAccount(Base):
    """Instagram Account model."""
    
    __tablename__ = 'instagram_accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    name = Column(String(255), nullable=True)
    biography = Column(Text, nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    snapshots = relationship("InstagramAccountSnapshot", back_populates="account", cascade="all, delete-orphan")
    posts = relationship("InstagramPost", back_populates="account", cascade="all, delete-orphan")


class InstagramAccountSnapshot(Base):
    """Instagram Account Snapshot for tracking metrics over time."""
    
    __tablename__ = 'instagram_account_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String(50), ForeignKey('instagram_accounts.account_id'), nullable=False, index=True)
    followers_count = Column(BigInteger, default=0)
    follows_count = Column(Integer, default=0)
    media_count = Column(Integer, default=0)
    snapshot_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    account = relationship("InstagramAccount", back_populates="snapshots")


class InstagramPost(Base):
    """Instagram Post model."""
    
    __tablename__ = 'instagram_posts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(50), unique=True, nullable=False, index=True)
    account_id = Column(String(50), ForeignKey('instagram_accounts.account_id'), nullable=False, index=True)
    caption = Column(Text, nullable=True)
    media_type = Column(String(20), nullable=True)
    media_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    permalink = Column(String(500), nullable=True)
    like_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("InstagramAccount", back_populates="posts")
