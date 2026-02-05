"""
Content Analytics Platform - Analytics Package
==============================================
"""

from .metrics import YouTubeMetrics, InstagramMetrics, CompetitorBenchmark
from .trends import TrendAnalyzer

__all__ = [
    'YouTubeMetrics',
    'InstagramMetrics',
    'CompetitorBenchmark',
    'TrendAnalyzer',
]
