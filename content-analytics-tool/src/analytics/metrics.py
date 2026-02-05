"""Engagement Metrics and Sentiment Analysis for Content Analytics Tool."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class EngagementMetrics:
    """Calculate engagement metrics for social media content."""
    
    @staticmethod
    def youtube_engagement_rate(
        views: int,
        likes: int,
        comments: int,
        shares: int = 0
    ) -> float:
        """Calculate YouTube video engagement rate.
        
        Args:
            views: Total view count
            likes: Total like count
            comments: Total comment count
            shares: Total share count (optional)
            
        Returns:
            Engagement rate as percentage (0-100)
        """
        if views == 0:
            return 0.0
        
        engagement = likes + comments + shares
        return round((engagement / views) * 100, 2)
    
    @staticmethod
    def instagram_engagement_rate(
        followers: int,
        likes: int,
        comments: int
    ) -> float:
        """Calculate Instagram engagement rate.
        
        Args:
            followers: Total follower count
            likes: Total likes on post(s)
            comments: Total comments on post(s)
            
        Returns:
            Engagement rate as percentage (0-100)
        """
        if followers == 0:
            return 0.0
        
        engagement = likes + comments
        return round((engagement / followers) * 100, 2)
    
    @staticmethod
    def growth_rate(
        current_value: int,
        previous_value: int
    ) -> float:
        """Calculate growth rate between two values.
        
        Args:
            current_value: Current metric value
            previous_value: Previous metric value
            
        Returns:
            Growth rate as percentage (can be negative)
        """
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        
        return round(((current_value - previous_value) / previous_value) * 100, 2)
    
    @staticmethod
    def average_engagement(posts: List[Dict[str, Any]], metric: str = 'like_count') -> float:
        """Calculate average engagement for a list of posts.
        
        Args:
            posts: List of post dictionaries
            metric: Metric to average ('like_count', 'comment_count', 'view_count')
            
        Returns:
            Average engagement value
        """
        if not posts:
            return 0.0
        
        total = sum(post.get(metric, 0) for post in posts)
        return round(total / len(posts), 2)
    
    @staticmethod
    def posts_per_period(
        posts: List[Dict[str, Any]],
        days: int = 30,
        date_field: str = 'timestamp'
    ) -> float:
        """Calculate average posts per time period.
        
        Args:
            posts: List of post dictionaries with date field
            days: Number of days to consider
            date_field: Name of the date field in post dictionaries
            
        Returns:
            Average posts per day
        """
        if not posts or days <= 0:
            return 0.0
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent_posts = []
        
        for post in posts:
            post_date = post.get(date_field)
            if isinstance(post_date, str):
                try:
                    post_date = datetime.fromisoformat(post_date.replace('Z', '+00:00'))
                except ValueError:
                    continue
            
            if post_date and post_date >= cutoff:
                recent_posts.append(post)
        
        return round(len(recent_posts) / days, 2)


class SentimentAnalyzer:
    """Analyze sentiment of text content using TextBlob."""
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        try:
            from textblob import TextBlob
            self._TextBlob = TextBlob
            self._available = True
        except ImportError:
            self._available = False
            self._TextBlob = None
    
    def analyze(self, text: str) -> Optional[float]:
        """Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score from -1 (negative) to 1 (positive), or None if unavailable
        """
        if not self._available or not text:
            return None
        
        try:
            blob = self._TextBlob(text)
            return round(blob.sentiment.polarity, 3)
        except Exception:
            return None
    
    def analyze_batch(self, texts: List[str]) -> List[Optional[float]]:
        """Analyze sentiment of multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment scores
        """
        return [self.analyze(text) for text in texts]
    
    def categorize(self, score: Optional[float]) -> str:
        """Categorize sentiment score.
        
        Args:
            score: Sentiment score (-1 to 1)
            
        Returns:
            Sentiment category ('positive', 'negative', or 'neutral')
        """
        if score is None:
            return 'unknown'
        
        if score > 0.1:
            return 'positive'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def get_sentiment_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Get distribution of sentiment categories.
        
        Args:
            scores: List of sentiment scores
            
        Returns:
            Dictionary with counts for each category
        """
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0, 'unknown': 0}
        
        for score in scores:
            category = self.categorize(score)
            distribution[category] += 1
        
        return distribution
