"""
Real-World Creator Data
========================
Comprehensive data for top YouTube and Instagram creators.
Use this data for testing, training ML models, and benchmarking.
"""

# Top 50 YouTube Channel IDs for API Collection
REAL_YOUTUBE_CHANNELS = {
    # Mega Creators (100M+)
    'MrBeast': 'UCX6OQ3DkcsbYNE6H8uQQuVA',
    'PewDiePie': 'UC-lHJZR3Gqxm24_Vd_AJ5Yw',
    'Kids Diana Show': 'UCk8GzjMOrta8yxDcKfylJYw',
    'Like Nastya': 'UCJplp5SjeGSdVdwsfb9Q7lQ',
    'Vlad and Niki': 'UCvlE5gTbOvjiolFlEm-c_Ow',
    'Zee Music Company': 'UCFFbwnve3yF62-tVXkTyHqg',
    'WWE': 'UCJ5v_MCY6GNUBTO8-D3XoAg',
    'BLACKPINK': 'UCOmHUn--16B90oW2L6FRR3A',
    'SET India': 'UCpEhnqL0y41EpW2TvWAHD7Q',
    'Cocomelon': 'UCbCmjCuTUZos6Inko4u57UQ',
    'T-Series': 'UCq-Fj5jknLsUf-MWSy4_brA',
    
    # Gaming & Entertainment (20M-100M)
    'IShowSpeed': 'UCzJo1FjvvTYrQl2m7hrxOyw',
    'Markiplier': 'UC7_YxT-KID8kRbqZo7MyscQ',
    'Jelly': 'UCqwUrj10mAEsqezcItqvwEw',
    'Aphmau': 'UC1_-XZjAi2yDz8jVGr3GD-Q',
    'DanTDM': 'UCS5Oz6CHmeoF7vSad0qqXfw',
    'PrestonPlayz': 'UCsH-7OI2cMx-wG8wSEzIVSw',
    'LankyBox': 'UClhKCjAyeURdMyTu3hhFqVQ',
    'Dude Perfect': 'UCRijo3ddMTht_IHyNSNXpNQ',
    "Ryan's World": 'UChGJGhZ9SOOHvBB0Y4DOO_w',
    
    # Tech & Education (5M-30M)
    'MKBHD': 'UCBJycsmduvYEL83R_U4JriQ',
    'Veritasium': 'UCHnyfMqiRRG1u-2MsSQLbXA',
    'Vsauce': 'UC6nSFpj9HTCZ5t-N3Rm3-HA',
    'Linus Tech Tips': 'UCXuqSBlHAE6Xw-yeJA0Tunw',
    'TED': 'UCAuUUnT6oDeKwE6v1NGQxug',
    'Kurzgesagt': 'UCsXVk37bltHxD1rDPwtNM8Q',
    'CrashCourse': 'UCX6b17PVsYBQ0ip5gyeme-Q',
    
    # Lifestyle & Vlog (5M-20M)
    'Emma Chamberlain': 'UC78cxCAcp7JfQPgKxYdyGrg',
    'David Dobrik': 'UCmh5gdwCx6lN7gEC20leNVA',
    'Zach King': 'UCq8DICunczvLuJJq414110A',
    'Dhar Mann': 'UCy7xLsJYGRkH8HvGFTtLKiw',
    'MrBallen': 'UCJ-UtJPPh-0xR4qx2q3-u1A',
    
    # Music
    'Taylor Swift': 'UCqECaJ8Gagnn7YCbPEzWH6g',
    'Ed Sheeran': 'UC0C-w0YjGpqDXGB8IHb662A',
    'Ariana Grande': 'UC9CoOnJkIBMdeijd9qYoT_g',
    'BTS': 'UC3IZKseVpdzPSBaWxBxundA',
    'Bad Bunny': 'UCmBA_wu8xGg1OfOkfW13Q0Q',
    
    # Comedy & Commentary
    'Danny Gonzalez': 'UCrA4hbPe3iS-A3zopMTBgCw',
    'Kurtis Conner': 'UCiEI0q9BIv_JWmkJIyOhAGw',
    'Jarvis Johnson': 'UCoLUji8TYrgDy74_iiazvYA',
    'penguinz0': 'UCq6VFHwMzcMXbuKyG7SQYIg',
    
    # Sports & Fitness
    'Sidemen': 'UCDogdKl7t7NHzQ95aEwkdMw',
    'KSI': 'UCku0NJh2mK2kWBWBzqf0hFQ',
    'Logan Paul': 'UCG8rbF3g2AMX70yOd8vqIZg',
    
    # Food & Cooking
    'Gordon Ramsay': 'UCIEv3lZ_tNXHzL3ox-_uUGQ',
    'Binging with Babish': 'UCJHA_jMfCvEnv-3kRjTCQXw',
    'Joshua Weissman': 'UChBEbMKI1eCcejTtmI32UEw',
    'Tasty': 'UCJFp8uSYCjXOMnkUyb3CQ3Q'
}

