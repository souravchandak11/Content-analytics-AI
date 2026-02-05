"""
Content Analytics Platform - Competitor Analysis Module
========================================================
Competitive benchmarking and gap analysis for content creators.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from loguru import logger


class CompetitorAnalyzer:
    """
    Analyze and benchmark against competitors.
    
    Provides insights on:
    - Performance comparison
    - Content gaps and opportunities
    - Industry benchmarking
    - Competitive trends
    """
    
    def __init__(self):
        """Initialize the competitor analyzer."""
        self.metrics_weights = {
            'subscribers': 0.25,
            'views': 0.25,
            'engagement_rate': 0.30,
            'upload_frequency': 0.20
        }
    
    def compare_metrics(
        self,
        your_channel: Dict,
        competitors: List[Dict]
    ) -> Dict[str, Any]:
        """
        Compare your channel metrics against competitors.
        """
        if not your_channel or not competitors:
            return {'error': 'Insufficient data for comparison'}
        
        all_channels = [your_channel] + competitors
        channel_metrics = []
        for channel in all_channels:
            metrics = self._extract_metrics(channel)
            channel_metrics.append({
                'name': channel.get('title', channel.get('name', 'Unknown')),
                'channel_id': channel.get('channel_id', ''),
                'is_you': channel == your_channel,
                **metrics
            })
        
        # Rank channels by each metric
        metrics_to_rank = ['subscribers', 'total_views', 'engagement_rate', 'upload_frequency']
        for metric in metrics_to_rank:
            sorted_channels = sorted(channel_metrics, key=lambda x: x.get(metric, 0), reverse=True)
            for i, ch in enumerate(sorted_channels):
                ch[f'{metric}_rank'] = i + 1
        
        # Calculate overall score
        for ch in channel_metrics:
            ch['overall_score'] = self._calculate_overall_score(ch, len(channel_metrics))
        
        channel_metrics.sort(key=lambda x: x['overall_score'], reverse=True)
        your_rank = next((i + 1 for i, ch in enumerate(channel_metrics) if ch['is_you']), 0)
        
        return {
            'rankings': channel_metrics,
            'your_rank': your_rank,
            'total_compared': len(channel_metrics),
            'percentile': round((1 - (your_rank - 1) / len(channel_metrics)) * 100, 1),
            'insights': self._generate_comparison_insights(channel_metrics, your_rank)
        }
    
    def identify_gaps(
        self,
        your_videos: List[Dict],
        competitor_videos: List[Dict]
    ) -> Dict[str, Any]:
        """
        Identify content gaps and opportunities.
        """
        your_topics = self._extract_topics(your_videos)
        competitor_topics = self._extract_topics(competitor_videos)
        
        gaps = []
        for topic, data in competitor_topics.items():
            if topic not in your_topics and data['count'] >= 2:
                gaps.append({
                    'topic': topic,
                    'competitor_frequency': data['count'],
                    'avg_views': int(data['total_views'] / data['count']),
                    'avg_engagement': round(data['total_engagement'] / data['count'], 2),
                    'opportunity_score': self._calculate_opportunity_score(data)
                })
        
        gaps.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        strengths = []
        for topic, data in your_topics.items():
            if topic in competitor_topics:
                comp_data = competitor_topics[topic]
                your_avg = data['total_engagement'] / data['count'] if data['count'] else 0
                comp_avg = comp_data['total_engagement'] / comp_data['count'] if comp_data['count'] else 0
                if your_avg > comp_avg * 1.2:
                    strengths.append({
                        'topic': topic,
                        'your_engagement': round(your_avg, 2),
                        'competitor_engagement': round(comp_avg, 2),
                        'advantage': round((your_avg / comp_avg - 1) * 100, 1)
                    })
        
        return {
            'content_gaps': gaps[:10],
            'your_strengths': strengths[:10],
            'recommendation': self._generate_gap_recommendation(gaps, strengths)
        }

    def _extract_metrics(self, channel: Dict) -> Dict:
        videos = channel.get('videos', [])
        total_views = sum(v.get('views', 0) for v in videos)
        total_likes = sum(v.get('likes', 0) for v in videos)
        total_comments = sum(v.get('comments', 0) for v in videos)
        
        engagement_rate = ((total_likes + total_comments) / total_views) * 100 if total_views > 0 else 0
        
        return {
            'subscribers': channel.get('subscribers', channel.get('subscriber_count', 0)),
            'total_views': total_views or channel.get('total_views', 0),
            'engagement_rate': round(engagement_rate, 2),
            'upload_frequency': round(len(videos) / 4, 2), # Simplified
            'video_count': len(videos) or channel.get('total_videos', 0)
        }

    def _calculate_overall_score(self, channel: Dict, total_count: int) -> float:
        scores = []
        for metric, weight in self.metrics_weights.items():
            rank_key = f"{'total_views' if metric == 'views' else metric}_rank"
            rank = channel.get(rank_key, total_count)
            score = (total_count - rank + 1) / total_count * 100
            scores.append(score * weight)
        return round(sum(scores), 2)

    def _extract_topics(self, videos: List[Dict]) -> Dict[str, Dict]:
        topics = {}
        for video in videos:
            tags = video.get('tags') or []
            views = video.get('views', 0)
            engagement = video.get('engagement_rate', 0) or 0
            for tag in tags:
                tag = tag.lower().strip()
                if not tag: continue
                if tag not in topics:
                    topics[tag] = {'count': 0, 'total_views': 0, 'total_engagement': 0}
                topics[tag]['count'] += 1
                topics[tag]['total_views'] += views
                topics[tag]['total_engagement'] += engagement
        return topics

    def _calculate_opportunity_score(self, data: Dict) -> float:
        avg_views = data['total_views'] / max(data['count'], 1)
        return round(np.log10(avg_views + 1) * 10 + data['total_engagement'] / max(data['count'], 1), 2)

    def _generate_comparison_insights(self, rankings: List[Dict], your_rank: int) -> List[str]:
        if your_rank == 1: return ["🏆 Top performer!"]
        return [f"📊 Ranked #{your_rank} of {len(rankings)}."]

    def _generate_gap_recommendation(self, gaps: List[Dict], strengths: List[Dict]) -> str:
        if gaps: return f"Opportunity in '{gaps[0]['topic']}'."
        return "Keep growing!"
