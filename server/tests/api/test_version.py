"""Tests for POST /version endpoint."""

from fastapi.testclient import TestClient


class TestVersionEndpoint:
    """Test POST /version endpoint."""

    def test_version_returns_200(self, client: TestClient):
        response = client.post("/version", json={})
        assert response.status_code == 200

    def test_version_returns_json(self, client: TestClient):
        response = client.post("/version", json={})
        assert response.headers["content-type"] == "application/json"

    def test_version_has_client_version(self, client: TestClient):
        response = client.post("/version", json={})
        data = response.json()
        assert "client_version" in data

    def test_version_has_data_version(self, client: TestClient):
        response = client.post("/version", json={})
        data = response.json()
        assert "data_version" in data

    def test_version_has_stage_ids(self, client: TestClient):
        response = client.post("/version", json={})
        data = response.json()
        assert "stage_ids" in data
        assert isinstance(data["stage_ids"], list)

    def test_version_client_version_is_string(self, client: TestClient):
        response = client.post("/version", json={})
        data = response.json()
        assert isinstance(data["client_version"], str)

    def test_version_data_version_is_string(self, client: TestClient):
        response = client.post("/version", json={})
        data = response.json()
        assert isinstance(data["data_version"], str)

    def test_version_x_galaxy_api_header(self, client: TestClient):
        response = client.post("/version", json={})
        assert "x-galaxy-api" in response.headers

    def test_version_x_galaxy_api_id_header(self, client: TestClient):
        response = client.post(
            "/version",
            json={},
            headers={"x-galaxy-api-id": "test-123"},
        )
        assert response.headers.get("x-galaxy-api-id") == "test-123"
