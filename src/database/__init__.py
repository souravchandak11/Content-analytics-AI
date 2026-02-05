"""
Content Analytics Platform - Database Package
=============================================
"""

from .connection import (
    get_session,
    get_db_session,
    get_engine,
    init_database,
    check_database_connection,
    get_database_info,
    cleanup
)

from .models import (
    Base,
    YouTubeChannel,
    YouTubeVideo,
    YouTubeVideoSnapshot,
    YouTubeChannelSnapshot,
    YouTubeComment,
    InstagramAccount,
    InstagramPost,
    InstagramAccountSnapshot,
    MLPrediction,
    ModelMetrics,
    AnalyticsCache
)

__all__ = [
    'get_session',
    'get_db_session',
    'get_engine',
    'init_database',
    'check_database_connection',
    'get_database_info',
    'cleanup',
    'Base',
    'YouTubeChannel',
    'YouTubeVideo',
    'YouTubeVideoSnapshot',
    'YouTubeChannelSnapshot',
    'YouTubeComment',
    'InstagramAccount',
    'InstagramPost',
    'InstagramAccountSnapshot',
    'MLPrediction',
    'ModelMetrics',
    'AnalyticsCache',
]
