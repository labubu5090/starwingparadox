"""Tests for POST /game_data/* endpoints."""

from fastapi.testclient import TestClient


class TestGameDataLoad:
    """Test POST /game_data/load endpoint."""

    def test_load_returns_501(self, client: TestClient):
        response = client.post("/game_data/load", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_load_returns_not_implemented(self, client: TestClient):
        response = client.post("/game_data/load", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/game_data/load"

    def test_load_no_result_field(self, client: TestClient):
        response = client.post("/game_data/load", json={})
        data = response.json()
        assert "result" not in data

    def test_load_x_legacy_compat(self, client: TestClient):
        response = client.post("/game_data/load", json={})
        assert response.headers.get("x-legacy-compat") == "false"
        assert "application/json" in response.headers["content-type"]


class TestGameDataLoadMission:
    """Test POST /game_data/load/mission endpoint."""

    def test_load_mission_returns_501(self, client: TestClient):
        response = client.post("/game_data/load/mission", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_load_mission_returns_not_implemented(self, client: TestClient):
        response = client.post("/game_data/load/mission", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/game_data/load/mission"

    def test_load_mission_no_result_field(self, client: TestClient):
        response = client.post("/game_data/load/mission", json={})
        data = response.json()
        assert "result" not in data
        assert "application/json" in response.headers["content-type"]


class TestGameDataSave:
    """Test POST /game_data/save endpoint."""

    def test_save_returns_501(self, client: TestClient):
        response = client.post("/game_data/save", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_save_returns_not_implemented(self, client: TestClient):
        response = client.post("/game_data/save", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/game_data/save"

    def test_save_no_result_without_persistence(self, client: TestClient):
        response = client.post("/game_data/save", json={})
        assert response.status_code != 200
        data = response.json()
        assert data.get("result") != 1

    def test_save_x_legacy_compat(self, client: TestClient):
        response = client.post("/game_data/save", json={})
        assert response.headers.get("x-legacy-compat") == "false"
        assert "application/json" in response.headers["content-type"]

    def test_save_has_corrid(self, client: TestClient):
        response = client.post("/game_data/save", json={})
        data = response.json()
        assert "corrid" in data
        assert isinstance(data["corrid"], str)
        assert len(data["corrid"]) > 0


class TestGameDataFallback:
    """Test POST /game_data/* fallback endpoint."""

    def test_unknown_game_data_returns_200(self, client: TestClient):
        response = client.post("/game_data/unknown_op", json={})
        assert response.status_code == 200

    def test_unknown_game_data_returns_result(self, client: TestClient):
        response = client.post("/game_data/unknown_op", json={})
        assert response.json()["result"] == 1
