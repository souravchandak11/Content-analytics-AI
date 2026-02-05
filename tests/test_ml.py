"""
Content Analytics Platform - ML Tests
======================================
"""

import pytest
from src.ml import ViralPredictor, GrowthForecaster, SentimentAnalyzer


class TestViralPredictor:
    """Tests for viral prediction model."""
    
    def test_extract_features(self):
        """Test feature extraction."""
        predictor = ViralPredictor()
        
        video_data = {
            'title': 'Amazing Tutorial! 🚀 Top 10 Tips',
            'description': 'Learn the best practices',
            'tags': ['tutorial', 'tips', 'coding'],
            'duration_seconds': 600,
            'channel_subscribers': 10000,
            'published_at': '2024-01-15T14:30:00Z'
        }
        
        features = predictor.extract_features(video_data)
        
        assert features.shape[0] == 1
        assert features.shape[1] > 0
    
    def test_predict_without_training(self):
        """Test prediction without trained model."""
        predictor = ViralPredictor()
        predictor.model = None  # Ensure no model
        
        result = predictor.predict({
            'title': 'Test Video',
            'description': 'Test',
            'tags': []
        })
        
        assert 'error' in result or 'viral_probability' in result


class TestSentimentAnalyzer:
    """Tests for sentiment analysis."""
    
    def test_analyze_positive_text(self):
        """Test positive sentiment detection."""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("This is amazing! I love it so much!")
        
        assert result['label'] == 'positive'
        assert result['score'] > 0
    
    def test_analyze_negative_text(self):
        """Test negative sentiment detection."""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("This is terrible and awful. Very disappointed.")
        
        assert result['label'] == 'negative'
        assert result['score'] < 0
    
    def test_analyze_neutral_text(self):
        """Test neutral sentiment detection."""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("The video is uploaded.")
        
        assert result['label'] == 'neutral'
    
    def test_analyze_empty_text(self):
        """Test handling of empty text."""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_text("")
        
        assert result['label'] == 'neutral'
        assert result['score'] == 0.0
    
    def test_analyze_comments_batch(self, sample_comments):
        """Test batch comment analysis."""
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze_comments(sample_comments)
        
        assert 'total_comments' in result
        assert result['total_comments'] == len(sample_comments)
        assert 'sentiment_distribution' in result
        assert 'avg_sentiment' in result
    
    def test_extract_topics(self):
        """Test topic extraction."""
        analyzer = SentimentAnalyzer()
        texts = [
            "Python programming tutorial for beginners",
            "Learn Python coding step by step",
            "Python is the best programming language"
        ]
        
        topics = analyzer.extract_topics(texts, top_n=5)
        
        assert len(topics) > 0
        assert topics[0][1] >= topics[-1][1]  # Sorted by frequency


class TestGrowthForecaster:
    """Tests for growth forecasting."""
    
    def test_fallback_forecast(self):
        """Test fallback forecasting method."""
        forecaster = GrowthForecaster()
        
        data = [
            {'date': '2024-01-01', 'subscribers': 1000},
            {'date': '2024-01-02', 'subscribers': 1010},
            {'date': '2024-01-03', 'subscribers': 1020},
            {'date': '2024-01-04', 'subscribers': 1030},
            {'date': '2024-01-05', 'subscribers': 1040},
        ]
        
        result = forecaster._fallback_forecast(data, 'subscribers', periods=7)
        
        assert 'forecast' in result
        assert len(result['forecast']) == 7
        assert result['model'] == 'linear_fallback'
    
    def test_forecast_engagement(self):
        """Test engagement forecasting."""
        forecaster = GrowthForecaster()
        
        posts_data = [
            {'like_count': 100, 'comments_count': 10, 'engagement_rate': 0.05},
            {'like_count': 120, 'comments_count': 15, 'engagement_rate': 0.06},
            {'like_count': 90, 'comments_count': 8, 'engagement_rate': 0.04},
        ]
        
        result = forecaster.forecast_engagement(posts_data, periods=5)
        
        assert 'expected_likes' in result
        assert 'expected_engagement_rate' in result
