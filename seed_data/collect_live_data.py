"""
Live Data Collection Script
============================
Collect real data from YouTube API using actual channel IDs.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from seed_data.real_world_creators import REAL_YOUTUBE_CHANNELS


def collect_top_creators(max_channels=10, videos_per_channel=10):
    """
    Collect real data from YouTube API for top creators.
    
    Args:
        max_channels: Maximum number of channels to collect
        videos_per_channel: Maximum videos per channel
    
    Returns:
        dict: Collection results
    """
    try:
        from src.api.youtube_client import YouTubeClient
        from src.database import get_db_session
        from src.database.models import YouTubeChannel, YouTubeVideo
    except ImportError as e:
        print(f"⚠️  Required modules not available: {e}")
        return None
    
    youtube = YouTubeClient()
    results = {
        'channels_collected': 0,
        'videos_collected': 0,
        'errors': []
    }
    
    print("\n🎬 Collecting Real YouTube Creator Data...")
    print("=" * 60)
    
    channels_to_collect = list(REAL_YOUTUBE_CHANNELS.items())[:max_channels]
    
    for name, channel_id in channels_to_collect:
        print(f"\n📺 Collecting: {name} ({channel_id})")
        
        try:
            # Get channel stats
            channel_data = youtube.get_channel_stats(channel_id)
            
            if channel_data:
                # Save channel
                with get_db_session() as session:
                    channel = YouTubeChannel(
                        channel_id=channel_id,
                        title=channel_data.get('title', name),
                        description=channel_data.get('description', ''),
                        subscribers=channel_data.get('subscribers', 0),
                        total_views=channel_data.get('total_views', 0),
                        total_videos=channel_data.get('total_videos', 0),
                        thumbnail_url=channel_data.get('thumbnail_url', ''),
                        country=channel_data.get('country', 'Unknown')
                    )
                    session.merge(channel)
                    session.commit()
                
                results['channels_collected'] += 1
                print(f"   ✓ Channel saved: {channel_data.get('subscribers', 0):,} subscribers")
                
                # Get recent videos
                videos = youtube.get_recent_videos(channel_id, max_results=videos_per_channel)
                
                with get_db_session() as session:
                    for video_data in videos:
                        video = YouTubeVideo(
                            video_id=video_data.get('video_id'),
                            channel_id=channel_id,
                            title=video_data.get('title', ''),
                            description=video_data.get('description', ''),
                            views=video_data.get('views', 0),
                            likes=video_data.get('likes', 0),
                            comments=video_data.get('comments', 0),
                            published_at=video_data.get('published_at'),
                            duration=video_data.get('duration', ''),
                            thumbnail_url=video_data.get('thumbnail_url', '')
                        )
                        session.merge(video)
                    session.commit()
                
                results['videos_collected'] += len(videos)
                print(f"   ✓ {len(videos)} videos saved")
                
            else:
                print(f"   ⚠️  Could not fetch channel data")
                results['errors'].append(f"{name}: No data returned")
            
            # Respect API rate limits
            print(f"   📊 Quota used: {youtube.quota_used}/10,000")
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results['errors'].append(f"{name}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 COLLECTION SUMMARY")
    print("=" * 60)
    print(f"Channels collected: {results['channels_collected']}")
    print(f"Videos collected: {results['videos_collected']}")
    
    if results['errors']:
        print(f"\n⚠️  Errors ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   - {error}")
    
    print("=" * 60)
    
    return results


def collect_single_channel(channel_id, videos_count=20):
    """
    Collect data for a single YouTube channel.
    
    Args:
        channel_id: YouTube channel ID
        videos_count: Number of videos to collect
    
    Returns:
        dict: Channel and videos data
    """
    try:
        from src.api.youtube_client import YouTubeClient
        
        youtube = YouTubeClient()
        
        print(f"\n🎬 Collecting data for channel: {channel_id}")
        
        # Get channel
        channel = youtube.get_channel_stats(channel_id)
        if not channel:
            print("❌ Could not fetch channel")
            return None
        
        print(f"✓ Channel: {channel.get('title', 'Unknown')}")
        print(f"  Subscribers: {channel.get('subscribers', 0):,}")
        
        # Get videos
        videos = youtube.get_recent_videos(channel_id, max_results=videos_count)
        print(f"✓ Videos collected: {len(videos)}")
        
        return {
            'channel': channel,
            'videos': videos,
            'quota_used': youtube.quota_used
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Collect YouTube creator data')
    parser.add_argument('--channels', type=int, default=5, help='Number of channels to collect')
    parser.add_argument('--videos', type=int, default=10, help='Videos per channel')
    parser.add_argument('--single', type=str, help='Collect single channel by ID')
    
    args = parser.parse_args()
    
    if args.single:
        result = collect_single_channel(args.single, args.videos)
        if result:
            print(f"\n✅ Collected {len(result['videos'])} videos")
    else:
        collect_top_creators(max_channels=args.channels, videos_per_channel=args.videos)
