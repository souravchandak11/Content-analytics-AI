"""
Content Analytics Platform - YouTube Data API v3 Client
=======================================================
Production-ready YouTube API client with quota management and error handling.
"""

import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from dotenv import load_dotenv
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.utils.mock_data import generate_mock_youtube_data

load_dotenv()


class QuotaExceededError(Exception):
    """Raised when YouTube API quota is exceeded."""
    pass


class YouTubeClient:
    """
    YouTube Data API v3 Client with quota management.
    
    Quota costs (approximate):
    - channels.list: 1 unit
    - videos.list: 1 unit
    - playlistItems.list: 1 unit
    - commentThreads.list: 1 unit
    - search.list: 100 units (expensive!)
    
    Free tier: 10,000 units/day
    """
    
    # API quota costs
    QUOTA_COSTS = {
        'channels.list': 1,
        'videos.list': 1,
        'playlistItems.list': 1,
        'commentThreads.list': 1,
        'search.list': 100,
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize YouTube client.
        
        Args:
            api_key: YouTube API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.use_mock = os.getenv('USE_MOCK_DATA', 'False').lower() == 'true'
        
        if not self.use_mock and not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not configured")
        
        self._youtube: Resource = None
        self.quota_used = 0
        self.daily_quota = int(os.getenv('YOUTUBE_DAILY_QUOTA', 10000))
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms between requests
    
    @property
    def youtube(self) -> Resource:
        """Lazy-load YouTube API resource."""
        if self._youtube is None:
            self._youtube = build('youtube', 'v3', developerKey=self.api_key)
        return self._youtube
    
    def _throttle(self) -> None:
        """Rate limit requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_request_interval:
            time.sleep(self._min_request_interval - elapsed)
        self._last_request_time = time.time()
    
    def _track_quota(self, operation: str, count: int = 1) -> None:
        """Track quota usage."""
        cost = self.QUOTA_COSTS.get(operation, 1) * count
        self.quota_used += cost
        if self.quota_used >= self.daily_quota:
            raise QuotaExceededError(f"Daily quota exceeded: {self.quota_used}/{self.daily_quota}")
        logger.debug(f"Quota: {operation} cost {cost}, total: {self.quota_used}/{self.daily_quota}")
    
    def quota_remaining(self) -> int:
        """Get remaining quota."""
        return max(0, self.daily_quota - self.quota_used)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(HttpError)
    )
    def get_channel_stats(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """
        Get channel statistics and metadata.
        
        Args:
            channel_id: YouTube channel ID (starts with UC)
            
        Returns:
            Channel data dictionary or None
        """
        self._throttle()
        
        try:
            response = self.youtube.channels().list(
                part='statistics,snippet,contentDetails,brandingSettings',
                id=channel_id
            ).execute()
            
            self._track_quota('channels.list')
            
            if not response.get('items'):
                logger.warning(f"Channel not found: {channel_id}")
                return None
            
            channel = response['items'][0]
            snippet = channel.get('snippet', {})
            stats = channel.get('statistics', {})
            content = channel.get('contentDetails', {})
            branding = channel.get('brandingSettings', {}).get('channel', {})
            
            return {
                'channel_id': channel_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'custom_url': snippet.get('customUrl', ''),
                'published_at': self._parse_datetime(snippet.get('publishedAt')),
                'country': snippet.get('country'),
                'subscribers': int(stats.get('subscriberCount', 0)),
                'total_views': int(stats.get('viewCount', 0)),
                'total_videos': int(stats.get('videoCount', 0)),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'banner_url': branding.get('bannerExternalUrl'),
                'keywords': branding.get('keywords', '').split() if branding.get('keywords') else [],
                'uploads_playlist': content.get('relatedPlaylists', {}).get('uploads'),
                'last_synced': datetime.utcnow()
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                logger.error(f"Quota exceeded or forbidden: {e}")
                raise QuotaExceededError(str(e))
            logger.error(f"YouTube API error for channel {channel_id}: {e}")
            raise
    
    def get_channel_videos(
        self, 
        channel_id: str, 
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get videos from a channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum videos to retrieve
            
        Returns:
            List of video dictionaries
        """
        if self.use_mock:
            logger.info(f"Returning mock data for channel {channel_id}")
            return generate_mock_youtube_data(max_results)

        # First get uploads playlist ID
        channel_data = self.get_channel_stats(channel_id)
        if not channel_data or not channel_data.get('uploads_playlist'):
            return []
        
        uploads_id = channel_data['uploads_playlist']
        video_ids = []
        next_page = None
        
        # Get video IDs from playlist
        while len(video_ids) < max_results:
            self._throttle()
            
            try:
                response = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=uploads_id,
                    maxResults=min(50, max_results - len(video_ids)),
                    pageToken=next_page
                ).execute()
                
                self._track_quota('playlistItems.list')
                
                for item in response.get('items', []):
                    video_ids.append(item['contentDetails']['videoId'])
                
                next_page = response.get('nextPageToken')
                if not next_page:
                    break
                    
            except HttpError as e:
                logger.error(f"Error fetching playlist: {e}")
                break
        
        # Get detailed video info in batches
        videos = []
        for i in range(0, len(video_ids), 50):
            batch = video_ids[i:i+50]
            batch_videos = self.get_videos_by_ids(batch)
            videos.extend(batch_videos)
        
        return videos
    
    def get_videos_by_ids(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get video details by IDs.
        
        Args:
            video_ids: List of video IDs
            
        Returns:
            List of video dictionaries
        """
        if not video_ids:
            return []
        
        self._throttle()
        
        try:
            response = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids[:50])
            ).execute()
            
            self._track_quota('videos.list')
            
            videos = []
            for video in response.get('items', []):
                snippet = video.get('snippet', {})
                stats = video.get('statistics', {})
                content = video.get('contentDetails', {})
                
                videos.append({
                    'video_id': video['id'],
                    'channel_id': snippet.get('channelId', ''),
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'published_at': self._parse_datetime(snippet.get('publishedAt')),
                    'duration': content.get('duration', ''),
                    'duration_seconds': self._parse_duration(content.get('duration', '')),
                    'category_id': snippet.get('categoryId'),
                    'tags': snippet.get('tags', []),
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'comments': int(stats.get('commentCount', 0)),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                    'privacy_status': video.get('status', {}).get('privacyStatus'),
                    'made_for_kids': video.get('status', {}).get('madeForKids'),
                    'default_language': snippet.get('defaultLanguage'),
                    'last_synced': datetime.utcnow()
                })
            
            return videos
            
        except HttpError as e:
            logger.error(f"Error fetching videos: {e}")
            return []
    
    def get_video_comments(
        self, 
        video_id: str, 
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get comments for a video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum comments to retrieve
            
        Returns:
            List of comment dictionaries
        """
        comments = []
        next_page = None
        
        while len(comments) < max_results:
            self._throttle()
            
            try:
                response = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=next_page,
                    textFormat='plainText',
                    order='relevance'
                ).execute()
                
                self._track_quota('commentThreads.list')
                
                for item in response.get('items', []):
                    snippet = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'comment_id': item['id'],
                        'video_id': video_id,
                        'text': snippet.get('textDisplay', ''),
                        'author': snippet.get('authorDisplayName', ''),
                        'author_channel_id': snippet.get('authorChannelId', {}).get('value'),
                        'likes': snippet.get('likeCount', 0),
                        'reply_count': item['snippet'].get('totalReplyCount', 0),
                        'published_at': self._parse_datetime(snippet.get('publishedAt'))
                    })
                
                next_page = response.get('nextPageToken')
                if not next_page:
                    break
                    
            except HttpError as e:
                if 'commentsDisabled' in str(e):
                    logger.info(f"Comments disabled for video: {video_id}")
                else:
                    logger.error(f"Error fetching comments: {e}")
                break
        
        return comments
    
    def search_channels(
        self, 
        query: str, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for channels (expensive - costs 100 units).
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of channel info dictionaries
        """
        self._throttle()
        
        try:
            response = self.youtube.search().list(
                part='snippet',
                q=query,
                type='channel',
                maxResults=max_results
            ).execute()
            
            self._track_quota('search.list')
            
            channels = []
            for item in response.get('items', []):
                snippet = item['snippet']
                channels.append({
                    'channel_id': item['id']['channelId'],
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url')
                })
            
            return channels
            
        except HttpError as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _parse_datetime(self, dt_str: str) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        if not duration:
            return 0
        
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
