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

    def test_matching_server_returns_ip_addr(self, client: TestClient):
        response = client.post("/matching/server", json={})
        data = response.json()
        assert "ip_addr" in data
        assert isinstance(data["ip_addr"], str)
        assert ":" in data["ip_addr"]

    def test_matching_server_no_result_field(self, client: TestClient):
        response = client.post("/matching/server", json={})
        data = response.json()
        assert "result" not in data

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

    def test_match_id_generate_returns_int(self, client: TestClient):
        response = client.post("/matching/match_id/generate", json={})
        data = response.json()
        assert "match_id" in data
        assert isinstance(data["match_id"], int)
        assert 10000 <= data["match_id"] <= 99999

    def test_match_id_generate_no_result_field(self, client: TestClient):
        response = client.post("/matching/match_id/generate", json={})
        data = response.json()
        assert "result" not in data


class TestMatchingFallback:
    """Test POST /matching/* fallback endpoint."""

    def test_unknown_matching_endpoint_returns_200(self, client: TestClient):
        response = client.post("/matching/unknown", json={})
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_unknown_matching_endpoint_returns_empty(self, client: TestClient):
        response = client.post("/matching/unknown", json={})
        data = response.json()
        assert data == {}

    def test_unknown_matching_endpoint_no_result(self, client: TestClient):
        response = client.post("/matching/unknown", json={})
        data = response.json()
        assert "result" not in data
