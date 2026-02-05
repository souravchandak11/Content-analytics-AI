"""
Seed Data Package
=================
Real-world creator data for testing, ML training, and benchmarking.
"""

from .real_world_creators import (
    REAL_YOUTUBE_CHANNELS,
    MRBEAST_DATA,
    ISHOWSPEED_DATA,
    MKBHD_DATA,
    PEWDIEPIE_DATA,
    T_SERIES_DATA,
    COCOMELON_DATA,
    DUDE_PERFECT_DATA,
    CRISTIANO_INSTAGRAM,
    KYLIE_JENNER_INSTAGRAM,
    MESSI_INSTAGRAM,
    CHARLI_DAMELIO_INSTAGRAM,
    PLATFORM_BENCHMARKS,
    VIRAL_FACTORS,
    ALL_YOUTUBE_CREATORS,
    ALL_INSTAGRAM_CREATORS
)

from .seed_database import (
    seed_database,
    get_sample_data,
    generate_mrbeast_videos,
    generate_ishowspeed_videos,
    generate_mkbhd_videos
)

__all__ = [
    'REAL_YOUTUBE_CHANNELS',
    'MRBEAST_DATA',
    'ISHOWSPEED_DATA',
    'MKBHD_DATA',
    'PEWDIEPIE_DATA',
    'T_SERIES_DATA',
    'COCOMELON_DATA',
    'DUDE_PERFECT_DATA',
    'CRISTIANO_INSTAGRAM',
    'KYLIE_JENNER_INSTAGRAM',
    'MESSI_INSTAGRAM',
    'CHARLI_DAMELIO_INSTAGRAM',
    'PLATFORM_BENCHMARKS',
    'VIRAL_FACTORS',
    'ALL_YOUTUBE_CREATORS',
    'ALL_INSTAGRAM_CREATORS',
    'seed_database',
    'get_sample_data',
    'generate_mrbeast_videos',
    'generate_ishowspeed_videos',
    'generate_mkbhd_videos'
]