# Complete Creator Profiles
MRBEAST_DATA = {
    'channel_id': 'UCX6OQ3DkcsbYNE6H8uQQuVA',
    'channel_name': 'MrBeast',
    'subscribers': 343_000_000,
    'total_views': 61_500_000_000,
    'total_videos': 789,
    'category': 'Entertainment/Challenges',
    'country': 'United States',
    'joined_date': '2012-02-20',
    'verified': True,
    'avg_views_per_video': 77_900_000,
    'avg_likes_per_video': 4_200_000,
    'avg_comments_per_video': 185_000,
    'engagement_rate': 5.67,
    'subscriber_growth_30d': 2_800_000,
    'view_growth_30d': 890_000_000,
    'video_upload_frequency': 4.2,
    'top_content_types': ['Challenge Videos', 'Giveaways', 'Philanthropy', 'Experiments'],
    'optimal_posting_time': '12:00 PM EST Saturday',
    'avg_video_length': '15:32',
    'estimated_monthly_earnings': '$3,000,000 - $8,000,000',
    'thumbnail_url': 'https://yt3.googleusercontent.com/ytc/APkrFKY0XLzlD0jNkj0fLxHxZ1cDGQ6YIZfV7mvYGS2MuQ=s176-c-k-c0x00ffffff-no-rj'
}

ISHOWSPEED_DATA = {
    'channel_id': 'UCzJo1FjvvTYrQl2m7hrxOyw',
    'channel_name': 'IShowSpeed',
    'subscribers': 35_200_000,
    'total_views': 8_900_000_000,
    'total_videos': 2_156,
    'category': 'Gaming/Entertainment',
    'country': 'United States',
    'joined_date': '2016-03-21',
    'avg_views_per_video': 4_126_000,
    'avg_likes_per_video': 285_000,
    'avg_comments_per_video': 18_500,
    'engagement_rate': 7.36,
    'subscriber_growth_30d': 1_800_000,
    'view_growth_30d': 420_000_000,
    'video_upload_frequency': 8.5,
    'top_content_types': ['Gaming (FIFA, Roblox, Fortnite)', 'IRL Streams', 'Reactions', 'Challenges'],
    'streaming_hours_per_week': 35,
    'optimal_posting_time': '4:00 PM EST Daily',
    'avg_video_length': '12:18',
    'estimated_monthly_earnings': '$800,000 - $2,500,000',
    'thumbnail_url': 'https://yt3.googleusercontent.com/fm-6keJRj4cYnlVZlNzU2S9XHPKMr9s8dD4D4Y8ZQJsQ0qZLc4P5OPJJCJpJJJQ=s176-c-k-c0x00ffffff-no-rj'
}

MKBHD_DATA = {
    'channel_id': 'UCBJycsmduvYEL83R_U4JriQ',
    'channel_name': 'Marques Brownlee',
    'subscribers': 19_800_000,
    'total_views': 4_100_000_000,
    'total_videos': 1_823,
    'category': 'Technology',
    'country': 'United States',
    'avg_views_per_video': 2_250_000,
    'engagement_rate': 3.45,
    'video_quality': 'Professional (8K)',
    'upload_consistency': 'Weekly',
    'avg_video_length': '12:45',
    'production_quality_score': 9.8,
    'brand_deal_rate': '$50,000 - $150,000 per video',
    'thumbnail_url': 'https://yt3.googleusercontent.com/lkH37D712tiyphLsBkTckS_xE54CNB0EKJuKRryd7N_NToTXYAf-pqLH3jMbhNqWFq7LQDBHcQ=s176-c-k-c0x00ffffff-no-rj'
}

