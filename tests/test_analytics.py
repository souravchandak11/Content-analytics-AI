"""
Analytics Tests
===============
Tests for analytics calculations and metrics.
"""

import pytest
from src.analytics import YouTubeMetrics, InstagramMetrics


class TestYouTubeMetrics:
    """Test YouTube analytics calculations"""
    
    def test_engagement_rate_calculation(self):
        """Test engagement rate formula"""
        rate = YouTubeMetrics.engagement_rate(
            views=10000,
            likes=500,
            comments=100
        )
        
        # (500 + 100) / 10000 = 0.06 = 6%
        expected = 0.06
        assert abs(rate - expected) < 0.001
        print(f"✓ Engagement rate: {rate:.4f} (expected {expected})")
    
    def test_engagement_rate_zero_views(self):
        """Test engagement rate with zero views"""
        rate = YouTubeMetrics.engagement_rate(views=0, likes=100, comments=10)
        assert rate == 0
        print("✓ Zero views handled correctly")
    
    def test_view_to_subscriber_ratio(self):
        """Test view to subscriber ratio"""
        ratio = YouTubeMetrics.view_to_subscriber_ratio(
            views=50000,
            subscribers=10000
        )
        
        expected = 5.0
        assert abs(ratio - expected) < 0.01
        print(f"✓ View/Sub ratio: {ratio:.2f} (expected {expected})")
    
    def test_channel_health_score(self):
        """Test channel health score calculation"""
        score = YouTubeMetrics.channel_health_score(
            subscriber_growth_rate=2.0,
            avg_engagement_rate=5.0,
            upload_frequency=2.0,
            avg_views_per_video=10000,
            subscribers=50000
        )
        
        # Score should be between 0-100
        assert 0 <= score <= 100
        print(f"✓ Channel health score: {score:.1f}/100")


class TestInstagramMetrics:
    """Test Instagram analytics calculations"""
    
    def test_engagement_rate(self):
        """Test Instagram engagement rate"""
        rate = InstagramMetrics.engagement_rate(
            likes=1000,
            comments=50,
            followers=10000
        )
        
        # (1000 + 50) / 10000 = 0.105 = 10.5%
        expected = 0.105
        assert abs(rate - expected) < 0.001
        print(f"✓ Instagram engagement: {rate:.4f} (expected {expected})")
    
    def test_engagement_rate_zero_followers(self):
        """Test engagement rate with zero followers"""
        rate = InstagramMetrics.engagement_rate(likes=100, comments=10, followers=0)
        assert rate == 0
        print("✓ Zero followers handled correctly")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
