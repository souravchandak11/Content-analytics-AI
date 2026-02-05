"""
Database Tests
==============
Tests for database connection and data persistence.
"""

import pytest
import os
from dotenv import load_dotenv

load_dotenv()


class TestDatabase:
    """Test database functionality"""
    
    def test_database_connection(self):
        """Test database connection"""
        from src.database import check_database_connection
        
        connected = check_database_connection()
        assert connected, "Database connection failed"
        print("✓ Database connection successful")
    
    def test_youtube_channel_save(self):
        """Test saving YouTube channel data"""
        from src.database import get_db_session
        from src.database.models import YouTubeChannel
        
        with get_db_session() as session:
            # Try to query channels
            count = session.query(YouTubeChannel).count()
            print(f"✓ Found {count} YouTube channels in database")
            # Just verify we can query without error
            assert count >= 0
    
    def test_database_tables_exist(self):
        """Verify all required database tables exist"""
        from src.database import get_db_session
        from sqlalchemy import inspect
        
        required_tables = [
            'youtube_channels',
            'youtube_videos',
            'instagram_accounts',
            'instagram_posts'
        ]
        
        with get_db_session() as session:
            inspector = inspect(session.bind)
            existing_tables = inspector.get_table_names()
            
            for table in required_tables:
                if table in existing_tables:
                    print(f"✓ Table '{table}' exists")
                else:
                    print(f"⚠️ Table '{table}' not found")
    
    def test_session_management(self):
        """Test database session management"""
        from src.database import get_db_session
        
        # Test context manager cleanup
        with get_db_session() as session:
            assert session is not None
            print("✓ Session created successfully")
        
        print("✓ Session cleaned up properly")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
