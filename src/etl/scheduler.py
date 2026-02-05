"""
Content Analytics Platform - ETL Scheduler
==========================================
Scheduled data collection with background tasks.
"""

import os
import time
from datetime import datetime
from typing import List

import schedule
from loguru import logger
from dotenv import load_dotenv

from .pipeline import DataPipeline, run_collection
from src.database import get_db_session, check_database_connection
from src.database.models import YouTubeChannel, InstagramAccount

load_dotenv()


class DataScheduler:
    """
    Scheduler for automated data collection.
    """
    
    def __init__(self):
        """Initialize scheduler."""
        self.pipeline = DataPipeline()
        self.running = False
        self._load_tracked_accounts()
    
    def _load_tracked_accounts(self) -> None:
        """Load tracked accounts from database."""
        self.youtube_channels: List[str] = []
        self.instagram_accounts: List[str] = []
        
        try:
            with get_db_session() as session:
                channels = session.query(YouTubeChannel).filter_by(
                    is_active=True
                ).all()
                self.youtube_channels = [c.channel_id for c in channels]
                
                accounts = session.query(InstagramAccount).filter_by(
                    is_active=True
                ).all()
                self.instagram_accounts = [a.instagram_id for a in accounts]
        except Exception as e:
            logger.warning(f"Could not load tracked accounts: {e}")
    
    def add_youtube_channel(self, channel_id: str) -> bool:
        """Add a YouTube channel to track."""
        if channel_id not in self.youtube_channels:
            self.youtube_channels.append(channel_id)
            return True
        return False
    
    def add_instagram_account(self, instagram_id: str) -> bool:
        """Add an Instagram account to track."""
        if instagram_id not in self.instagram_accounts:
            self.instagram_accounts.append(instagram_id)
            return True
        return False
    
    def daily_collection(self) -> None:
        """Run daily data collection for all tracked accounts."""
        logger.info("=" * 60)
        logger.info(f"Starting scheduled collection at {datetime.now()}")
        logger.info("=" * 60)
        
        # Reload tracked accounts
        self._load_tracked_accounts()
        
        results = run_collection(
            youtube_channels=self.youtube_channels,
            instagram_accounts=self.instagram_accounts
        )
        
        # Log summary
        yt_videos = sum(r.get('videos_collected', 0) for r in results['youtube'])
        ig_posts = sum(r.get('posts_collected', 0) for r in results['instagram'])
        
        logger.info(f"Collection complete:")
        logger.info(f"  YouTube: {len(results['youtube'])} channels, {yt_videos} videos")
        logger.info(f"  Instagram: {len(results['instagram'])} accounts, {ig_posts} posts")
    
    def start(self, run_now: bool = True) -> None:
        """
        Start the scheduler.
        
        Args:
            run_now: Run collection immediately on start
        """
        # Check database connection
        if not check_database_connection():
            logger.error("Database connection failed. Cannot start scheduler.")
            return
        
        # Schedule daily collection
        collection_time = os.getenv('COLLECTION_TIME', '02:00')
        schedule.every().day.at(collection_time).do(self.daily_collection)
        
        logger.info(f"Scheduler started. Daily collection at {collection_time}")
        logger.info(f"Tracking {len(self.youtube_channels)} YouTube channels")
        logger.info(f"Tracking {len(self.instagram_accounts)} Instagram accounts")
        
        if run_now:
            logger.info("Running initial collection...")
            self.daily_collection()
        
        self.running = True
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        logger.info("Scheduler stopped")


def main():
    """Run the scheduler."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Content Analytics Data Scheduler')
    parser.add_argument('--no-initial', action='store_true', help='Skip initial collection')
    parser.add_argument('--add-channel', type=str, help='Add YouTube channel to track')
    parser.add_argument('--add-instagram', type=str, help='Add Instagram account to track')
    args = parser.parse_args()
    
    scheduler = DataScheduler()
    
    if args.add_channel:
        scheduler.add_youtube_channel(args.add_channel)
        logger.info(f"Added YouTube channel: {args.add_channel}")
    
    if args.add_instagram:
        scheduler.add_instagram_account(args.add_instagram)
        logger.info(f"Added Instagram account: {args.add_instagram}")
    
    try:
        scheduler.start(run_now=not args.no_initial)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.stop()


if __name__ == '__main__':
    main()