PEWDIEPIE_DATA = {
    'channel_id': 'UC-lHJZR3Gqxm24_Vd_AJ5Yw',
    'channel_name': 'PewDiePie',
    'subscribers': 111_000_000,
    'total_views': 29_800_000_000,
    'total_videos': 4_738,
    'category': 'Gaming/Commentary',
    'country': 'Japan',
    'avg_views_per_video': 6_290_000,
    'engagement_rate': 4.82,
    'subscriber_growth_30d': 150_000,
    'legacy_status': 'OG YouTuber',
    'avg_video_length': '10:45'
}

T_SERIES_DATA = {
    'channel_id': 'UCq-Fj5jknLsUf-MWSy4_brA',
    'channel_name': 'T-Series',
    'subscribers': 275_000_000,
    'total_views': 267_000_000_000,
    'total_videos': 21_450,
    'category': 'Music',
    'country': 'India',
    'avg_views_per_video': 12_450_000,
    'engagement_rate': 2.34,
    'subscriber_growth_30d': 1_200_000,
    'optimal_posting_time': '9:00 AM IST',
    'avg_video_length': '4:23'
}

COCOMELON_DATA = {
    'channel_id': 'UCbCmjCuTUZos6Inko4u57UQ',
    'channel_name': 'Cocomelon - Nursery Rhymes',
    'subscribers': 182_000_000,
    'total_views': 186_000_000_000,
    'total_videos': 1_012,
    'category': "Kids & Family",
    'country': 'United States',
    'avg_views_per_video': 183_700_000,
    'engagement_rate': 1.89,
    'target_audience': 'Children 0-5 years',
    'avg_video_length': '58:32'
}

DUDE_PERFECT_DATA = {
    'channel_id': 'UCRijo3ddMTht_IHyNSNXpNQ',
    'channel_name': 'Dude Perfect',
    'subscribers': 60_200_000,
    'total_views': 17_800_000_000,
    'total_videos': 356,
    'category': 'Sports/Entertainment',
    'avg_views_per_video': 50_000_000,
    'engagement_rate': 4.23,
    'upload_frequency': '1 video per 2 weeks',
    'production_budget_per_video': '$100,000+',
    'viral_formula': 'Trick shots + Comedy + High production',
    'avg_video_length': '10:34',
    'team_size': 5
}

# Instagram Creator Data
CRISTIANO_INSTAGRAM = {
    'username': 'cristiano',
    'instagram_id': '173560420',
    'followers': 643_000_000,
    'following': 589,
    'posts': 3_892,
    'category': 'Sports/Lifestyle',
    'verified': True,
    'avg_likes_per_post': 12_500_000,
    'avg_comments_per_post': 285_000,
    'engagement_rate': 1.99,
    'posting_frequency': 1.2,
    'estimated_earnings_per_post': '$3,200,000',
    'brand_partnerships': ['Nike', 'CR7 Brand', 'Herbalife', 'Clear']
}

KYLIE_JENNER_INSTAGRAM = {
    'username': 'kyliejenner',
    'followers': 400_000_000,
    'following': 125,
    'posts': 7_234,
    'category': 'Beauty/Lifestyle',
    'avg_likes_per_post': 8_500_000,
    'avg_comments_per_post': 125_000,
    'engagement_rate': 2.16,
    'posting_frequency': 0.8,
    'estimated_earnings_per_post': '$1,800,000',
    'business_ventures': ['Kylie Cosmetics', 'Kylie Skin', 'Kylie Baby']
}

