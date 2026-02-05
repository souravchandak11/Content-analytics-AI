"""
Content Analytics Platform - Instagram Graph API Client
=======================================================
Production-ready Instagram API client with rate limiting.
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests
from dotenv import load_dotenv
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from src.utils.mock_data import generate_mock_instagram_data

load_dotenv()


class InstagramAPIError(Exception):
    """Instagram API error."""
    pass


class RateLimitError(Exception):
    """Rate limit exceeded."""
    pass


class InstagramClient:
    """
    Instagram Graph API Client.
    
    Requires:
    - Instagram Business or Creator Account
    - Facebook App with Instagram Graph API enabled
    - Access token with required permissions
    """
    
    BASE_URL = 'https://graph.instagram.com'
    GRAPH_URL = 'https://graph.facebook.com/v18.0'
    
    def __init__(self, access_token: str = None):
        """
        Initialize Instagram client.
        
        Args:
            access_token: Instagram access token
        """
        self.access_token = access_token or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.use_mock = os.getenv('USE_MOCK_DATA', 'False').lower() == 'true'
        
        if not self.use_mock and not self.access_token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN not configured")
        
        self._session = requests.Session()
        self._last_request = 0
        self._min_interval = 0.5  # 500ms between requests
        self._rate_limit = int(os.getenv('INSTAGRAM_RATE_LIMIT', 200))
        self._requests_made = 0
    
    def _throttle(self) -> None:
        """Rate limit requests."""
        elapsed = time.time() - self._last_request
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request = time.time()
        self._requests_made += 1
        
        if self._requests_made >= self._rate_limit:
            logger.warning("Approaching rate limit")
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Dict = None,
        use_graph: bool = False
    ) -> Dict:
        """Make API request with error handling."""
        self._throttle()
        
        base = self.GRAPH_URL if use_graph else self.BASE_URL
        url = f"{base}/{endpoint}"
        
        request_params = params or {}
        request_params['access_token'] = self.access_token
        
        try:
            response = self._session.get(url, params=request_params, timeout=30)
            data = response.json()
            
            if 'error' in data:
                error = data['error']
                code = error.get('code', 0)
                
                if code == 4 or code == 17:  # Rate limit
                    raise RateLimitError(error.get('message', 'Rate limited'))
                
                raise InstagramAPIError(
                    f"API Error {code}: {error.get('message', 'Unknown error')}"
                )
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise InstagramAPIError(f"Request failed: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def get_user_profile(self, user_id: str = 'me') -> Optional[Dict[str, Any]]:
        """
        Get Instagram user profile.
        
        Args:
            user_id: Instagram user ID or 'me'
            
        Returns:
            User profile data
        """
        fields = [
            'id', 'username', 'name', 'account_type',
            'media_count', 'followers_count', 'follows_count',
            'biography', 'website', 'profile_picture_url'
        ]
        
        try:
            data = self._make_request(
                user_id,
                params={'fields': ','.join(fields)}
            )
            
            return {
                'instagram_id': data.get('id'),
                'username': data.get('username'),
                'name': data.get('name'),
                'account_type': data.get('account_type'),
                'media_count': data.get('media_count', 0),
                'followers_count': data.get('followers_count', 0),
                'follows_count': data.get('follows_count', 0),
                'biography': data.get('biography'),
                'website': data.get('website'),
                'profile_picture_url': data.get('profile_picture_url'),
                'last_synced': datetime.utcnow()
            }
            
        except InstagramAPIError as e:
            logger.error(f"Failed to get profile: {e}")
            return None
    
    def get_user_media(
        self, 
        user_id: str = 'me', 
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Get user's media posts.
        
        Args:
            user_id: Instagram user ID
            limit: Maximum posts to retrieve
            
        Returns:
            List of media posts
        """
        if self.use_mock:
            logger.info(f"Returning mock data for user {user_id}")
            return generate_mock_instagram_data(limit)

        fields = [
            'id', 'caption', 'media_type', 'media_url',
            'permalink', 'thumbnail_url', 'timestamp',
            'like_count', 'comments_count'
        ]
        
        posts = []
        after = None
        
        while len(posts) < limit:
            params = {
                'fields': ','.join(fields),
                'limit': min(25, limit - len(posts))
            }
            if after:
                params['after'] = after
            
            try:
                data = self._make_request(f"{user_id}/media", params=params)
                
                for item in data.get('data', []):
                    posts.append({
                        'post_id': item.get('id'),
                        'caption': item.get('caption', ''),
                        'media_type': item.get('media_type'),
                        'media_url': item.get('media_url'),
                        'permalink': item.get('permalink'),
                        'thumbnail_url': item.get('thumbnail_url'),
                        'timestamp': self._parse_timestamp(item.get('timestamp')),
                        'like_count': item.get('like_count', 0),
                        'comments_count': item.get('comments_count', 0),
                        'hashtags': self._extract_hashtags(item.get('caption', '')),
                        'mentions': self._extract_mentions(item.get('caption', ''))
                    })
                
                paging = data.get('paging', {})
                after = paging.get('cursors', {}).get('after')
                
                if not after or not data.get('data'):
                    break
                    
            except InstagramAPIError as e:
                logger.error(f"Failed to get media: {e}")
                break
        
        return posts
    
    def get_media_insights(self, media_id: str) -> Dict[str, Any]:
        """
        Get insights for a media post.
        
        Args:
            media_id: Instagram media ID
            
        Returns:
            Media insights dictionary
        """
        # Metrics vary by media type
        metrics = 'engagement,impressions,reach,saved'
        
        try:
            data = self._make_request(
                f"{media_id}/insights",
                params={'metric': metrics}
            )
            
            insights = {}
            for item in data.get('data', []):
                name = item.get('name')
                values = item.get('values', [])
                if values:
                    insights[name] = values[0].get('value', 0)
            
            return insights
            
        except InstagramAPIError as e:
            logger.error(f"Failed to get insights for {media_id}: {e}")
            return {}
    
    def get_account_insights(
        self, 
        user_id: str = 'me',
        period: str = 'day',
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get account-level insights.
        
        Args:
            user_id: Instagram user ID
            period: Time period (day, week, days_28)
            metrics: List of metrics
            
        Returns:
            Account insights dictionary
        """
        if metrics is None:
            metrics = ['impressions', 'reach', 'follower_count', 'profile_views']
        
        try:
            data = self._make_request(
                f"{user_id}/insights",
                params={
                    'metric': ','.join(metrics),
                    'period': period
                }
            )
            
            insights = {}
            for item in data.get('data', []):
                name = item.get('name')
                insights[name] = item.get('values', [])
            
            return insights
            
        except InstagramAPIError as e:
            logger.error(f"Failed to get account insights: {e}")
            return {}
    
    def _parse_timestamp(self, ts: str) -> Optional[datetime]:
        """Parse Instagram timestamp."""
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        import re
        return re.findall(r'#(\w+)', text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text."""
        if not text:
            return []
        import re
        return re.findall(r'@(\w+)', text)
