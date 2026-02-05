
import pytest
import sys
import os
import numpy as np

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ml.recommendations import ContentRecommender
from src.ml.competitor import CompetitorAnalyzer

class TestMLModels:
    """Test machine learning model performance"""
    
    def test_recommendation_system(self):
        """Test content recommendation engine"""
        recommender = ContentRecommender()
        
        # Mock data
        videos_data = [
            {'title': 'Python Tutorial 1', 'tags': ['python', 'coding'], 'views': 1000, 'likes': 50, 'comments': 5},
            {'title': 'Python Tutorial 2', 'tags': ['python', 'tutorial'], 'views': 2000, 'likes': 100, 'comments': 10},
            {'title': 'Gaming Video', 'tags': ['gaming', 'minecraft'], 'views': 500, 'likes': 10, 'comments': 1}
        ]
        
        recommendations = recommender.recommend_topics(videos_data, top_n=3)
        
        assert len(recommendations) > 0, "Should return recommendations"
        assert recommendations[0]['topic'] in ['python', 'coding', 'tutorial'], "Should identify top topics"
        
        print("✓ Recommendation system working")

    def test_competitor_analysis(self):
         """Test competitor analysis logic"""
         analyzer = CompetitorAnalyzer()
         
         # Mock objects that behave like dictionaries for compatibility
         my_channel = {'title': 'Me', 'subscribers': 1000, 'total_views': 5000, 'videos': [{'views': 500, 'likes': 50}]}
         competitors = [
             {'title': 'Comp1', 'subscribers': 2000, 'total_views': 10000, 'videos': [{'views': 1000, 'likes': 100}]},
             {'title': 'Comp2', 'subscribers': 500, 'total_views': 2000, 'videos': [{'views': 200, 'likes': 20}]}
         ]
         
         results = analyzer.compare_metrics(my_channel, competitors)
         
         assert 'your_rank' in results, "Should calculate rankings"
         assert len(results['rankings']) == 3, "Ranking calculation incorrect"
         
         print("✓ Competitor analysis working")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
