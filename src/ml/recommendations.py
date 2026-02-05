"""
Content Analytics Platform - Content Recommendations Engine
============================================================
AI-powered content recommendations based on performance data.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import numpy as np
from loguru import logger


class ContentRecommender:
    """
    Generate content recommendations based on historical performance data.
    
    Uses collaborative filtering and content-based analysis to suggest:
    - Trending topics
    - Optimal posting times
    - Content types and formats
    - Tags and keywords
    """
    
    def __init__(self):
        """Initialize the recommender."""
        self.engagement_weights = {
            'views': 0.3,
            'likes': 0.25,
            'comments': 0.25,
            'shares': 0.2
        }
    
    def recommend_topics(
        self,
        videos_data: List[Dict],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend trending topics based on high-performing content.
        
        Args:
            videos_data: List of video data with performance metrics
            top_n: Number of topics to recommend
            
        Returns:
            List of topic recommendations with scores
        """
        if not videos_data:
            return []
        
        # Calculate engagement score for each video
        scored_videos = []
        for video in videos_data:
            score = self._calculate_engagement_score(video)
            scored_videos.append({**video, 'engagement_score': score})
        
        # Sort by engagement score
        scored_videos.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Extract topics from top performers
        topic_scores = {}
        for video in scored_videos[:50]:  # Top 50 videos
            tags = video.get('tags') or []
            title_words = self._extract_keywords(video.get('title') or '')
            
            for tag in tags:
                tag_lower = tag.lower().strip()
                if tag_lower:
                    if tag_lower not in topic_scores:
                        topic_scores[tag_lower] = {'score': 0, 'count': 0}
                    topic_scores[tag_lower]['score'] += video['engagement_score']
                    topic_scores[tag_lower]['count'] += 1
            
            for word in title_words:
                if word not in topic_scores:
                    topic_scores[word] = {'score': 0, 'count': 0}
                topic_scores[word]['score'] += video['engagement_score'] * 0.5
                topic_scores[word]['count'] += 1
        
        # Calculate average score and rank
        ranked_topics = []
        for topic, data in topic_scores.items():
            if data['count'] >= 2:  # Minimum appearances
                avg_score = data['score'] / data['count']
                ranked_topics.append({
                    'topic': topic,
                    'relevance_score': float(round(avg_score, 2)),
                    'frequency': int(data['count']),
                    'trending': bool(data['count'] >= 5)
                })
        
        ranked_topics.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return ranked_topics[:top_n]
    
    def recommend_posting_time(
        self,
        videos_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze optimal posting times based on engagement patterns.
        
        Args:
            videos_data: List of video data with timestamps and metrics
            
        Returns:
            Optimal posting time recommendations
        """
        if not videos_data:
            return {
                'best_hours': [],
                'best_days': [],
                'heatmap': []
            }
        
        # Initialize heatmap (7 days x 24 hours)
        heatmap = [[0.0 for _ in range(24)] for _ in range(7)]
        counts = [[0 for _ in range(24)] for _ in range(7)]
        
        for video in videos_data:
            published = video.get('published_at')
            if not published:
                continue
            
            if isinstance(published, str):
                try:
                    published = datetime.fromisoformat(published.replace('Z', '+00:00'))
                except:
                    continue
            
            day = published.weekday()
            hour = published.hour
            score = self._calculate_engagement_score(video)
            
            heatmap[day][hour] += score
            counts[day][hour] += 1
        
        # Calculate averages
        for d in range(7):
            for h in range(24):
                if counts[d][h] > 0:
                    heatmap[d][h] = round(heatmap[d][h] / counts[d][h], 2)
        
        # Find best hours (aggregate across days)
        hour_scores = {}
        for h in range(24):
            total = sum(heatmap[d][h] for d in range(7))
            count = sum(1 for d in range(7) if heatmap[d][h] > 0)
            if count > 0:
                hour_scores[h] = total / count
        
        best_hours = sorted(hour_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Find best days
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_scores = {}
        for d in range(7):
            total = sum(heatmap[d])
            count = sum(1 for h in range(24) if heatmap[d][h] > 0)
            if count > 0:
                day_scores[days[d]] = total / count
        
        best_days = sorted(day_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'best_hours': [
                {'hour': int(h), 'score': float(round(s, 2)), 'label': f"{h:02d}:00"}
                for h, s in best_hours
            ],
            'best_days': [
                {'day': str(d), 'score': float(round(s, 2))}
                for d, s in best_days
            ],
            'heatmap': heatmap,
            'recommendation': self._format_time_recommendation(best_hours, best_days)
        }
    
    def recommend_content_type(
        self,
        videos_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Recommend content types and formats based on performance.
        
        Args:
            videos_data: List of video data with duration and metrics
            
        Returns:
            Content type recommendations
        """
        if not videos_data:
            return {'recommendations': []}
        
        # Categorize by duration
        duration_buckets = {
            'short': {'range': (0, 60), 'label': 'Short (<1 min)', 'videos': []},
            'medium': {'range': (60, 300), 'label': 'Medium (1-5 min)', 'videos': []},
            'standard': {'range': (300, 600), 'label': 'Standard (5-10 min)', 'videos': []},
            'long': {'range': (600, 1200), 'label': 'Long (10-20 min)', 'videos': []},
            'extended': {'range': (1200, float('inf')), 'label': 'Extended (20+ min)', 'videos': []}
        }
        
        for video in videos_data:
            duration = video.get('duration_seconds') or 0
            score = self._calculate_engagement_score(video)
            
            for bucket_name, bucket in duration_buckets.items():
                if bucket['range'][0] <= duration < bucket['range'][1]:
                    bucket['videos'].append(score)
                    break
        
        # Calculate performance by duration
        recommendations = []
        for bucket_name, bucket in duration_buckets.items():
            if bucket['videos']:
                avg_score = sum(bucket['videos']) / len(bucket['videos'])
                recommendations.append({
                    'type': bucket_name,
                    'label': bucket['label'],
                    'avg_engagement': float(round(avg_score, 2)),
                    'sample_size': int(len(bucket['videos'])),
                    'recommended': bool(avg_score > 50)
                })
        
        recommendations.sort(key=lambda x: x['avg_engagement'], reverse=True)
        
        # Determine optimal duration
        optimal = recommendations[0] if recommendations else None
        
        return {
            'recommendations': recommendations,
            'optimal_format': optimal,
            'insight': self._generate_format_insight(recommendations)
        }
    
    def recommend_tags(
        self,
        videos_data: List[Dict],
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Recommend tags based on high-performing content.
        
        Args:
            videos_data: List of video data with tags and metrics
            top_n: Number of tags to recommend
            
        Returns:
            List of tag recommendations with performance scores
        """
        if not videos_data:
            return []
        
        tag_performance = {}
        
        for video in videos_data:
            tags = video.get('tags') or []
            score = self._calculate_engagement_score(video)
            views = video.get('views', 0)
            
            for tag in tags:
                tag = tag.lower().strip()
                if not tag or len(tag) < 2:
                    continue
                
                if tag not in tag_performance:
                    tag_performance[tag] = {
                        'scores': [],
                        'views': [],
                        'count': 0
                    }
                
                tag_performance[tag]['scores'].append(score)
                tag_performance[tag]['views'].append(views)
                tag_performance[tag]['count'] += 1
        
        # Calculate tag recommendations
        tag_recs = []
        for tag, data in tag_performance.items():
            if data['count'] >= 2:  # Minimum usage
                avg_score = sum(data['scores']) / len(data['scores'])
                avg_views = sum(data['views']) / len(data['views'])
                
                tag_recs.append({
                    'tag': str(tag),
                    'performance_score': float(round(avg_score, 2)),
                    'avg_views': int(avg_views),
                    'usage_count': int(data['count']),
                    'effectiveness': 'high' if avg_score > 70 else 'medium' if avg_score > 40 else 'low'
                })
        
        tag_recs.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return tag_recs[:top_n]
    
    def get_content_ideas(
        self,
        videos_data: List[Dict],
        num_ideas: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate content ideas based on trend analysis.
        
        Args:
            videos_data: Historical video data
            num_ideas: Number of ideas to generate
            
        Returns:
            List of content ideas with context
        """
        if not videos_data:
            return []
        
        # Get top topics
        top_topics = self.recommend_topics(videos_data, top_n=10)
        
        # Get optimal format
        format_rec = self.recommend_content_type(videos_data)
        optimal_format = format_rec.get('optimal_format', {})
        
        # Get best timing
        timing = self.recommend_posting_time(videos_data)
        
        # Generate ideas by combining insights
        ideas = []
        
        for i, topic in enumerate(top_topics[:num_ideas]):
            idea = {
                'idea_number': i + 1,
                'topic': topic['topic'].title(),
                'title_suggestion': self._generate_title_suggestion(topic['topic'], videos_data),
                'recommended_format': str(optimal_format.get('label', 'Standard (5-10 min)')),
                'best_posting_time': str(timing.get('recommendation', 'Weekdays 2-4 PM')),
                'predicted_engagement': float(topic['relevance_score']),
                'confidence': 'high' if topic['frequency'] >= 5 else 'medium',
                'similar_successful_videos': self._find_similar_videos(topic['topic'], videos_data)[:3]
            }
            ideas.append(idea)
        
        return ideas
    
    def _calculate_engagement_score(self, video: Dict) -> float:
        """Calculate weighted engagement score (0-100)."""
        views = video.get('views', 0)
        likes = video.get('likes', 0)
        comments = video.get('comments', 0)
        
        if views == 0:
            return 0
        
        like_rate = (likes / views) * 100 if views else 0
        comment_rate = (comments / views) * 100 if views else 0
        
        # Normalize scores
        view_score = min(100, np.log10(views + 1) * 15)
        like_score = min(100, like_rate * 10)
        comment_score = min(100, comment_rate * 50)
        
        engagement = (
            view_score * self.engagement_weights['views'] +
            like_score * self.engagement_weights['likes'] +
            comment_score * self.engagement_weights['comments']
        )
        
        return float(min(100, engagement))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        if not text:
            return []
        
        # Simple keyword extraction
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'must', 'this', 'that', 'these', 'those',
                      'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her',
                      'its', 'our', 'their', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
        
        words = text.lower().split()
        keywords = [w.strip('.,!?()[]{}":;') for w in words 
                   if w.lower() not in stop_words and len(w) > 2]
        
        return keywords[:10]  # Return top 10 keywords
    
    def _format_time_recommendation(
        self,
        best_hours: List[Tuple[int, float]],
        best_days: List[Tuple[str, float]]
    ) -> str:
        """Format time recommendation as readable string."""
        if not best_hours or not best_days:
            return "Insufficient data for recommendation"
        
        day = best_days[0][0] if best_days else "Weekday"
        hour = best_hours[0][0] if best_hours else 14
        
        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        
        return f"Best: {day}s around {display_hour}:00 {period}"
    
    def _generate_format_insight(self, recommendations: List[Dict]) -> str:
        """Generate insight about content format."""
        if not recommendations:
            return "Need more data to generate insights"
        
        top = recommendations[0]
        return f"Your {top['label']} content performs best with {top['avg_engagement']:.0f}% avg engagement"
    
    def _generate_title_suggestion(self, topic: str, videos_data: List[Dict]) -> str:
        """Generate a title suggestion based on successful patterns."""
        # Find successful videos with this topic
        relevant = [v for v in videos_data 
                   if topic.lower() in (v.get('title') or '').lower() or 
                   topic.lower() in str(v.get('tags') or []).lower()]
        
        if not relevant:
            return f"How to Master {topic.title()} in 2024"
        
        # Analyze patterns in successful titles
        patterns = [
            f"The Ultimate {topic.title()} Guide",
            f"{topic.title()}: Everything You Need to Know",
            f"10 {topic.title()} Tips That Actually Work",
            f"Why {topic.title()} Changed My Life",
            f"{topic.title()} Tutorial for Beginners"
        ]
        
        return patterns[hash(topic) % len(patterns)]
    
    def _find_similar_videos(self, topic: str, videos_data: List[Dict]) -> List[Dict]:
        """Find videos similar to a topic."""
        similar = []
        for video in videos_data:
            if topic.lower() in video.get('title', '').lower():
                similar.append({
                    'title': video.get('title', '')[:50],
                    'views': video.get('views', 0),
                    'engagement': self._calculate_engagement_score(video)
                })
        
        similar.sort(key=lambda x: x['engagement'], reverse=True)
        return similar
