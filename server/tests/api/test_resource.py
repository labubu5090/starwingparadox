"""Tests for POST /resource endpoint."""

from fastapi.testclient import TestClient


class TestResourceEndpoint:
    """Test POST /resource endpoint."""

    def test_resource_returns_200(self, client: TestClient):
        response = client.post("/resource", json={})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_resource_returns_json(self, client: TestClient):
        response = client.post("/resource", json={})
        assert "application/json" in response.headers["content-type"]

    def test_resource_x_galaxy_api_header(self, client: TestClient):
        response = client.post("/resource", json={})
        assert "x-galaxy-api" in response.headers
        assert response.headers.get("x-galaxy-api") == "*/*"

    def test_resource_x_galaxy_api_id_echoed(self, client: TestClient):
        response = client.post(
            "/resource",
            json={},
            headers={"x-galaxy-api-id": "test-id"},
        )
        assert response.headers.get("x-galaxy-api-id") == "test-id"

    def test_resource_body_not_required(self, client: TestClient):
        response = client.post("/resource")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
