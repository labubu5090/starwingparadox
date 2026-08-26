"""Tests for health and readiness endpoints."""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test GET /health endpoint."""

    def test_health_returns_ok(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_json(self, client: TestClient):
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"


class TestReadinessEndpoint:
    """Test GET /ready endpoint."""

    def test_ready_returns_status(self, client: TestClient):
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ready"

    def test_ready_returns_json(self, client: TestClient):
        response = client.get("/ready")
        assert response.headers["content-type"] == "application/json"
