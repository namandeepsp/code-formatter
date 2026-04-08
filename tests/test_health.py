import pytest
import time

class TestHealthEndpoints:
    
    def test_ping_endpoint(self, client):
        """Test that ping endpoint responds quickly"""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.text == "pong"
    
    def test_health_endpoint(self, client):
        """Test health check shows all formatters"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "warning"]
        assert "formatters" in data
        assert "memory_usage_mb" in data
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint returns memory info"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "memory_mb" in data
        assert isinstance(data["memory_mb"], (int, float))
        assert data["memory_mb"] > 0
    
    def test_health_response_time(self, client):
        """Test health check is fast"""
        start = time.time()
        response = client.get("/ping")
        elapsed = time.time() - start
        assert elapsed < 0.05  # 50ms max
        assert response.status_code == 200