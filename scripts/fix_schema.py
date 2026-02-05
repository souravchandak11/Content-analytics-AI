
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

from src.database import init_database, check_database_connection

def fix_schema():
    print("Self-Correction: Fixing database schema mismatch...")
    if check_database_connection():
        init_database(drop_existing=True)
        print("✅ Database re-initialized with full schema.")
    else:
        print("❌ Could not connect to database.")

if __name__ == "__main__":
    fix_schema()
