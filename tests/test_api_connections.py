"""
API Connection Tests
====================
Tests for YouTube and Instagram API connections.
"""

import pytest
import os
from dotenv import load_dotenv

load_dotenv()


class TestAPIConnections:
    """Test API connection functionality"""
    
    def test_youtube_connection(self):
        """Test YouTube API connection or mock mode"""
        from src.api import YouTubeClient
        
        client = YouTubeClient()
        
        # Either mock mode is enabled or we have an API key
        if client.use_mock:
            # Mock mode - should return mock data
            data = client.get_channel_videos("test_channel_id", max_results=5)
            assert data is not None
            assert len(data) > 0
            print("✓ YouTube API: Running in MOCK mode")
        else:
            # Real API - should have valid key
            assert client.api_key is not None
            print("✓ YouTube API: Connected with real API key")
    
    def test_instagram_connection(self):
        """Test Instagram API connection or mock mode"""
        from src.api import InstagramClient
        
        client = InstagramClient()
        
        # Either mock mode is enabled or we have an access token
        if client.use_mock:
            # Mock mode - should return mock data
            data = client.get_user_media("test_user_id", limit=5)
            assert data is not None
            assert len(data) > 0
            print("✓ Instagram API: Running in MOCK mode")
        else:
            # Real API - should have valid token
            assert client.access_token is not None
            print("✓ Instagram API: Connected with real access token")
    
    def test_youtube_mock_data_structure(self):
        """Verify mock YouTube data has correct structure"""
        from src.utils.mock_data import generate_mock_youtube_data
        
        data = generate_mock_youtube_data(count=3)
        
        assert len(data) == 3
        
        required_fields = ['video_id', 'title', 'views', 'likes', 'comments']
        for item in data:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
        
        print("✓ Mock YouTube data structure is valid")
    
    def test_instagram_mock_data_structure(self):
        """Verify mock Instagram data has correct structure"""
        from src.utils.mock_data import generate_mock_instagram_data
        
        data = generate_mock_instagram_data(count=3)
        
        assert len(data) == 3
        
        required_fields = ['id', 'caption', 'like_count', 'comments_count', 'media_type']
        for item in data:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
        
        print("✓ Mock Instagram data structure is valid")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
