import sys
import os
import logging
import requests
import json

# Add current directory to path
sys.path.append(os.getcwd())

# Disable logs
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

from src.database import get_db_session
from src.database.queries import YouTubeRepository
from src.database.models import YouTubeChannel, YouTubeVideo

OUTPUT_FILE = "verification_results.txt"

def log(msg):
    print(msg)
    with open(OUTPUT_FILE, "a") as f:
        f.write(msg + "\n")

def check_system():
    # Clear file
    with open(OUTPUT_FILE, "w") as f:
        f.write("System Verification Results\n===========================\n")

    channel_id = None

    # 1. DB Check
    try:
        with get_db_session() as session:
            log("1. Database Check:")
            channels = YouTubeRepository.get_all_channels(session, active_only=False)
            val_channels = len(channels)
            log(f"   - Total Channels: {val_channels}")
            
            if val_channels > 0:
                c = channels[0]
                channel_id = c.channel_id
                log(f"   - Selected Test Channel: {channel_id} ({c.title})")
                
                # Check videos
                videos = YouTubeRepository.get_channel_videos(session, channel_id)
                log(f"   - Videos for Channel: {len(videos)}")
            else:
                log("   - [WARN] No channels found in DB.")

    except Exception as e:
        log(f"   - [ERROR] DB Check Failed: {str(e)}")

    # 2. API Check
    if channel_id:
        log("\n2. API Endpoint Check:")
        base_url = "http://localhost:8000/api"
        
        # Test Recommendations
        try:
            url = f"{base_url}/ai/recommendations/{channel_id}"
            r = requests.get(url)
            log(f"   - GET /ai/recommendations: {r.status_code}")
            if r.status_code != 200:
                log(f"     Response: {r.text}")
        except Exception as e:
            log(f"   - [ERROR] Recommendations failed: {e}")

        # Test Competitor Compare
        try:
            url = f"{base_url}/ai/competitor/compare"
            payload = {
                "your_channel_id": channel_id,
                "competitor_channel_ids": [channel_id] # Compare to self
            }
            r = requests.post(url, json=payload)
            log(f"   - POST /ai/competitor/compare: {r.status_code}")
            if r.status_code != 200:
                log(f"     Response: {r.text}")
        except Exception as e:
            log(f"   - [ERROR] Competitor Compare failed: {e}")
            
    else:
        log("[SKIP] API tests skipped because no channel ID found.")

if __name__ == "__main__":
    check_system()
