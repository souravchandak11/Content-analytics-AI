
import os
import sys
from datetime import datetime, timedelta
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal, init_db
from src.database.models import (
    YouTubeChannel, YouTubeChannelSnapshot, YouTubeVideo, YouTubeComment,
    InstagramAccount, InstagramAccountSnapshot, InstagramPost
)

def seed_real_world_data():
    """Seed the database with real-world creator data found from the web."""
    print("🚀 Seeding real-world data...")
    
    db = SessionLocal()
    try:
        # 1. YouTube Channels
        channels_data = [
            {
                "channel_id": "UCBJycsmduvYELg82Rl82Y8Q",
                "title": "MKBHD",
                "description": "Marques Brownlee - Quality Tech Videos",
                "subscriber_count": 20700000,
                "view_count": 5200000000,
                "video_count": 1600,
                "videos": [
                    {"video_id": "v1", "title": "What's on my Phone 2026!", "views": 2300000, "likes": 150000, "comments": 8000},
                    {"video_id": "v2", "title": "Smartphone Awards 2025!", "views": 4900000, "likes": 320000, "comments": 12000},
                    {"video_id": "v3", "title": "$1 vs $10,000,000 Futuristic Tech!", "views": 8400000, "likes": 500000, "comments": 25000},
                ]
            },
            {
                "channel_id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
                "title": "MrBeast",
                "description": "I do crazy stuff for charity and fun!",
                "subscriber_count": 465000000,
                "view_count": 110000000000,
                "video_count": 800,
                "videos": [
                    {"video_id": "b1", "title": "50 YouTubers Fight for $1,000,000", "views": 412000000, "likes": 15000000, "comments": 500000},
                    {"video_id": "b2", "title": "Would You Fly to Paris for a Baguette?", "views": 1500000000, "likes": 42000000, "comments": 1200000},
                    {"video_id": "b3", "title": "Survive 30 Days Trapped In The Sky", "views": 137000000, "likes": 8000000, "comments": 400000},
                ]
            }
        ]

        for c_data in channels_data:
            # Create channel
            channel = db.query(YouTubeChannel).filter_by(channel_id=c_data["channel_id"]).first()
            if not channel:
                channel = YouTubeChannel(
                    channel_id=c_data["channel_id"],
                    title=c_data["title"],
                    description=c_data["description"]
                )
                db.add(channel)
                db.flush()

            # Create random snapshots for the last 30 days
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=i)
                # Apply some random variation to subscriber count back in time
                sub_count = c_data["subscriber_count"] - (i * random.randint(1000, 50000))
                views = c_data["view_count"] - (i * random.randint(1000000, 10000000))
                
                snapshot = YouTubeChannelSnapshot(
                    channel_id=c_data["channel_id"],
                    subscriber_count=max(0, sub_count),
                    view_count=max(0, views),
                    video_count=c_data["video_count"],
                    snapshot_date=date
                )
                db.add(snapshot)

            # Add videos
            for v_data in c_data["videos"]:
                video = db.query(YouTubeVideo).filter_by(video_id=v_data["video_id"]).first()
                if not video:
                    video = YouTubeVideo(
                        video_id=v_data["video_id"],
                        channel_id=channel.channel_id,
                        title=v_data["title"],
                        description="",
                        view_count=v_data["views"],
                        like_count=v_data["likes"],
                        comment_count=v_data["comments"],
                        published_at=datetime.utcnow() - timedelta(days=random.randint(1, 100))
                    )
                    db.add(video)
                    db.flush()

                # Add some dummy comments
                comments = [
                    "This is amazing!", "Love the quality of this video.", "Incredible work as always.",
                    "The tech in this is mind-blowing.", "Can't wait for the next one!", "Great insights."
                ]
                for i in range(5):
                    comment_id = f"c_{v_data['video_id']}_{i}"
                    if not db.query(YouTubeComment).filter_by(comment_id=comment_id).first():
                        comment = YouTubeComment(
                            comment_id=comment_id,
                            video_id=video.video_id,
                            author=f"User_{random.randint(1, 1000)}",
                            text=random.choice(comments),
                            like_count=random.randint(0, 1000),
                            sentiment_score=random.uniform(0.5, 1.0),
                            published_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                        )
                        db.add(comment)

        # 2. Instagram Accounts
        insta_data = [
            {
                "account_id": "cr7_1",
                "username": "cristiano",
                "name": "Cristiano Ronaldo",
                "followers": 671000000,
                "media_count": 3998,
                "bio": "Believe. Work hard. Repeat.",
                "posts": [
                    {"post_id": "p1", "caption": "Great win today!", "likes": 12000000, "comments": 80000},
                    {"post_id": "p2", "caption": "Back at training.", "likes": 8000000, "comments": 45000},
                ]
            },
            {
                "account_id": "nike_1",
                "username": "nike",
                "name": "Nike",
                "followers": 298300000,
                "media_count": 943,
                "bio": "Just Do It.",
                "posts": [
                    {"post_id": "n1", "caption": "Move your world.", "likes": 500000, "comments": 5000},
                ]
            }
        ]

        for i_data in insta_data:
            account = db.query(InstagramAccount).filter_by(account_id=i_data["account_id"]).first()
            if not account:
                account = InstagramAccount(
                    account_id=i_data["account_id"],
                    username=i_data["username"],
                    name=i_data["name"],
                    biography=i_data["bio"]
                )
                db.add(account)
                db.flush()

            # Create snapshots
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=i)
                snapshot = InstagramAccountSnapshot(
                    account_id=i_data["account_id"],
                    followers_count=i_data["followers"] - (i * random.randint(5000, 20000)),
                    media_count=i_data["media_count"],
                    snapshot_date=date
                )
                db.add(snapshot)

            # Add posts
            for p_data in i_data["posts"]:
                post = db.query(InstagramPost).filter_by(post_id=p_data["post_id"]).first()
                if not post:
                    post = InstagramPost(
                        post_id=p_data["post_id"],
                        account_id=account.account_id,
                        caption=p_data["caption"],
                        like_count=p_data["likes"],
                        comments_count=p_data["comments"],
                        timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                    )
                    db.add(post)

        db.commit()
        print("✅ Data seeding complete!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_world_data()