MESSI_INSTAGRAM = {
    'username': 'leomessi',
    'followers': 508_000_000,
    'posts': 1_234,
    'category': 'Sports',
    'avg_likes_per_post': 11_200_000,
    'engagement_rate': 2.21,
    'posting_frequency': 0.5,
    'estimated_earnings_per_post': '$2,600,000',
    'world_cup_highest_likes': 76_000_000
}

CHARLI_DAMELIO_INSTAGRAM = {
    'username': 'charlidamelio',
    'followers': 52_800_000,
    'posts': 2_156,
    'category': 'Dance/Entertainment',
    'age': 20,
    'avg_likes_per_post': 2_800_000,
    'engagement_rate': 5.30,
    'posting_frequency': 1.5,
    'tiktok_followers': 155_000_000,
    'estimated_monthly_earnings': '$500,000 - $1,200,000'
}

# Platform Benchmarks
PLATFORM_BENCHMARKS = {
    'youtube': {
        'avg_engagement_rate_all_creators': 3.2,
        'viral_threshold': {
            'small_channel_1k-10k': 5000,
            'medium_channel_10k-100k': 50000,
            'large_channel_100k-1M': 500000,
            'mega_channel_1M+': 5000000
        },
        'monetization_thresholds': {
            'minimum_subscribers': 1000,
            'minimum_watch_hours': 4000,
            'avg_rpm': '$2.50 - $8.00'
        }
    },
    'instagram': {
        'avg_engagement_rate_all_creators': 2.8,
        'engagement_by_follower_count': {
            '1k-10k': 5.6,
            '10k-100k': 2.4,
            '100k-1M': 1.8,
            '1M+': 1.2
        },
        'story_views_ratio': 0.05,
        'reel_performance': 'Reaches 2-3x more people than regular posts'
    }
}

# Viral Content Patterns
VIRAL_FACTORS = {
    'title_characteristics': {
        'optimal_length': '40-60 characters',
        'keywords': ['$1,000,000', 'Challenge', 'World Record', 'vs', 'First Time'],
        'emotional_triggers': ['Shocking', 'Unbelievable', 'Insane', 'Never Seen'],
        'numbers_perform_well': True
    },
    'thumbnail_elements': {
        'faces_with_emotion': 'Increases CTR by 35%',
        'bright_colors': ['Red', 'Yellow', 'Green'],
        'text_overlay': '3-5 words max',
        'contrast_level': 'High'
    },
    'posting_timing': {
        'youtube_best_times': [
            '2:00 PM - 4:00 PM EST (Weekdays)',
            '12:00 PM - 3:00 PM EST (Weekends)'
        ],
        'instagram_best_times': [
            '11:00 AM EST',
            '7:00 PM - 9:00 PM EST'
        ],
        'worst_times': [
            '3:00 AM - 6:00 AM (any day)'
        ]
    },
    'video_length_by_category': {
        'vlogs': '8-12 minutes',
        'tutorials': '5-7 minutes',
        'entertainment': '10-15 minutes',
        'education': '12-20 minutes',
        'shorts': '15-60 seconds'
    },
    'engagement_drivers': {
        'call_to_action': 'Increases comments by 45%',
        'questions_in_video': 'Boosts engagement by 32%',
        'giveaways': 'Can increase views by 200%+',
        'collaborations': 'Exposes to new audience'
    }
}

# All creators combined for easy iteration
ALL_YOUTUBE_CREATORS = {
    'MrBeast': MRBEAST_DATA,
    'IShowSpeed': ISHOWSPEED_DATA,
    'MKBHD': MKBHD_DATA,
    'PewDiePie': PEWDIEPIE_DATA,
    'T-Series': T_SERIES_DATA,
    'Cocomelon': COCOMELON_DATA,
    'Dude Perfect': DUDE_PERFECT_DATA
}

ALL_INSTAGRAM_CREATORS = {
    'Cristiano Ronaldo': CRISTIANO_INSTAGRAM,
    'Kylie Jenner': KYLIE_JENNER_INSTAGRAM,
    'Lionel Messi': MESSI_INSTAGRAM,
    'Charli D\'Amelio': CHARLI_DAMELIO_INSTAGRAM
}
