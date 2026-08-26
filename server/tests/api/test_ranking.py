"""Tests for POST /ranking/* endpoints."""

from fastapi.testclient import TestClient


class TestRankingNational:
    """Test POST /ranking/national endpoint."""

    def test_ranking_national_returns_200(self, client: TestClient):
        response = client.post("/ranking/national", json={})
        assert response.status_code == 200

    def test_ranking_national_returns_json(self, client: TestClient):
        response = client.post("/ranking/national", json={})
        assert "application/json" in response.headers["content-type"]


class TestRankingLocation:
    """Test POST /ranking/location endpoint."""

    def test_ranking_location_returns_200(self, client: TestClient):
        response = client.post("/ranking/location", json={})
        assert response.status_code == 200

    def test_ranking_location_returns_json(self, client: TestClient):
        response = client.post("/ranking/location", json={})
        assert "application/json" in response.headers["content-type"]


class TestRankingPrefecture:
    """Test POST /ranking/prefecture endpoint."""

    def test_ranking_prefecture_returns_200(self, client: TestClient):
        response = client.post("/ranking/prefecture", json={})
        assert response.status_code == 200

    def test_ranking_prefecture_returns_json(self, client: TestClient):
        response = client.post("/ranking/prefecture", json={})
        assert "application/json" in response.headers["content-type"]


class TestRankingEvent:
    """Test POST /ranking/event endpoint."""

    def test_ranking_event_returns_200(self, client: TestClient):
        response = client.post("/ranking/event", json={})
        assert response.status_code == 200

    def test_ranking_event_returns_json(self, client: TestClient):
        response = client.post("/ranking/event", json={})
        assert "application/json" in response.headers["content-type"]


class TestRankingWeapon:
    """Test POST /ranking/weapon endpoint."""

    def test_ranking_weapon_returns_200(self, client: TestClient):
        response = client.post("/ranking/weapon", json={"role_id": "1"})
        assert response.status_code == 200

    def test_ranking_weapon_returns_json(self, client: TestClient):
        response = client.post("/ranking/weapon", json={"role_id": "1"})
        assert "application/json" in response.headers["content-type"]
