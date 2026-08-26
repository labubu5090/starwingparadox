"""Tests for POST /matching/* endpoints."""

from fastapi.testclient import TestClient


class TestMatchingServer:
    """Test POST /matching/server endpoint."""

    def test_matching_server_returns_200(self, client: TestClient):
        response = client.post("/matching/server", json={})
        assert response.status_code == 200

    def test_matching_server_returns_json(self, client: TestClient):
        response = client.post("/matching/server", json={})
        assert "application/json" in response.headers["content-type"]

    def test_matching_server_returns_servers(self, client: TestClient):
        response = client.post("/matching/server", json={})
        data = response.json()
        assert "result" in data

    def test_matching_server_x_galaxy_api_header(self, client: TestClient):
        response = client.post("/matching/server", json={})
        assert "x-galaxy-api" in response.headers

    def test_matching_server_echoes_api_id(self, client: TestClient):
        response = client.post(
            "/matching/server",
            json={},
            headers={"x-galaxy-api-id": "match-test"},
        )
        assert response.headers.get("x-galaxy-api-id") == "match-test"


class TestMatchIdGenerate:
    """Test POST /matching/match_id/generate endpoint."""

    def test_match_id_generate_returns_200(self, client: TestClient):
        response = client.post("/matching/match_id/generate", json={})
        assert response.status_code == 200

    def test_match_id_generate_returns_json(self, client: TestClient):
        response = client.post("/matching/match_id/generate", json={})
        assert "application/json" in response.headers["content-type"]

    def test_match_id_generate_has_match_id(self, client: TestClient):
        response = client.post("/matching/match_id/generate", json={})
        data = response.json()
        assert "match_id" in data


class TestMatchingFallback:
    """Test POST /matching/* fallback endpoint."""

    def test_unknown_matching_endpoint_returns_200(self, client: TestClient):
        response = client.post("/matching/unknown", json={})
        assert response.status_code == 200

    def test_unknown_matching_endpoint_returns_result(self, client: TestClient):
        response = client.post("/matching/unknown", json={})
        data = response.json()
        assert "result" in data
