"""Sync Service for orchestrating API data fetching and DB persistence."""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from src.api.youtube_client import YouTubeClient
from src.api.instagram_client import InstagramClient
from src.database.queries import YouTubeQueries, InstagramQueries
from src.analytics.metrics import SentimentAnalyzer

logger = logging.getLogger(__name__)

class SyncService:
    """Service to handle synchronization between social media APIs and local database."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.yt_queries = YouTubeQueries(db_session)
        self.ig_queries = InstagramQueries(db_session)
        self.yt_client = YouTubeClient()
        self.ig_client = InstagramClient()
        self.sentiment_analyzer = SentimentAnalyzer()

    def sync_youtube_channel(self, channel_id: str) -> bool:
        """Fetch and save YouTube channel data, videos, and comments."""
        logger.info(f"Syncing YouTube channel: {channel_id}")
        
        # 1. Sync Channel Stats
        channel_data = self.yt_client.get_channel_stats(channel_id)
        if not channel_data:
            logger.error(f"Failed to fetch channel stats for {channel_id}")
            return False
        
        self.yt_queries.save_channel(channel_data)
        
        # 2. Sync Recent Videos
        videos = self.yt_client.get_videos(channel_id, max_results=20)
        for video in videos:
            self.yt_queries.save_video(video)
            
            # 3. Sync Comments for each video
            comments = self.yt_client.get_comments(video['video_id'], max_results=50)
            for comment in comments:
                sentiment = self.sentiment_analyzer.analyze(comment['text'])
                self.yt_queries.save_comment(comment, sentiment_score=sentiment)
        
        return True

    def sync_instagram_account(self, user_id: str = "me") -> bool:
        """Fetch and save Instagram account info and media."""
        logger.info(f"Syncing Instagram account: {user_id}")
        
        # 1. Sync Account Info
        account_data = self.ig_client.get_account_info(user_id)
        if not account_data:
            logger.error(f"Failed to fetch Instagram account info for {user_id}")
            return False
        
        self.ig_queries.save_account(account_data)
        account_id = account_data['account_id']
        
        # 2. Sync Recent Posts
        media_posts = self.ig_client.get_media(user_id, max_results=20)
        for post in media_posts:
            self.ig_queries.save_post(post, account_id=account_id)
            
        return True

    def sync_all(self, yt_channel_id: Optional[str] = None, ig_user_id: str = "me") -> Dict[str, bool]:
        """Perform a full sync for both platforms if possible."""
        results = {"youtube": False, "instagram": False}
        
        if yt_channel_id:
            results["youtube"] = self.sync_youtube_channel(yt_channel_id)
            
        if self.ig_client._is_valid:
            results["instagram"] = self.sync_instagram_account(ig_user_id)
            
        return results
