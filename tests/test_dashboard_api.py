
import pytest
from fastapi.testclient import TestClient
from server.main import app

client = TestClient(app)

def test_dashboard_summary_endpoint():
    """Test the newly created dashboard summary endpoint."""
    response = client.get("/api/ai/dashboard/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "metrics" in data
    assert "feed" in data
    assert "growth_forecast" in data
    assert "retention_index" in data
    
    metrics = data["metrics"]
    assert "total_audience" in metrics
    assert "total_reach" in metrics
    assert metrics["total_audience"] > 0
    assert metrics["total_reach"] > 0
    
    feed = data["feed"]
    assert isinstance(feed, list)
    if len(feed) > 0:
        item = feed[0]
        assert "type" in item
        assert "title" in item
        assert "views" in item
        assert "engagement" in item
        assert "id" in item
