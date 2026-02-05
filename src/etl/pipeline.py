"""
Content Analytics Platform - ETL Pipeline
==========================================
Data extraction, transformation, and loading pipeline.
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from loguru import logger

from src.api import YouTubeClient, InstagramClient, QuotaExceededError
from src.database import get_db_session
from src.database.queries import YouTubeRepository, InstagramRepository
from src.analytics.metrics import YouTubeMetrics, InstagramMetrics


class DataPipeline:
    """
    Main ETL pipeline for collecting social media data.
    """
    
    def __init__(self):
        """Initialize pipeline with API clients."""
        try:
            self.youtube = YouTubeClient()
        except ValueError:
            logger.warning("YouTube API not configured")
            self.youtube = None
        
        try:
            self.instagram = InstagramClient()
        except ValueError:
            logger.warning("Instagram API not configured")
            self.instagram = None
    
    def collect_youtube_channel(
        self, 
        channel_id: str,
        max_videos: int = 50,
        collect_comments: bool = True,
        max_comments_per_video: int = 100
    ) -> Dict[str, Any]:
        """
        Collect complete YouTube channel data.
        
        Args:
            channel_id: YouTube channel ID
            max_videos: Maximum videos to collect
            collect_comments: Whether to collect comments
            max_comments_per_video: Max comments per video
            
        Returns:
            Collection statistics
        """
        if not self.youtube:
            return {'error': 'YouTube API not configured'}
        
        logger.info(f"Starting YouTube collection for channel: {channel_id}")
        stats = {
            'channel_id': channel_id,
            'start_time': datetime.utcnow().isoformat(),
            'videos_collected': 0,
            'comments_collected': 0,
            'errors': []
        }
        
        try:
            # Get channel data
            channel_data = self.youtube.get_channel_stats(channel_id)
            if not channel_data:
                stats['errors'].append('Channel not found')
                return stats
            
            # Save channel to database
            with get_db_session() as session:
                channel = YouTubeRepository.upsert_channel(session, channel_data)
                
                # Create snapshot
                YouTubeRepository.create_channel_snapshot(
                    session,
                    channel_id=channel_id,
                    subscribers=channel_data['subscribers'],
                    total_views=channel_data['total_views'],
                    total_videos=channel_data['total_videos']
                )
                
                stats['channel_title'] = channel_data['title']
                stats['subscribers'] = channel_data['subscribers']
            
            logger.info(f"Channel saved: {channel_data['title']}")
            
            # Get videos
            videos = self.youtube.get_channel_videos(channel_id, max_results=max_videos)
            logger.info(f"Found {len(videos)} videos")
            
            for video in videos:
                try:
                    with get_db_session() as session:
                        # Calculate engagement metrics
                        video['engagement_rate'] = YouTubeMetrics.engagement_rate(
                            video['views'], video['likes'], video['comments']
                        )
                        video['like_rate'] = YouTubeMetrics.like_rate(
                            video['views'], video['likes']
                        )
                        video['comment_rate'] = YouTubeMetrics.comment_rate(
                            video['views'], video['comments']
                        )
                        
                        # Save video
                        YouTubeRepository.upsert_video(session, video)
                        
                        # Create snapshot
                        YouTubeRepository.create_video_snapshot(
                            session,
                            video_id=video['video_id'],
                            views=video['views'],
                            likes=video['likes'],
                            comments=video['comments']
                        )
                        
                        stats['videos_collected'] += 1
                    
                    # Collect comments for popular videos
                    if collect_comments and video['views'] > 1000:
                        comments = self._collect_video_comments(
                            video['video_id'], 
                            max_comments_per_video
                        )
                        stats['comments_collected'] += len(comments)
                    
                    # Rate limiting
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing video {video['video_id']}: {e}")
                    stats['errors'].append(str(e))
            
            stats['quota_used'] = self.youtube.quota_used
            stats['quota_remaining'] = self.youtube.quota_remaining()
            
        except QuotaExceededError as e:
            logger.error(f"Quota exceeded: {e}")
            stats['errors'].append('Quota exceeded')
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            stats['errors'].append(str(e))
        
        stats['end_time'] = datetime.utcnow().isoformat()
        logger.info(f"Collection complete: {stats['videos_collected']} videos")
        
        return stats
    
    def _collect_video_comments(
        self, 
        video_id: str, 
        max_comments: int
    ) -> List[Dict]:
        """Collect and save video comments."""
        from src.database.models import YouTubeComment
        
        comments = self.youtube.get_video_comments(video_id, max_comments)
        
        with get_db_session() as session:
            for comment_data in comments:
                existing = session.query(YouTubeComment).filter_by(
                    comment_id=comment_data['comment_id']
                ).first()
                
                if not existing:
                    comment = YouTubeComment(**comment_data)
                    session.add(comment)
            
            session.flush()
        
        return comments
    
    def collect_instagram_account(
        self, 
        user_id: str = 'me',
        max_posts: int = 50,
        collect_insights: bool = True
    ) -> Dict[str, Any]:
        """
        Collect Instagram account data.
        
        Args:
            user_id: Instagram user ID or 'me'
            max_posts: Maximum posts to collect
            collect_insights: Whether to collect post insights
            
        Returns:
            Collection statistics
        """
        if not self.instagram:
            return {'error': 'Instagram API not configured'}
        
        logger.info(f"Starting Instagram collection for: {user_id}")
        stats = {
            'user_id': user_id,
            'start_time': datetime.utcnow().isoformat(),
            'posts_collected': 0,
            'errors': []
        }
        
        try:
            # Get profile
            profile = self.instagram.get_user_profile(user_id)
            if not profile:
                stats['errors'].append('Profile not found')
                return stats
            
            # Save account
            with get_db_session() as session:
                InstagramRepository.upsert_account(session, profile)
                
                InstagramRepository.create_account_snapshot(
                    session,
                    instagram_id=profile['instagram_id'],
                    followers=profile['followers_count'],
                    follows=profile['follows_count'],
                    media_count=profile['media_count']
                )
            
            stats['username'] = profile['username']
            stats['followers'] = profile['followers_count']
            
            logger.info(f"Account saved: {profile['username']}")
            
            # Get posts
            posts = self.instagram.get_user_media(user_id, limit=max_posts)
            logger.info(f"Found {len(posts)} posts")
            
            for post in posts:
                try:
                    # Get insights if available
                    if collect_insights:
                        insights = self.instagram.get_media_insights(post['post_id'])
                        post.update({
                            'engagement': insights.get('engagement'),
                            'impressions': insights.get('impressions'),
                            'reach': insights.get('reach'),
                            'saved': insights.get('saved')
                        })
                    
                    # Calculate engagement rate
                    post['instagram_id'] = profile['instagram_id']
                    post['engagement_rate'] = InstagramMetrics.engagement_rate(
                        post['like_count'],
                        post['comments_count'],
                        profile['followers_count']
                    )
                    
                    with get_db_session() as session:
                        InstagramRepository.upsert_post(session, post)
                    
                    stats['posts_collected'] += 1
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error processing post {post['post_id']}: {e}")
                    stats['errors'].append(str(e))
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            stats['errors'].append(str(e))
        
        stats['end_time'] = datetime.utcnow().isoformat()
        logger.info(f"Collection complete: {stats['posts_collected']} posts")
        
        return stats


def run_collection(
    youtube_channels: List[str] = None,
    instagram_accounts: List[str] = None
) -> Dict[str, Any]:
    """
    Run data collection for multiple accounts.
    
    Args:
        youtube_channels: List of YouTube channel IDs
        instagram_accounts: List of Instagram user IDs
        
    Returns:
        Collection results
    """
    pipeline = DataPipeline()
    results = {
        'start_time': datetime.utcnow().isoformat(),
        'youtube': [],
        'instagram': []
    }
    
    if youtube_channels:
        for channel_id in youtube_channels:
            result = pipeline.collect_youtube_channel(channel_id)
            results['youtube'].append(result)
            time.sleep(5)  # Pause between channels
    
    if instagram_accounts:
        for user_id in instagram_accounts:
            result = pipeline.collect_instagram_account(user_id)
            results['instagram'].append(result)
            time.sleep(5)
    
    results['end_time'] = datetime.utcnow().isoformat()
    return results
