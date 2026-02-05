"""
Content Analytics Platform - Topic Clustering Module
=====================================================
NLP-based content categorization and theme extraction.
"""

from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from loguru import logger


class TopicClusterer:
    """
    Cluster content into semantic groups and identify dominant themes.
    """
    
    def __init__(self, n_clusters: int = 5):
        """Initialize clusterer."""
        self.n_clusters = n_clusters
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,
            ngram_range=(1, 2)
        )
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    
    def cluster_content(
        self,
        videos_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Group videos into clusters based on title and description.
        """
        if len(videos_data) < self.n_clusters:
            return {'error': 'Not enough data to cluster'}
            
        # Prepare text data
        texts = []
        for v in videos_data:
            title = v.get('title', '')
            desc = v.get('description', '') or ''
            texts.append(f"{title} {desc}")
            
        try:
            # Vectorize and cluster
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            clusters = self.model.fit_predict(tfidf_matrix)
            
            # Group videos by cluster
            grouped_videos = [[] for _ in range(self.n_clusters)]
            for i, cluster_id in enumerate(clusters):
                video = videos_data[i]
                video_info = {
                    'video_id': video.get('video_id'),
                    'title': video.get('title'),
                    'views': video.get('views', 0),
                    'engagement': video.get('engagement_rate', 0)
                }
                grouped_videos[cluster_id].append(video_info)
                
            # Analyze each cluster
            cluster_insights = []
            feature_names = self.vectorizer.get_feature_names_out()
            order_centroids = self.model.cluster_centers_.argsort()[:, ::-1]
            
            for i in range(self.n_clusters):
                videos = grouped_videos[i]
                if not videos: continue
                
                # Top keywords for cluster
                keywords = [feature_names[ind] for ind in order_centroids[i, :10]]
                
                avg_views = np.mean([v['views'] for v in videos])
                avg_engagement = np.mean([v['engagement'] for v in videos])
                
                cluster_insights.append({
                    'cluster_id': int(i),
                    'name': f"Topic: {keywords[0].title()}",
                    'keywords': [str(k) for k in keywords],
                    'video_count': int(len(videos)),
                    'avg_views': int(avg_views),
                    'avg_engagement': float(round(float(avg_engagement), 2)),
                    'performance_index': float(self._calculate_performance_index(avg_views, avg_engagement))
                })
                
            cluster_insights.sort(key=lambda x: x['avg_views'], reverse=True)
            
            return {
                'clusters': cluster_insights,
                'total_videos': len(videos_data),
                'top_performing_topic': cluster_insights[0] if cluster_insights else None
            }
            
        except Exception as e:
            logger.error(f"Clustering error: {e}")
            return {'error': str(e)}

    def _calculate_performance_index(self, views: float, engagement: float) -> float:
        return round(np.log10(views + 1) * engagement, 2)

    def extract_themes(self, videos_data: List[Dict]) -> List[Dict]:
        """Simplified theme extraction."""
        all_tags = []
        for v in videos_data:
            all_tags.extend(v.get('tags', []))
        
        counts = Counter(all_tags).most_common(10)
        return [{'theme': tag, 'frequency': count} for tag, count in counts]
