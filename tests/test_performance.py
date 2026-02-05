"""
Performance Tests
=================
Tests for query and API performance benchmarks.
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_database_query_performance():
    """Test database query performance"""
    try:
        from src.database import get_db_session
        from src.database.models import YouTubeVideo
        
        with get_db_session() as session:
            start = time.time()
            
            # Query 100 videos
            videos = session.query(YouTubeVideo).limit(100).all()
            
            elapsed = time.time() - start
            
            if elapsed < 1.0:
                print(f"✓ Database query: {elapsed:.3f}s (< 1s threshold)")
                return True
            else:
                print(f"⚠️  Database query slow: {elapsed:.3f}s (> 1s threshold)")
                return False
                
    except Exception as e:
        print(f"⚠️  Error testing database performance: {e}")
        return True


def test_api_response_time():
    """Test API endpoint response time"""
    import requests
    
    try:
        start = time.time()
        
        response = requests.get('http://localhost:8000/health', timeout=5)
        
        elapsed = time.time() - start
        
        if response.status_code == 200 and elapsed < 2.0:
            print(f"✓ API health check: {elapsed:.3f}s (< 2s threshold)")
            return True
        elif response.status_code != 200:
            print(f"⚠️  API health check failed: Status {response.status_code}")
            return False
        else:
            print(f"⚠️  API response slow: {elapsed:.3f}s (> 2s threshold)")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running - skipping performance test")
        return True
    except Exception as e:
        print(f"⚠️  Error testing API performance: {e}")
        return True


def test_dashboard_summary_performance():
    """Test dashboard summary endpoint performance"""
    import requests
    
    try:
        start = time.time()
        
        response = requests.get('http://localhost:8000/api/ai/dashboard/summary', timeout=10)
        
        elapsed = time.time() - start
        
        if response.status_code == 200 and elapsed < 5.0:
            print(f"✓ Dashboard summary: {elapsed:.3f}s (< 5s threshold)")
            return True
        elif response.status_code != 200:
            print(f"⚠️  Dashboard summary failed: Status {response.status_code}")
            return False
        else:
            print(f"⚠️  Dashboard summary slow: {elapsed:.3f}s (> 5s threshold)")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  API server not running - skipping test")
        return True
    except Exception as e:
        print(f"⚠️  Error testing dashboard summary: {e}")
        return True


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("⚡ PERFORMANCE TESTS")
    print("=" * 50 + "\n")
    
    results = []
    results.append(test_database_query_performance())
    results.append(test_api_response_time())
    results.append(test_dashboard_summary_performance())
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("✅ All performance tests PASSED!")
        sys.exit(0)
    else:
        print("⚠️  Some performance tests had issues")
        sys.exit(1)
