
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from src.database import get_db_session, check_database_connection
from src.database.models import YouTubeChannel

def check_db():
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    if check_database_connection():
        print("✅ Database connection successful")
        with get_db_session() as session:
            channels = session.query(YouTubeChannel).all()
            print(f"Found {len(channels)} channels:")
            for c in channels:
                print(f" - {c.title} ({c.channel_id})")
    else:
        print("❌ Database connection failed")

if __name__ == "__main__":
    check_db()
