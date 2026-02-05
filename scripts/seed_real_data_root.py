
import os
import sys
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from src.database import get_db_session
from src.database.models import (
    YouTubeChannel, YouTubeVideo, YouTubeChannelSnapshot, 
    InstagramAccount, InstagramPost, InstagramAccountSnapshot
)

def seed_data():
    print("🚀 Seeding real-world data (Root Compatible)...")
    
    with get_db_session() as session:
        # 1. YouTube: MKBHD
        mkbhd = YouTubeChannel(
            channel_id="UCBJycsmduvYELg8Ga73Wnsw",
            title="Marques Brownlee",
            description="Quality Tech Videos",
            subscribers=19400000,
            total_views=4000000000,
            total_videos=1600,
            custom_url="@mkbhd",
            thumbnail_url="https://yt3.googleusercontent.com/lkH3xt8ZhmVMduU6PROreS198v02aYocS79_0m9hS66fRA-I9unf9EIDb5cl97-UvSra5s_X_w=s176-c-k-c0x00ffffff-no-rj"
        )
        session.add(mkbhd)
        
        # 2. YouTube: MrBeast
        mrbeast = YouTubeChannel(
            channel_id="UCX6OQ3DkcsbYNE6H8uQQuVA",
            title="MrBeast",
            description="I do crazy stuff",
            subscribers=240000000,
            total_views=43000000000,
            total_videos=780,
            custom_url="@mrbeast",
            thumbnail_url="https://yt3.googleusercontent.com/fxG_Z3Rf_zAtSsb9_B7_YyW6uK_x_T2l3p8_wscKzI9m7vI_1e7h7n3p4c3p4c3p=s176"
        )
        session.add(mrbeast)
        
        # 3. Instagram: Cristiano Ronaldo
        cr7 = InstagramAccount(
            instagram_id="17841400000000001",
            username="cristiano",
            name="Cristiano Ronaldo",
            followers_count=620000000,
            follows_count=580,
            media_count=3600,
            profile_picture_url="https://instagram.fccu1-1.fna.fbcdn.net/v/t51.2885-19/..."
        )
        session.add(cr7)
        
        # 4. Instagram: Nike
        nike = InstagramAccount(
            instagram_id="17841400000000002",
            username="nike",
            name="Nike",
            followers_count=306000000,
            follows_count=120,
            media_count=1000,
            profile_picture_url="https://instagram.fccu1-1.fna.fbcdn.net/v/t51.2885-19/..."
        )
        session.add(nike)
        
        session.flush() # Ensure parents have IDs
        
        # Add some videos
        v1 = YouTubeVideo(
            video_id="dQw4w9WgXcQ", # Rickroll for fun
            channel_id=mkbhd.channel_id,
            title="What's on my Phone 2026!",
            views=5000000,
            likes=250000,
            comments=15000,
            engagement_rate=0.053,
            published_at=datetime.utcnow() - timedelta(days=2)
        )
        session.add(v1)
        
        v2 = YouTubeVideo(
            video_id="yield_test_1",
            channel_id=mrbeast.channel_id,
            title="50 YouTubers Fight for $1,000,000",
            views=150000000,
            likes=8500000,
            comments=450000,
            engagement_rate=0.06,
            published_at=datetime.utcnow() - timedelta(days=5)
        )
        session.add(v2)
        
        # Add some IG posts
        p1 = InstagramPost(
            post_id="post_cr7_1",
            instagram_id=cr7.instagram_id,
            caption="Great win today! ⚽️",
            like_count=12000000,
            comments_count=85000,
            engagement_rate=0.02,
            timestamp=datetime.utcnow() - timedelta(days=1)
        )
        session.add(p1)
        
        print("✅ Data seeded successfully.")

if __name__ == "__main__":
    seed_data()
