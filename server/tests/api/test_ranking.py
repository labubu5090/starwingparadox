"""Tests for POST /ranking/* endpoints."""

from fastapi.testclient import TestClient


class TestRankingNational:
    """Test POST /ranking/national endpoint."""

    def test_ranking_national_returns_501(self, client: TestClient):
        response = client.post("/ranking/national", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_ranking_national_returns_not_implemented(self, client: TestClient):
        response = client.post("/ranking/national", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/ranking/national"

    def test_ranking_national_x_legacy_compat(self, client: TestClient):
        response = client.post("/ranking/national", json={})
        assert response.headers.get("x-legacy-compat") == "false"
        assert "application/json" in response.headers["content-type"]


class TestRankingLocation:
    """Test POST /ranking/location endpoint."""

    def test_ranking_location_returns_501(self, client: TestClient):
        response = client.post("/ranking/location", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_ranking_location_returns_not_implemented(self, client: TestClient):
        response = client.post("/ranking/location", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/ranking/location"
        assert "application/json" in response.headers["content-type"]


class TestRankingPrefecture:
    """Test POST /ranking/prefecture endpoint."""

    def test_ranking_prefecture_returns_501(self, client: TestClient):
        response = client.post("/ranking/prefecture", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_ranking_prefecture_returns_not_implemented(self, client: TestClient):
        response = client.post("/ranking/prefecture", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/ranking/prefecture"
        assert "application/json" in response.headers["content-type"]


class TestRankingEvent:
    """Test POST /ranking/event endpoint."""

    def test_ranking_event_returns_501(self, client: TestClient):
        response = client.post("/ranking/event", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_ranking_event_returns_not_implemented(self, client: TestClient):
        response = client.post("/ranking/event", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/ranking/event"
        assert "application/json" in response.headers["content-type"]


class TestRankingWeapon:
    """Test POST /ranking/weapon endpoint."""

    def test_ranking_weapon_returns_501(self, client: TestClient):
        response = client.post("/ranking/weapon", json={"role_id": "1"})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_ranking_weapon_returns_not_implemented(self, client: TestClient):
        response = client.post("/ranking/weapon", json={"role_id": "1"})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/ranking/weapon"
        assert "application/json" in response.headers["content-type"]


class TestRankingFallback:
    """Test POST /ranking/* fallback endpoint."""

    def test_unknown_ranking_returns_200(self, client: TestClient):
        response = client.post("/ranking/unknown", json={})
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_unknown_ranking_returns_empty(self, client: TestClient):
        response = client.post("/ranking/unknown", json={})
        assert response.json() == {}
