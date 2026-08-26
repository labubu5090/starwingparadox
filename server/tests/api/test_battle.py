"""Tests for POST /battle/* endpoints."""

from fastapi.testclient import TestClient


class TestBattleRecord2on2:
    """Test POST /battle/record_2on2 endpoint."""

    def test_record_2on2_returns_501(self, client: TestClient):
        response = client.post("/battle/record_2on2", json={})
        assert response.status_code == 501
        data = response.json()
        assert isinstance(data, dict)
        assert "error" in data

    def test_record_2on2_returns_not_implemented(self, client: TestClient):
        response = client.post("/battle/record_2on2", json={})
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/battle/record_2on2"

    def test_record_2on2_no_result_field(self, client: TestClient):
        response = client.post("/battle/record_2on2", json={})
        data = response.json()
        assert "result" not in data

    def test_record_2on2_no_success_claim(self, client: TestClient):
        response = client.post("/battle/record_2on2", json={})
        assert response.status_code != 200
        assert response.json().get("result") != 1

    def test_record_2on2_x_legacy_compat(self, client: TestClient):
        response = client.post("/battle/record_2on2", json={})
        assert response.headers.get("x-legacy-compat") == "false"

    def test_record_2on2_has_corrid(self, client: TestClient):
        response = client.post("/battle/record_2on2", json={})
        data = response.json()
        assert "corrid" in data
        assert isinstance(data["corrid"], str)
        assert len(data["corrid"]) > 0


class TestBattleFallback:
    """Test POST /battle/* fallback endpoint."""

    def test_unknown_battle_returns_200(self, client: TestClient):
        response = client.post("/battle/unknown_op", json={})
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_unknown_battle_returns_result(self, client: TestClient):
        response = client.post("/battle/unknown_op", json={})
        data = response.json()
        assert data["result"] == 1
        assert isinstance(data, dict)
