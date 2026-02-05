"""
Analytics Benchmarking Utilities
================================
Compare channel performance against industry leaders.
"""

from .real_world_creators import (
    MRBEAST_DATA, ISHOWSPEED_DATA, MKBHD_DATA,
    PLATFORM_BENCHMARKS
)


def benchmark_channel(channel_metrics: dict) -> dict:
    """
    Benchmark a channel against industry leaders.
    
    Args:
        channel_metrics: Dict with keys:
            - subscribers: int
            - avg_views_per_video: int
            - engagement_rate: float
            - category: str
    
    Returns:
        dict: Benchmark comparison results
    """
    engagement = channel_metrics.get('engagement_rate', 0)
    subscribers = channel_metrics.get('subscribers', 0)
    avg_views = channel_metrics.get('avg_views_per_video', 0)
    
    # Determine tier
    if engagement > 6.0:
        tier = 'Elite'
        tier_examples = ['IShowSpeed (7.36%)', 'MrBeast (5.67%)']
    elif engagement > 4.0:
        tier = 'Above Average'
        tier_examples = ['PewDiePie (4.82%)', 'Dude Perfect (4.23%)']
    elif engagement > 2.5:
        tier = 'Average'
        tier_examples = ['MKBHD (3.45%)', 'Industry avg (3.2%)']
    else:
        tier = 'Below Average'
        tier_examples = ['T-Series (2.34%)', 'Cocomelon (1.89%)']
    
    # Calculate percentiles
    industry_avg = PLATFORM_BENCHMARKS['youtube']['avg_engagement_rate_all_creators']
    engagement_vs_avg = ((engagement - industry_avg) / industry_avg) * 100
    
    # Views per subscriber ratio
    if subscribers > 0:
        view_ratio = avg_views / subscribers
        if view_ratio > 0.5:
            view_health = 'Excellent'
        elif view_ratio > 0.2:
            view_health = 'Good'
        elif view_ratio > 0.1:
            view_health = 'Average'
        else:
            view_health = 'Below Average'
    else:
        view_health = 'Unknown'
    
    # Compare to leaders
    comparisons = []
    
    if engagement >= MRBEAST_DATA['engagement_rate']:
        comparisons.append(f"✓ Outperforming MrBeast ({MRBEAST_DATA['engagement_rate']}%)")
    else:
        gap = MRBEAST_DATA['engagement_rate'] - engagement
        comparisons.append(f"  {gap:.1f}% below MrBeast")
    
    if engagement >= MKBHD_DATA['engagement_rate']:
        comparisons.append(f"✓ Outperforming MKBHD ({MKBHD_DATA['engagement_rate']}%)")
    else:
        gap = MKBHD_DATA['engagement_rate'] - engagement
        comparisons.append(f"  {gap:.1f}% below MKBHD")
    
    return {
        'tier': tier,
        'tier_examples': tier_examples,
        'engagement_rate': engagement,
        'industry_avg': industry_avg,
        'vs_industry_avg': f"{engagement_vs_avg:+.1f}%",
        'view_health': view_health,
        'leader_comparisons': comparisons,
        'recommendations': get_recommendations(engagement, subscribers, avg_views)
    }


def get_recommendations(engagement: float, subscribers: int, avg_views: int) -> list:
    """Get improvement recommendations based on metrics."""
    recommendations = []
    
    if engagement < 3.0:
        recommendations.append({
            'area': 'Engagement',
            'priority': 'High',
            'action': 'Add more calls-to-action and ask questions to boost comments'
        })
    
    if subscribers > 0 and avg_views / subscribers < 0.1:
        recommendations.append({
            'area': 'Views',
            'priority': 'High',
            'action': 'Improve thumbnails and titles for better click-through rate'
        })
    
    if engagement < 5.0:
        recommendations.append({
            'area': 'Content Strategy',
            'priority': 'Medium',
            'action': 'Study viral patterns: challenges, giveaways, and collaborations work best'
        })
    
    return recommendations


def get_viral_threshold(subscribers: int) -> int:
    """
    Get the view count threshold for a video to be considered viral.
    
    Args:
        subscribers: Channel subscriber count
    
    Returns:
        int: Views needed to be considered viral
    """
    thresholds = PLATFORM_BENCHMARKS['youtube']['viral_threshold']
    
    if subscribers < 10_000:
        return thresholds['small_channel_1k-10k']
    elif subscribers < 100_000:
        return thresholds['medium_channel_10k-100k']
    elif subscribers < 1_000_000:
        return thresholds['large_channel_100k-1M']
    else:
        return thresholds['mega_channel_1M+']


def calculate_estimated_earnings(views: int, category: str = 'entertainment') -> dict:
    """
    Estimate earnings based on views and category.
    
    Args:
        views: Total video views
        category: Content category
    
    Returns:
        dict: Estimated earnings range
    """
    # RPM (Revenue per Mille/1000 views) by category
    rpm_ranges = {
        'technology': (5.00, 12.00),
        'finance': (8.00, 20.00),
        'entertainment': (2.00, 6.00),
        'gaming': (2.00, 5.00),
        'music': (1.00, 3.00),
        'kids': (0.50, 2.00),
        'education': (4.00, 10.00)
    }
    
    rpm_low, rpm_high = rpm_ranges.get(category.lower(), (2.50, 8.00))
    
    earnings_low = (views / 1000) * rpm_low
    earnings_high = (views / 1000) * rpm_high
    
    return {
        'low_estimate': earnings_low,
        'high_estimate': earnings_high,
        'rpm_range': f"${rpm_low:.2f} - ${rpm_high:.2f}",
        'formatted': f"${earnings_low:,.0f} - ${earnings_high:,.0f}"
    }


def compare_to_creator(channel_metrics: dict, creator_name: str) -> dict:
    """
    Compare a channel directly to a specific creator.
    
    Args:
        channel_metrics: Your channel's metrics
        creator_name: Name of creator to compare ('MrBeast', 'MKBHD', etc.)
    
    Returns:
        dict: Detailed comparison
    """
    creators = {
        'MrBeast': MRBEAST_DATA,
        'IShowSpeed': ISHOWSPEED_DATA,
        'MKBHD': MKBHD_DATA
    }
    
    if creator_name not in creators:
        return {'error': f'Unknown creator: {creator_name}'}
    
    creator = creators[creator_name]
    
    comparison = {
        'your_channel': channel_metrics,
        'compared_to': creator_name,
        'metrics_comparison': {}
    }
    
    # Compare each metric
    metrics_to_compare = ['subscribers', 'engagement_rate', 'avg_views_per_video']
    
    for metric in metrics_to_compare:
        your_value = channel_metrics.get(metric, 0)
        their_value = creator.get(metric, 0)
        
        if their_value > 0:
            percentage = (your_value / their_value) * 100
            comparison['metrics_comparison'][metric] = {
                'your_value': your_value,
                'their_value': their_value,
                'percentage_of_theirs': f"{percentage:.2f}%",
                'gap': their_value - your_value
            }
    
    return comparison
