
import os
import sys
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from src.database import get_db_session
from src.database.models import (
    YouTubeChannel, YouTubeVideo, YouTubeChannelSnapshot, 
    InstagramAccount, InstagramPost, InstagramAccountSnapshot,
    YouTubeComment
)

def seed_comprehensive_data():
    print("🚀 Seeding comprehensive real-world data...")
    
    with get_db_session() as session:
        # Clear existing data (optional, but cleaner)
        # session.query(YouTubeVideo).delete()
        # session.query(YouTubeChannel).delete()
        # session.query(InstagramPost).delete()
        # session.query(InstagramAccount).delete()
        
        # --- 1. YouTube Channels ---
        channels = [
            {
                "id": "UCBJycsmduvYELg8Ga73Wnsw", "title": "Marques Brownlee", "desc": "Quality Tech Videos",
                "subs": 19400000, "views": 4010000000, "vids": 1645, "handle": "@mkbhd",
                "thumb": "https://yt3.googleusercontent.com/lkH3xt8ZhmVMduU6PROreS198v02aYocS79_0m9hS66fRA-I9unf9EIDb5cl97-UvSra5s_X_w=s176-c-k-c0x00ffffff-no-rj"
            },
            {
                "id": "UCX6OQ3DkcsbYNE6H8uQQuVA", "title": "MrBeast", "desc": "I do crazy stuff",
                "subs": 252000000, "views": 47000000000, "vids": 803, "handle": "@mrbeast",
                "thumb": "https://yt3.googleusercontent.com/fxG_Z3Rf_zAtSsb9_B7_YyW6uK_x_T2l3p8_wscKzI9m7vI_1e7h7n3p4c3p4c3p=s176"
            },
           {
                "id": "UC-lHJZR3Gqxm24_Vd_AJ5Yw", "title": "PewDiePie", "desc": "Gaming and memes",
                "subs": 111000000, "views": 29000000000, "vids": 4700, "handle": "@pewdiepie",
                "thumb": "https://yt3.googleusercontent.com/5oUY3tC5OdqCW22xHyUPD8lNO603cf-L_hu3KWMBXS3rJf9nC1BN8kLFqBd9H-yKeG-t88f1=s176-c-k-c0x00ffffff-no-rj"
            },
             {
                "id": "UCo_q6aOlvPH7M-j_XGWVgXg", "title": "Veritasium", "desc": "Science and engineering videos",
                "subs": 14500000, "views": 2100000000, "vids": 380, "handle": "@veritasium",
                "thumb": "https://yt3.googleusercontent.com/ytc/AIdro_k2A0yT5l3lA0l3lA0l3l_A0l3l=s176-c-k-c0x00ffffff-no-rj"
            },
            {
                "id": "UCWIzUBWkFnivohkXCXiWdbA", "title": "IShowSpeed", "desc": "Gaming and streaming",
                "subs": 24000000, "views": 2500000000, "vids": 1300, "handle": "@ishowspeed",
                "thumb": "https://yt3.googleusercontent.com/ytc/AIdro_k2A0yT5l3lA0l3lA0l3l_A0l3l=s176-c-k-c0x00ffffff-no-rj"
            },
            {
                "id": "UCVtFOytbRp7yKS6MroMYtHG", "title": "KSI", "desc": "Music, Boxing, Gaming",
                "subs": 24100000, "views": 6000000000, "vids": 1200, "handle": "@ksi",
                "thumb": "https://yt3.googleusercontent.com/ytc/AIdro_k2A0yT5l3lA0l3lA0l3l_A0l3l=s176-c-k-c0x00ffffff-no-rj"
            }
        ]

        for c_data in channels:
            channel = session.query(YouTubeChannel).filter_by(channel_id=c_data['id']).first()
            if not channel:
                channel = YouTubeChannel(
                    channel_id=c_data['id'],
                    title=c_data['title'],
                    description=c_data['desc'],
                    subscribers=c_data['subs'],
                    total_views=c_data['views'],
                    total_videos=c_data['vids'],
                    custom_url=c_data['handle'],
                    thumbnail_url=c_data['thumb']
                )
                session.add(channel)
            else:
                 # Update existing
                channel.subscribers = c_data['subs']
                channel.total_views = c_data['views']
                channel.total_videos = c_data['vids']
            
            session.flush()

            # Generate Growth History (30 days)
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=30-i)
                # Create slightly noisy linear growth
                daily_sub_gain = random.randint(1000, 50000) if c_data['subs'] > 100000000 else random.randint(500, 10000)
                sub_hist = int(c_data['subs'] - (daily_sub_gain * (30-i)))
                view_hist = int(c_data['views'] - (daily_sub_gain * 100 * (30-i)))
                
                snap = YouTubeChannelSnapshot(
                    channel_id=c_data['id'],
                    snapshot_date=date,
                    subscribers=sub_hist,
                    total_views=view_hist,
                    total_videos=c_data['vids'] - (1 if i < 25 else 0),
                    subscribers_delta=daily_sub_gain,
                    views_delta=daily_sub_gain * 100
                )
                session.add(snap)

            # Generate Videos (15 per channel)
            topics = ["Tech", "Gaming", "Vlog", "Challenge", "Science", "Review", "Tutorial", "News"]
            # Realish thumbnails for demo
            thumbs = [
                "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg",
                "https://i.ytimg.com/vi/jNQXAC9IVRw/mqdefault.jpg",
                "https://i.ytimg.com/vi/9bZkp7q19f0/mqdefault.jpg",
                "https://i.ytimg.com/vi/kJQP7kiw5Fk/mqdefault.jpg",
                "https://i.ytimg.com/vi/fH7d6XX0j4s/mqdefault.jpg"
            ]
            
            for v_i in range(15):
                views_base = c_data['subs'] * random.uniform(0.1, 0.5) if v_i == 0 else c_data['subs'] * random.uniform(0.01, 0.2)
                views = int(views_base)
                comments = int(views * random.uniform(0.001, 0.005))
                likes = int(views * random.uniform(0.04, 0.10))
                
                vid_date = datetime.utcnow() - timedelta(days=random.randint(0, 60))
                
                video = YouTubeVideo(
                    video_id=f"{c_data['id']}_v{v_i}",
                    channel_id=c_data['id'],
                    title=f"{random.choice(['Ultimate', 'Crazy', 'Best', 'Why I', 'How to'])} {random.choice(topics)} {random.choice(['Moment', 'Review', 'Challenge', 'Explained', '2024'])} #{v_i+1}",
                    description="This is a generated video description.",
                    views=views,
                    likes=likes,
                    comments=comments,
                    engagement_rate=round((likes+comments)/views, 4) if views > 0 else 0,
                    published_at=vid_date,
                    tags=[random.choice(topics) for _ in range(3)],
                    duration_seconds=random.randint(300, 1800),
                    thumbnail_url=thumbs[v_i % len(thumbs)]
                )
                # Check exist
                exist_vid = session.query(YouTubeVideo).filter_by(video_id=video.video_id).first()
                if not exist_vid:
                    session.add(video)
                    session.flush()
                    
                    # Add dummy comments for sentiment analysis
                    sentiments = ["Amazing video!", "Very helpful, thanks!", "I don't like this approach.", "Interesting, but could be shorter.", "WOW!", "Best creator ever.", "Meh.", "Can you do a review of the new iPhone?"]
                    for c_i in range(10):
                        comment = YouTubeComment(
                            comment_id=f"comm_{video.video_id}_{c_i}",
                            video_id=video.video_id,
                            text=random.choice(sentiments) + f" (Comment {c_i})",
                            author=f"Viewer_{random.randint(1,1000)}",
                            published_at=vid_date + timedelta(hours=c_i)
                        )
                        session.add(comment)

        # --- 2. Instagram Accounts ---
        accounts = [
             {
                "id": "17841400000000001", "user": "cristiano", "name": "Cristiano Ronaldo",
                "fol": 622000000, "med": 3640,
                "pic": "https://instagram.fccu1-1.fna.fbcdn.net/v/t51.2885-19/..."
            },
            {
                "id": "17841400000000002", "user": "nike", "name": "Nike",
                "fol": 306000000, "med": 1020,
                "pic": "https://instagram.fccu1-1.fna.fbcdn.net/v/t51.2885-19/..."
            },
             {
                "id": "17841400000000003", "user": "natgeo", "name": "National Geographic",
                "fol": 283000000, "med": 29000,
                "pic": "https://instagram.fccu1-1.fna.fbcdn.net/v/t51.2885-19/..."
            },
            {
                "id": "17841400000000004", "user": "ishowspeed", "name": "IShowSpeed",
                "fol": 16000000, "med": 150,
                "pic": "https://instagram.fccu1-1.fna.fbcdn.net/v/t51.2885-19/..."
            },
            {
                "id": "17841400000000005", "user": "ksi", "name": "KSI",
                "fol": 13200000, "med": 1800,
                "pic": "https://instagram.fccu1-1.fna.fbcdn.net/v/t51.2885-19/..."
            }
        ]

        for a_data in accounts:
            account = session.query(InstagramAccount).filter_by(instagram_id=a_data['id']).first()
            if not account:
                account = InstagramAccount(
                    instagram_id=a_data['id'],
                    username=a_data['user'],
                    name=a_data['name'],
                    followers_count=a_data['fol'],
                    follows_count=random.randint(100, 1000),
                    media_count=a_data['med'],
                    profile_picture_url=a_data['pic']
                )
                session.add(account)
            session.flush()

             # Generate Posts (12 per account)
            ig_images = [
                "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                "https://images.unsplash.com/photo-1517544152467-1dc0097270be?w=500",
                "https://images.unsplash.com/photo-1505764775204-581ce8198bbd?w=500",
                "https://images.unsplash.com/photo-1523995462485-3d171b5c8fa9?w=500"
            ]
            
            for p_i in range(12):
                likes = int(a_data['fol'] * random.uniform(0.01, 0.05))
                comms = int(likes * random.uniform(0.005, 0.02))
                
                post = InstagramPost(
                    post_id=f"ig_{a_data['id']}_p{p_i}",
                    instagram_id=a_data['id'],
                    caption=f"Amazing shot from today! #{a_data['user']} #viral #{random.choice(['love', 'life', 'sports', 'nature'])}",
                    media_type="IMAGE" if random.random() > 0.3 else "VIDEO",
                    media_url=ig_images[p_i % len(ig_images)],
                    permalink=f"https://instagram.com/p/{p_i}",
                    like_count=likes,
                    comments_count=comms,
                    timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                
                exist_post = session.query(InstagramPost).filter_by(post_id=post.post_id).first()
                if not exist_post:
                    session.add(post)

        print("✅ Comprehensive data seeded successfully.")

if __name__ == "__main__":
    seed_comprehensive_data()
