"""
Environment Configuration Validation Test
==========================================
Verifies all required environment variables are properly set.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_environment_variables():
    """Verify all required environment variables are set"""
    
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'SECRET_KEY': 'Application secret key'
    }
    
    optional_vars = {
        'YOUTUBE_API_KEY': 'YouTube API key',
        'INSTAGRAM_ACCESS_TOKEN': 'Instagram access token',
        'REDIS_URL': 'Redis connection string',
        'USE_MOCK_DATA': 'Mock data mode flag'
    }
    
    missing = []
    warnings = []
    
    print("\n🔍 Checking Environment Variables...")
    print("=" * 50)
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(f"❌ {var} ({description})")
            print(f"❌ {var}: NOT SET")
        else:
            # Mask sensitive data
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"✓ {var}: {masked}")
    
    print("")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value:
            warnings.append(f"⚠️  {var} ({description}) - Optional")
            print(f"⚠️  {var}: NOT SET (optional)")
        else:
            masked = value[:10] + "..." if len(value) > 10 else "***"
            print(f"✓ {var}: {masked}")
    
    print("=" * 50)
    
    if missing:
        print("\n❌ MISSING REQUIRED VARIABLES:")
        for msg in missing:
            print(msg)
        print("\nPlease create a .env file with these variables.")
        return False
    
    if warnings:
        print("\n⚠️  OPTIONAL VARIABLES NOT SET:")
        for msg in warnings:
            print(msg)
    
    # Check mock mode
    mock_mode = os.getenv('USE_MOCK_DATA', 'false').lower() == 'true'
    print(f"\n📊 Mock Data Mode: {'ENABLED' if mock_mode else 'DISABLED'}")
    
    print("\n✅ All required environment variables are configured!")
    return True


def test_database_url_format():
    """Validate DATABASE_URL format"""
    db_url = os.getenv('DATABASE_URL', '')
    
    if not db_url:
        print("⚠️  DATABASE_URL not set")
        return True  # Optional for SQLite fallback
    
    valid_prefixes = ['postgresql://', 'postgres://', 'sqlite:///', 'mysql://']
    
    if any(db_url.startswith(prefix) for prefix in valid_prefixes):
        print(f"✓ DATABASE_URL format is valid")
        return True
    else:
        print(f"❌ DATABASE_URL format is invalid. Expected: postgresql://user:pass@host:port/db")
        return False


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🧪 ENVIRONMENT VALIDATION TEST")
    print("=" * 60)
    
    success = test_environment_variables()
    db_valid = test_database_url_format()
    
    if success and db_valid:
        print("\n✅ Environment validation PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Environment validation FAILED!")
        sys.exit(1)
