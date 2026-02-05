"""Instagram Graph API Client for Content Analytics Tool."""

import os
from typing import List, Dict, Optional, Any
import requests
from dotenv import load_dotenv

load_dotenv()


class InstagramClient:
    """Client for interacting with Instagram Graph API."""
    
    BASE_URL = "https://graph.instagram.com"
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize the Instagram API client.
        
        Args:
            access_token: Instagram Graph API access token. 
                         If not provided, reads from environment.
        """
        self.access_token = access_token or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self._is_valid = self.access_token and self.access_token != '[PLACEHOLDER]'
    
    def _check_client(self) -> bool:
        """Check if the client is properly initialized."""
        return self._is_valid
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to the Instagram Graph API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response JSON or None if error
        """
        if not self._check_client():
            return None
            
        params = params or {}
        params['access_token'] = self.access_token
        
        try:
            response = requests.get(f"{self.BASE_URL}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Instagram API Error: {e}")
            return None
    
    def get_account_info(self, user_id: str = "me") -> Optional[Dict[str, Any]]:
        """Get Instagram account information.
        
        Args:
            user_id: Instagram user ID or 'me' for authenticated user
            
        Returns:
            Dictionary containing account information or None if error
        """
        if not self._check_client():
            return None
            
        fields = "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url"
        data = self._make_request(user_id, {"fields": fields})
        
        if not data:
            return None
        
        return {
            'account_id': data.get('id'),
            'username': data.get('username'),
            'name': data.get('name', ''),
            'biography': data.get('biography', ''),
            'followers_count': data.get('followers_count', 0),
            'follows_count': data.get('follows_count', 0),
            'media_count': data.get('media_count', 0),
            'profile_picture_url': data.get('profile_picture_url', '')
        }
    
    def get_media(self, user_id: str = "me", max_results: int = 25) -> List[Dict[str, Any]]:
        """Get media posts from an Instagram account.
        
        Args:
            user_id: Instagram user ID or 'me' for authenticated user
            max_results: Maximum number of posts to retrieve
            
        Returns:
            List of media post dictionaries
        """
        if not self._check_client():
            return []
            
        fields = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count"
        data = self._make_request(f"{user_id}/media", {
            "fields": fields,
            "limit": min(max_results, 100)
        })
        
        if not data or 'data' not in data:
            return []
        
        posts = []
        for item in data['data'][:max_results]:
            posts.append({
                'post_id': item.get('id'),
                'caption': item.get('caption', ''),
                'media_type': item.get('media_type'),
                'media_url': item.get('media_url', ''),
                'thumbnail_url': item.get('thumbnail_url', item.get('media_url', '')),
                'permalink': item.get('permalink', ''),
                'timestamp': item.get('timestamp'),
                'like_count': item.get('like_count', 0),
                'comments_count': item.get('comments_count', 0)
            })
        
        return posts
    
    def get_media_insights(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get insights for a specific media post.
        
        Args:
            media_id: Instagram media ID
            
        Returns:
            Dictionary with engagement metrics or None if error
        """
        if not self._check_client():
            return None
            
        # Insights metrics depend on media type
        metrics = "engagement,impressions,reach,saved"
        data = self._make_request(f"{media_id}/insights", {"metric": metrics})
        
        if not data or 'data' not in data:
            return None
        
        insights = {}
        for metric in data.get('data', []):
            insights[metric['name']] = metric['values'][0]['value']
        
        return insights
    
    def get_account_insights(self, user_id: str = "me", period: str = "day") -> Optional[Dict[str, Any]]:
        """Get account-level insights.
        
        Args:
            user_id: Instagram user ID or 'me' for authenticated user
            period: Time period ('day', 'week', 'days_28', 'lifetime')
            
        Returns:
            Dictionary with account metrics or None if error
        """
        if not self._check_client():
            return None
            
        metrics = "impressions,reach,profile_views,website_clicks"
        data = self._make_request(f"{user_id}/insights", {
            "metric": metrics,
            "period": period
        })
        
        if not data or 'data' not in data:
            return None
        
        insights = {}
        for metric in data.get('data', []):
            insights[metric['name']] = metric['values'][0]['value']
        
        return insights
