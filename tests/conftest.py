"""
Content Analytics Platform - Test Configuration
================================================
"""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_video_data():
    """Sample video data for testing."""
    return {
        'video_id': 'test123',
        'channel_id': 'UC123456',
        'title': 'How to Build an Amazing App! 🚀',
        'description': 'In this tutorial, we build an amazing app step by step.',
        'tags': ['tutorial', 'coding', 'python'],
        'duration_seconds': 600,
        'views': 10000,
        'likes': 500,
        'comments': 50,
        'published_at': '2024-01-15T12:00:00Z'
    }


@pytest.fixture
def sample_channel_data():
    """Sample channel data for testing."""
    return {
        'channel_id': 'UC123456',
        'title': 'Test Channel',
        'description': 'A test YouTube channel',
        'subscribers': 100000,
        'total_views': 5000000,
        'total_videos': 150
    }


@pytest.fixture
def sample_comments():
    """Sample comments for sentiment analysis."""
    return [
        {'text': 'This video is amazing! Great tutorial!'},
        {'text': 'Very helpful, thank you so much!'},
        {'text': 'I dont understand this at all, very confusing'},
        {'text': 'Worst video ever, disliked'},
        {'text': 'Okay video, nothing special'}
    ]
