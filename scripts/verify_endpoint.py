
import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_test():
    try:
        from server.main import app
        client = TestClient(app)
        print("Testing /api/ai/dashboard/summary...")
        response = client.get("/api/ai/dashboard/summary")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
        if response.status_code == 200:
            print("✅ Success!")
        else:
            print("❌ Failed!")
    except Exception as e:
        print(f"💥 Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    run_test()
