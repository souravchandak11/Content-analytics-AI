"""
Content Analytics Platform - API Tests
======================================
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health and status endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Content Analytics Platform'
        assert 'version' in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'database' in data


@pytest.fixture
def client():
    """Create test client."""
    try:
        from server.main import app
        return TestClient(app)
    except ImportError:
        pytest.skip("Server not available")
