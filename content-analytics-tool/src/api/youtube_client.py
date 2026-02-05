"""YouTube Data API Client for Content Analytics Tool."""

import os
from typing import List, Dict, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()


class YouTubeClient:
    """Client for interacting with YouTube Data API v3."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the YouTube API client.
        
        Args:
            api_key: YouTube Data API key. If not provided, reads from environment.
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        if not self.api_key or self.api_key == '[PLACEHOLDER]':
            self.youtube = None
        else:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def _check_client(self) -> bool:
        """Check if the client is properly initialized."""
        return self.youtube is not None
    
    def get_channel_stats(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel statistics.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Dictionary containing channel statistics or None if error
        """
        if not self._check_client():
            return None
            
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics,contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            channel = response['items'][0]
            return {
                'channel_id': channel_id,
                'title': channel['snippet']['title'],
                'description': channel['snippet'].get('description', ''),
                'thumbnail_url': channel['snippet']['thumbnails']['default']['url'],
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'view_count': int(channel['statistics'].get('viewCount', 0)),
                'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
            }
        except HttpError as e:
            print(f"YouTube API Error: {e}")
            return None
    
    def get_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get videos from a channel.
        
        Args:
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to retrieve
            
        Returns:
            List of video dictionaries
        """
        if not self._check_client():
            return []
            
        try:
            # First get the uploads playlist ID
            channel_stats = self.get_channel_stats(channel_id)
            if not channel_stats:
                return []
            
            playlist_id = channel_stats['uploads_playlist_id']
            
            videos = []
            next_page_token = None
            
            while len(videos) < max_results:
                request = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(videos)),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    video_id = item['contentDetails']['videoId']
                    video_stats = self.get_video_stats(video_id)
                    
                    videos.append({
                        'video_id': video_id,
                        'channel_id': channel_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet'].get('description', ''),
                        'thumbnail_url': item['snippet']['thumbnails']['default']['url'],
                        'published_at': item['snippet']['publishedAt'],
                        **video_stats
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos[:max_results]
        except HttpError as e:
            print(f"YouTube API Error: {e}")
            return []
    
    def get_video_stats(self, video_id: str) -> Dict[str, int]:
        """Get statistics for a specific video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with view_count, like_count, comment_count
        """
        if not self._check_client():
            return {'view_count': 0, 'like_count': 0, 'comment_count': 0}
            
        try:
            request = self.youtube.videos().list(
                part='statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return {'view_count': 0, 'like_count': 0, 'comment_count': 0}
            
            stats = response['items'][0]['statistics']
            return {
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0))
            }
        except HttpError as e:
            print(f"YouTube API Error: {e}")
            return {'view_count': 0, 'like_count': 0, 'comment_count': 0}
    
    def get_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get comments for a video.
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to retrieve
            
        Returns:
            List of comment dictionaries
        """
        if not self._check_client():
            return []
            
        try:
            comments = []
            next_page_token = None
            
            while len(comments) < max_results:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=next_page_token,
                    textFormat='plainText'
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'comment_id': item['id'],
                        'video_id': video_id,
                        'author': comment['authorDisplayName'],
                        'text': comment['textDisplay'],
                        'like_count': comment.get('likeCount', 0),
                        'published_at': comment['publishedAt']
                    })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return comments[:max_results]
        except HttpError as e:
            print(f"YouTube API Error (comments may be disabled): {e}")
            return []
