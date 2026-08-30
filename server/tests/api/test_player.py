"""Tests for POST /player/* endpoints."""

from fastapi.testclient import TestClient


class TestPlayerProfileLoad:
    """Test POST /player/profile/load endpoint."""

    def test_profile_load_returns_200(self, client: TestClient):
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "TESTNESYS00001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "player_id" in data
        assert "nesys_id" in data

    def test_profile_load_returns_json(self, client: TestClient):
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "TESTNESYS00001"},
        )
        assert "application/json" in response.headers["content-type"]

    def test_profile_load_x_galaxy_api_header(self, client: TestClient):
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "TESTNESYS00001"},
        )
        assert "x-galaxy-api" in response.headers
        assert response.headers.get("x-galaxy-api") == "*/*"


class TestPlayerLogin:
    """Test POST /player/login endpoint."""

    def test_login_returns_200(self, client: TestClient):
        response = client.post(
            "/player/login",
            json={"player_id": "10010"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "result" in data

    def test_login_returns_json(self, client: TestClient):
        response = client.post(
            "/player/login",
            json={"player_id": "10010"},
        )
        assert "application/json" in response.headers["content-type"]

    def test_login_x_galaxy_api_header(self, client: TestClient):
        response = client.post(
            "/player/login",
            json={"player_id": "10010"},
        )
        assert "x-galaxy-api" in response.headers
        assert response.headers.get("x-galaxy-api") == "*/*"


class TestPlayerRegister:
    """Test POST /player/register endpoint."""

    def test_register_returns_200(self, client: TestClient):
        response = client.post(
            "/player/register",
            json={"player_id": "10010"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "result" in data
        assert response.headers["content-type"] == "application/json"

    def test_register_returns_result(self, client: TestClient):
        response = client.post(
            "/player/register",
            json={"player_id": "10010"},
        )
        data = response.json()
        assert "result" in data


class TestPlayerLoginBonus:
    """Test POST /player/login_bonus endpoint."""

    def test_login_bonus_returns_200(self, client: TestClient):
        response = client.post(
            "/player/login_bonus",
            json={"player_id": "10010"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "result" in data
        assert response.headers["content-type"] == "application/json"

    def test_login_bonus_has_result(self, client: TestClient):
        response = client.post(
            "/player/login_bonus",
            json={"player_id": "10010"},
        )
        data = response.json()
        assert "result" in data


class TestPlayerFallback:
    """Test POST /player/* fallback endpoint."""

    def test_unknown_player_endpoint_returns_200(self, client: TestClient):
        response = client.post(
            "/player/unknown_operation",
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "result" in data

    def test_unknown_player_endpoint_returns_result(self, client: TestClient):
        response = client.post(
            "/player/unknown_operation",
            json={},
        )
        data = response.json()
        assert "result" in data
