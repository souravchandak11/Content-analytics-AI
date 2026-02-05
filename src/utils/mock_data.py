
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# High-quality, reliable image URLs
YOUTUBE_THUMBNAILS = [
    "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=225&fit=crop",  # Tech
    "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=400&h=225&fit=crop",  # Gaming
    "https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=400&h=225&fit=crop",  # Music
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=400&h=225&fit=crop",  # Coding
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400&h=225&fit=crop",  # Business
    "https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?w=400&h=225&fit=crop",  # Sports
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=225&fit=crop",  # Robot/AI
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&h=225&fit=crop",  # Analytics
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=225&fit=crop",  # Dashboard
    "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400&h=225&fit=crop",  # Creative
]

INSTAGRAM_THUMBNAILS = [
    "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=400&h=400&fit=crop",  # Portrait
    "https://images.unsplash.com/photo-1523264766585-fb5deca88dfc?w=400&h=400&fit=crop",  # Nature
    "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&h=400&fit=crop",  # Food
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop",  # Fashion
    "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=400&fit=crop",  # Travel
    "https://images.unsplash.com/photo-1530047198215-f89ae2d4e6d5?w=400&h=400&fit=crop",  # Fitness
    "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=400&h=400&fit=crop",  # Shopping
    "https://images.unsplash.com/photo-1588392382834-a891154bca4d?w=400&h=400&fit=crop",  # Nature
]

def generate_mock_youtube_data(num_videos=20):
    """
    Generate fake YouTube video data.
    
    Args:
        num_videos (int): Number of mock videos to generate
        
    Returns:
        list: List of dictionaries containing video data
    """
    videos = []
    topics = ['Tech', 'Gaming', 'Vlog', 'Tutorial', 'Review', 'Comedy', 'Education']
    
    video_titles = [
        "How I Made $1M in 24 Hours",
        "This Changed Everything About My Life",
        "The Most Insane Challenge Ever",
        "You Won't Believe What Happened Next",
        "Ultimate Guide to Going Viral",
        "I Spent 100 Days Learning This",
        "First Time Trying This Challenge",
        "The Truth About Social Media",
        "Behind The Scenes of My Content",
        "React to Viral TikToks",
    ]
    
    for i in range(num_videos):
        published_at = fake.date_time_between(start_date='-1y', end_date='now')
        views = random.randint(10000, 5000000)
        likes = int(views * random.uniform(0.03, 0.08))
        comments = int(views * random.uniform(0.002, 0.01))
        
        video = {
            'video_id': f'YT_{uuid.uuid4().hex[:11]}',
            'title': random.choice(video_titles) + f" #{i+1}",
            'description': fake.paragraph(nb_sentences=3),
            'views': views,
            'likes': likes,
            'comments': comments,
            'published_at': published_at.isoformat() + "Z",
            'duration_seconds': random.randint(180, 1200),
            'thumbnail_url': YOUTUBE_THUMBNAILS[i % len(YOUTUBE_THUMBNAILS)],
            'tags': [random.choice(topics) for _ in range(3)],
            'category_id': str(random.randint(1, 40)),
            'engagement_rate': round((likes + comments) / views, 4) if views > 0 else 0
        }
        videos.append(video)
        
    return videos

def generate_mock_instagram_data(num_posts=20):
    """
    Generate fake Instagram post data.
    
    Args:
        num_posts (int): Number of mock posts to generate
        
    Returns:
        list: List of dictionaries containing post data
    """
    posts = []
    
    captions = [
        "Living my best life ✨",
        "New content alert! 🔥",
        "Behind the scenes 📸",
        "Can't stop, won't stop 💪",
        "Making memories 🌟",
        "Grateful for this journey 🙏",
        "Dream big, work hard 💫",
        "Vibes only ✌️",
    ]
    
    for i in range(num_posts):
        timestamp = fake.date_time_between(start_date='-1y', end_date='now')
        like_count = random.randint(1000, 100000)
        comments_count = int(like_count * random.uniform(0.01, 0.05))
        
        post = {
            'id': f'IG_{uuid.uuid4().hex[:11]}',
            'post_id': f'IG_{uuid.uuid4().hex[:11]}',
            'caption': random.choice(captions) + " " + " ".join([f"#{fake.word()}" for _ in range(3)]),
            'like_count': like_count,
            'comments_count': comments_count,
            'media_url': INSTAGRAM_THUMBNAILS[i % len(INSTAGRAM_THUMBNAILS)],
            'media_type': random.choice(['IMAGE', 'VIDEO', 'CAROUSEL_ALBUM']),
            'permalink': f"https://instagram.com/p/{uuid.uuid4().hex[:11]}/",
            'timestamp': timestamp.isoformat() + "Z",
            'thumbnail_url': INSTAGRAM_THUMBNAILS[i % len(INSTAGRAM_THUMBNAILS)]
        }
        posts.append(post)
        
    return posts
