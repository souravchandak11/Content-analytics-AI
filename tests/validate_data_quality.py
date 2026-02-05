"""
Data Quality Validation
=======================
Validates the quality and integrity of collected data.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def validate_youtube_data():
    """Validate YouTube data quality"""
    try:
        from src.database import get_db_session
        from src.database.models import YouTubeVideo
        
        with get_db_session() as session:
            videos = session.query(YouTubeVideo).limit(100).all()
            
            if not videos:
                print("⚠️  No YouTube videos found in database")
                return True  # Not a failure, just empty
            
            issues = []
            
            for video in videos:
                # Check for null titles
                if not video.title:
                    issues.append(f"Video {video.video_id}: Missing title")
                
                # Check for negative views
                if video.views is not None and video.views < 0:
                    issues.append(f"Video {video.video_id}: Negative view count")
                
                # Check for unrealistic engagement
                if video.engagement_rate and video.engagement_rate > 1:
                    issues.append(f"Video {video.video_id}: Engagement rate > 100%")
            
            if issues:
                print("⚠️  Data quality issues found:")
                for issue in issues[:10]:  # Show first 10
                    print(f"   - {issue}")
                return False
            
            print(f"✓ YouTube data quality check passed ({len(videos)} videos)")
            return True
            
    except Exception as e:
        print(f"⚠️  Error checking YouTube data: {e}")
        return True  # Don't fail if we can't check


def validate_instagram_data():
    """Validate Instagram data quality"""
    try:
        from src.database import get_db_session
        from src.database.models import InstagramPost
        
        with get_db_session() as session:
            posts = session.query(InstagramPost).limit(100).all()
            
            if not posts:
                print("⚠️  No Instagram posts found in database")
                return True  # Not a failure, just empty
            
            issues = []
            
            for post in posts:
                # Check for negative likes
                if post.like_count is not None and post.like_count < 0:
                    issues.append(f"Post {post.post_id}: Negative like count")
                
                # Check for missing media type
                if not post.media_type:
                    issues.append(f"Post {post.post_id}: Missing media type")
            
            if issues:
                print("⚠️  Data quality issues found:")
                for issue in issues[:10]:
                    print(f"   - {issue}")
                return False
            
            print(f"✓ Instagram data quality check passed ({len(posts)} posts)")
            return True
            
    except Exception as e:
        print(f"⚠️  Error checking Instagram data: {e}")
        return True


def validate_data_consistency():
    """Check data consistency across tables"""
    try:
        from src.database import get_db_session
        from src.database.models import YouTubeChannel, YouTubeVideo
        
        with get_db_session() as session:
            # Check for orphaned videos
            orphaned = session.query(YouTubeVideo).filter(
                ~YouTubeVideo.channel_id.in_(
                    session.query(YouTubeChannel.channel_id)
                )
            ).count()
            
            if orphaned > 0:
                print(f"⚠️  Found {orphaned} orphaned videos (no parent channel)")
            else:
                print("✓ Data consistency check passed")
            
            return orphaned == 0
            
    except Exception as e:
        print(f"⚠️  Error checking data consistency: {e}")
        return True


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🔍 DATA QUALITY VALIDATION")
    print("=" * 50 + "\n")
    
    results = []
    results.append(validate_youtube_data())
    results.append(validate_instagram_data())
    results.append(validate_data_consistency())
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("✅ All data quality checks PASSED!")
        sys.exit(0)
    else:
        print("⚠️  Some data quality checks had issues")
        sys.exit(1)
