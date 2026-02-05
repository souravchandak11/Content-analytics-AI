"""
Content Analytics Platform - Analytics Metrics
===============================================
Core metrics calculations for YouTube and Instagram analytics.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from scipy import stats


class YouTubeMetrics:
    """
    YouTube performance metrics calculations.
    """
    
    @staticmethod
    def engagement_rate(views: int, likes: int, comments: int) -> float:
        """
        Calculate engagement rate.
        
        Formula: (Likes + Comments) / Views * 100
        
        Industry benchmarks:
        - Excellent: > 6%
        - Good: 3-6%
        - Average: 1-3%
        - Poor: < 1%
        """
        if views == 0:
            return 0.0
        return round(((likes + comments) / views) * 100, 4)
    
    @staticmethod
    def like_rate(views: int, likes: int) -> float:
        """Like rate (likes per view percentage)."""
        if views == 0:
            return 0.0
        return round((likes / views) * 100, 4)
    
    @staticmethod
    def comment_rate(views: int, comments: int) -> float:
        """Comment rate (comments per view percentage)."""
        if views == 0:
            return 0.0
        return round((comments / views) * 100, 4)
    
    @staticmethod
    def views_per_subscriber(views: int, subscribers: int) -> float:
        """Views per subscriber ratio."""
        if subscribers == 0:
            return 0.0
        return round(views / subscribers, 2)
    
    @staticmethod
    def average_view_duration_score(
        avg_view_duration: int, 
        video_duration: int
    ) -> float:
        """
        Calculate audience retention score.
        
        Returns percentage of video watched on average.
        """
        if video_duration == 0:
            return 0.0
        return round((avg_view_duration / video_duration) * 100, 2)
    
    @staticmethod
    def virality_score(
        views: int,
        likes: int,
        comments: int,
        published_days: int,
        avg_channel_views: float
    ) -> float:
        """
        Calculate a virality score (0-100).
        
        Considers:
        - Views vs channel average
        - Engagement rate
        - Growth velocity
        """
        if published_days == 0 or avg_channel_views == 0:
            return 0.0
        
        # View velocity (views per day)
        velocity = views / max(published_days, 1)
        
        # Relative performance
        relative_views = views / avg_channel_views
        
        # Engagement factor
        engagement = YouTubeMetrics.engagement_rate(views, likes, comments)
        
        # Combined score (normalized to 0-100)
        score = (
            min(relative_views * 20, 40) +  # Max 40 points for views
            min(engagement * 5, 30) +        # Max 30 points for engagement
            min(velocity / 1000, 30)         # Max 30 points for velocity
        )
        
        return round(min(score, 100), 2)
    
    @staticmethod
    def growth_rate(
        current_value: int,
        previous_value: int
    ) -> float:
        """Calculate percentage growth rate."""
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        return round(((current_value - previous_value) / previous_value) * 100, 2)
    
    @staticmethod
    def channel_health_score(
        subscriber_growth_rate: float,
        avg_engagement_rate: float,
        upload_frequency: float,  # videos per week
        avg_views_per_video: float,
        subscribers: int
    ) -> Dict[str, Any]:
        """
        Calculate overall channel health score.
        
        Returns a score (0-100) with breakdown.
        """
        # Subscriber growth component (0-25)
        growth_score = min(max(subscriber_growth_rate, 0) * 2, 25)
        
        # Engagement component (0-25)
        engagement_score = min(avg_engagement_rate * 5, 25)
        
        # Consistency component (0-25)
        # Ideal: 1-3 videos per week
        if 1 <= upload_frequency <= 3:
            consistency_score = 25
        elif upload_frequency < 1:
            consistency_score = upload_frequency * 15
        else:
            consistency_score = max(25 - (upload_frequency - 3) * 3, 10)
        
        # Performance component (0-25)
        # Views per video relative to subscribers
        views_ratio = avg_views_per_video / max(subscribers, 1)
        performance_score = min(views_ratio * 50, 25)
        
        total_score = growth_score + engagement_score + consistency_score + performance_score
        
        return {
            'total_score': round(total_score, 1),
            'growth_score': round(growth_score, 1),
            'engagement_score': round(engagement_score, 1),
            'consistency_score': round(consistency_score, 1),
            'performance_score': round(performance_score, 1),
            'grade': _score_to_grade(total_score)
        }


class InstagramMetrics:
    """
    Instagram performance metrics calculations.
    """
    
    @staticmethod
    def engagement_rate(
        likes: int,
        comments: int,
        followers: int
    ) -> float:
        """
        Calculate Instagram engagement rate.
        
        Formula: (Likes + Comments) / Followers * 100
        
        Industry benchmarks:
        - Excellent: > 6%
        - Good: 3-6%
        - Average: 1-3%
        - Poor: < 1%
        """
        if followers == 0:
            return 0.0
        return round(((likes + comments) / followers) * 100, 4)
    
    @staticmethod
    def engagement_rate_by_reach(
        likes: int,
        comments: int,
        reach: int
    ) -> float:
        """
        Engagement rate by reach (more accurate).
        
        Formula: (Likes + Comments) / Reach * 100
        """
        if reach == 0:
            return 0.0
        return round(((likes + comments) / reach) * 100, 4)
    
    @staticmethod
    def save_rate(saves: int, reach: int) -> float:
        """Save rate (saves per reach)."""
        if reach == 0:
            return 0.0
        return round((saves / reach) * 100, 4)
    
    @staticmethod
    def reach_rate(reach: int, followers: int) -> float:
        """Reach rate (percentage of followers reached)."""
        if followers == 0:
            return 0.0
        return round((reach / followers) * 100, 2)
    
    @staticmethod
    def impression_frequency(
        impressions: int,
        reach: int
    ) -> float:
        """Average times each reached user saw the content."""
        if reach == 0:
            return 0.0
        return round(impressions / reach, 2)
    
    @staticmethod
    def follower_growth_rate(
        current_followers: int,
        previous_followers: int
    ) -> float:
        """Calculate follower growth rate percentage."""
        if previous_followers == 0:
            return 100.0 if current_followers > 0 else 0.0
        return round(
            ((current_followers - previous_followers) / previous_followers) * 100, 
            2
        )
    
    @staticmethod
    def best_posting_time(
        posts_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze best posting times based on engagement.
        
        Args:
            posts_data: List of posts with timestamp and engagement
            
        Returns:
            Best times analysis
        """
        if not posts_data:
            return {'error': 'No data'}
        
        df = pd.DataFrame(posts_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day_name()
        
        # Analyze by hour
        hourly = df.groupby('hour').agg({
            'engagement_rate': 'mean',
            'like_count': 'mean'
        }).round(2)
        
        best_hour = hourly['engagement_rate'].idxmax()
        
        # Analyze by day
        daily = df.groupby('day').agg({
            'engagement_rate': 'mean',
            'like_count': 'mean'
        }).round(2)
        
        best_day = daily['engagement_rate'].idxmax()
        
        return {
            'best_hour': int(best_hour),
            'best_day': best_day,
            'hourly_engagement': hourly['engagement_rate'].to_dict(),
            'daily_engagement': daily['engagement_rate'].to_dict()
        }


class CompetitorBenchmark:
    """
    Competitive benchmarking utilities.
    """
    
    @staticmethod
    def calculate_percentile(
        value: float,
        comparison_values: List[float]
    ) -> float:
        """Calculate percentile rank among competitors."""
        if not comparison_values:
            return 50.0
        return round(stats.percentileofscore(comparison_values, value), 1)
    
    @staticmethod
    def performance_index(
        channel_metric: float,
        industry_avg: float
    ) -> float:
        """
        Calculate performance index.
        
        100 = at industry average
        >100 = above average
        <100 = below average
        """
        if industry_avg == 0:
            return 100.0
        return round((channel_metric / industry_avg) * 100, 1)
    
    @staticmethod
    def compare_channels(
        channels_data: List[Dict]
    ) -> pd.DataFrame:
        """
        Create comparative analysis of multiple channels.
        
        Args:
            channels_data: List of channel metric dictionaries
            
        Returns:
            DataFrame with rankings and comparisons
        """
        df = pd.DataFrame(channels_data)
        
        # Add rankings
        for metric in ['subscribers', 'avg_views', 'engagement_rate']:
            if metric in df.columns:
                df[f'{metric}_rank'] = df[metric].rank(ascending=False)
        
        return df


def _score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'
