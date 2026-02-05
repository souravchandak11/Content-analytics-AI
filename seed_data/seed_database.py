"""
Database Seeding Script
=======================
Seeds the database with real-world creator data for testing and demos.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from seed_data.real_world_creators import (
    MRBEAST_DATA, ISHOWSPEED_DATA, MKBHD_DATA,
    PEWDIEPIE_DATA, DUDE_PERFECT_DATA
)


def generate_mrbeast_videos():
    """Generate realistic MrBeast video data"""
    video_titles = [
        '$1 vs $1,000,000 Hotel Room',
        'I Built 100 Houses And Gave Them Away',
        'I Spent 7 Days In Solitary Confinement',
        '$1 vs $100,000 Airplane Ticket',
        'I Ate The World\'s Largest Pizza',
        'Last To Leave Circle Wins $500,000',
        'I Survived 50 Hours In Antarctica',
        'I Opened A Free Car Dealership',
        'World\'s Most Dangerous Trap',
        '$456,000 Squid Game In Real Life',
        'I Gave My 100,000,000th Subscriber An Island',
        'Lamborghini vs World\'s Largest Shredder',
        'I Spent 24 Hours Straight In Slime',
        '$1 vs $250,000 Vacation!',
        'Ages 1 - 100 Fight For $500,000',
        'Every Country On Earth Fights For $250,000',
        'I Survived 100 Days In A Nuclear Bunker',
        'World\'s Deadliest Laser Maze',
        '$1 vs $1,000,000,000 Yacht',
        'I Built The World\'s Longest Bridge'
    ]
    
    videos = []
    for idx, title in enumerate(video_titles):
        base_views = random.randint(70_000_000, 180_000_000)
        
        video = {
            'video_id': f'MRBEAST_VID_{idx:03d}',
            'channel_id': 'UCX6OQ3DkcsbYNE6H8uQQuVA',
            'title': title,
            'description': f'{title} - Another incredible MrBeast challenge!',
            'published_at': datetime.now() - timedelta(days=random.randint(7, 365)),
            'duration': f'PT{random.randint(12, 22)}M{random.randint(10, 59)}S',
            'views': base_views,
            'likes': int(base_views * random.uniform(0.05, 0.07)),
            'comments': int(base_views * random.uniform(0.002, 0.003)),
            'thumbnail_url': f'https://i.ytimg.com/vi/MRBEAST_VID_{idx:03d}/maxresdefault.jpg',
            'tags': ['MrBeast', 'Challenge', 'Giveaway', 'Entertainment']
        }
        videos.append(video)
    
    return videos


def generate_ishowspeed_videos():
    """Generate realistic IShowSpeed video data"""
    video_titles = [
        'I Met Cristiano Ronaldo',
        'Jumping From A Plane',
        'Playing FIFA 25 for 24 Hours',
        'IShowSpeed Reacts to Messi',
        'Speed Plays Roblox',
        'FORTNITE LIVE STREAM GONE WRONG',
        'Speed House Tour 2025',
        'I Got Banned From FIFA (Again)',
        'Speed Meets Drake',
        'Suiii Challenge in Real Life',
        'Speed Plays GTA 6',
        'Most Insane FIFA Pack Opening Ever',
        'Speed vs KSI Boxing',
        'I Spent $100,000 on FIFA Ultimate Team',
        'Speed\'s Most Viral Moments'
    ]
    
    videos = []
    for idx, title in enumerate(video_titles):
        base_views = random.randint(3_000_000, 50_000_000)
        
        video = {
            'video_id': f'SPEED_VID_{idx:03d}',
            'channel_id': 'UCzJo1FjvvTYrQl2m7hrxOyw',
            'title': title,
            'description': f'{title} - Speed energy only!',
            'published_at': datetime.now() - timedelta(days=random.randint(1, 60)),
            'duration': f'PT{random.randint(8, 18)}M{random.randint(10, 59)}S',
            'views': base_views,
            'likes': int(base_views * random.uniform(0.06, 0.10)),
            'comments': int(base_views * random.uniform(0.003, 0.006)),
            'thumbnail_url': f'https://i.ytimg.com/vi/SPEED_VID_{idx:03d}/maxresdefault.jpg',
            'tags': ['IShowSpeed', 'Gaming', 'Reaction', 'Entertainment']
        }
        videos.append(video)
    
    return videos


def generate_mkbhd_videos():
    """Generate realistic MKBHD video data"""
    video_titles = [
        'iPhone 16 Pro Review: The Real Truth',
        'Tesla Cybertruck: 1 Year Later',
        'M4 MacBook Pro Review',
        'Galaxy S25 Ultra - The Full Picture',
        'The Best Smartphone of 2025',
        'Apple Vision Pro After 1 Year',
        'Why I Left Android for iPhone',
        'The $10,000 Setup Tour',
        'AI Phones Are Here: What You Need to Know',
        'Every Phone I\'ve Ever Used',
        'The Pixel 9 Pro XL Review',
        'Sony Xperia 1 VI: Still Unique'
    ]
    
    videos = []
    for idx, title in enumerate(video_titles):
        base_views = random.randint(2_000_000, 10_000_000)
        
        video = {
            'video_id': f'MKBHD_VID_{idx:03d}',
            'channel_id': 'UCBJycsmduvYEL83R_U4JriQ',
            'title': title,
            'description': f'In-depth tech review: {title}',
            'published_at': datetime.now() - timedelta(days=random.randint(7, 120)),
            'duration': f'PT{random.randint(10, 20)}M{random.randint(10, 59)}S',
            'views': base_views,
            'likes': int(base_views * random.uniform(0.035, 0.055)),
            'comments': int(base_views * random.uniform(0.001, 0.0025)),
            'thumbnail_url': f'https://i.ytimg.com/vi/MKBHD_VID_{idx:03d}/maxresdefault.jpg',
            'tags': ['MKBHD', 'Tech', 'Review', 'Smartphone']
        }
        videos.append(video)
    
    return videos


def generate_monthly_snapshots(channel_data, months=12):
    """Generate monthly historical snapshots for a channel"""
    snapshots = []
    base_subs = int(channel_data['subscribers'] * 0.85)  # Start at 85% of current
    base_views = int(channel_data['total_views'] * 0.80)
    
    for i in range(months):
        growth_factor = 1 + (i * 0.012)  # ~1.2% monthly growth
        
        snapshot = {
            'channel_id': channel_data['channel_id'],
            'subscribers': int(base_subs * growth_factor),
            'total_views': int(base_views * growth_factor),
            'total_videos': channel_data['total_videos'] - (months - i) * 3,
            'snapshot_date': datetime.now() - timedelta(days=30 * (months - i))
        }
        snapshots.append(snapshot)
    
    return snapshots


def seed_database():
    """Seed the database with all creator data"""
    try:
        from src.database import get_db_session, init_database
        from src.database.models import YouTubeChannel, YouTubeVideo, YouTubeChannelSnapshot
        
        # Initialize database
        init_database()
        
        print("\n🌱 Seeding Database with Real Creator Data...")
        print("=" * 60)
        
        with get_db_session() as session:
            # Seed MrBeast
            print("\n📺 Seeding MrBeast data...")
            mrbeast_channel = YouTubeChannel(
                channel_id=MRBEAST_DATA['channel_id'],
                title=MRBEAST_DATA['channel_name'],
                description='Official MrBeast YouTube channel',
                subscribers=MRBEAST_DATA['subscribers'],
                total_views=MRBEAST_DATA['total_views'],
                total_videos=MRBEAST_DATA['total_videos'],
                thumbnail_url=MRBEAST_DATA.get('thumbnail_url', ''),
                country=MRBEAST_DATA['country'],
                published_at=datetime.strptime(MRBEAST_DATA['joined_date'], '%Y-%m-%d')
            )
            session.merge(mrbeast_channel)
            
            for video_data in generate_mrbeast_videos():
                video = YouTubeVideo(**video_data)
                session.merge(video)
            
            for snapshot_data in generate_monthly_snapshots(MRBEAST_DATA):
                snapshot = YouTubeChannelSnapshot(**snapshot_data)
                session.add(snapshot)
            
            print(f"   ✓ Added {len(generate_mrbeast_videos())} videos")
            
            # Seed IShowSpeed
            print("\n📺 Seeding IShowSpeed data...")
            speed_channel = YouTubeChannel(
                channel_id=ISHOWSPEED_DATA['channel_id'],
                title=ISHOWSPEED_DATA['channel_name'],
                description='IShowSpeed - Gaming and Entertainment',
                subscribers=ISHOWSPEED_DATA['subscribers'],
                total_views=ISHOWSPEED_DATA['total_views'],
                total_videos=ISHOWSPEED_DATA['total_videos'],
                thumbnail_url=ISHOWSPEED_DATA.get('thumbnail_url', ''),
                country=ISHOWSPEED_DATA['country'],
                published_at=datetime.strptime(ISHOWSPEED_DATA['joined_date'], '%Y-%m-%d')
            )
            session.merge(speed_channel)
            
            for video_data in generate_ishowspeed_videos():
                video = YouTubeVideo(**video_data)
                session.merge(video)
            
            for snapshot_data in generate_monthly_snapshots(ISHOWSPEED_DATA):
                snapshot = YouTubeChannelSnapshot(**snapshot_data)
                session.add(snapshot)
            
            print(f"   ✓ Added {len(generate_ishowspeed_videos())} videos")
            
            # Seed MKBHD
            print("\n📺 Seeding MKBHD data...")
            mkbhd_channel = YouTubeChannel(
                channel_id=MKBHD_DATA['channel_id'],
                title=MKBHD_DATA['channel_name'],
                description='Quality Tech Videos',
                subscribers=MKBHD_DATA['subscribers'],
                total_views=MKBHD_DATA['total_views'],
                total_videos=MKBHD_DATA['total_videos'],
                thumbnail_url=MKBHD_DATA.get('thumbnail_url', ''),
                country=MKBHD_DATA['country']
            )
            session.merge(mkbhd_channel)
            
            for video_data in generate_mkbhd_videos():
                video = YouTubeVideo(**video_data)
                session.merge(video)
            
            for snapshot_data in generate_monthly_snapshots(MKBHD_DATA):
                snapshot = YouTubeChannelSnapshot(**snapshot_data)
                session.add(snapshot)
            
            print(f"   ✓ Added {len(generate_mkbhd_videos())} videos")
            
            session.commit()
        
        print("\n" + "=" * 60)
        print("✅ Database seeding complete!")
        print("   - 3 channels added")
        print("   - 47 videos added")
        print("   - 36 monthly snapshots added")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"\n⚠️  Database modules not available: {e}")
        print("   Using mock data mode instead.")
        return False
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        return False


def get_sample_data():
    """Get sample data without database for testing"""
    return {
        'channels': [MRBEAST_DATA, ISHOWSPEED_DATA, MKBHD_DATA],
        'mrbeast_videos': generate_mrbeast_videos(),
        'ishowspeed_videos': generate_ishowspeed_videos(),
        'mkbhd_videos': generate_mkbhd_videos()
    }


if __name__ == '__main__':
    seed_database()
