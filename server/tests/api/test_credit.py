"""Tests for POST /credit/* endpoints."""

from fastapi.testclient import TestClient


class TestCreditFallback:
    """Test POST /credit/* fallback endpoint."""

    def test_credit_returns_200(self, client: TestClient):
        response = client.post("/credit/some_operation", json={})
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_credit_returns_empty(self, client: TestClient):
        response = client.post("/credit/some_operation", json={})
        assert response.json() == {}

    def test_credit_no_result_field(self, client: TestClient):
        response = client.post("/credit/some_operation", json={})
        data = response.json()
        assert "result" not in data

    def test_credit_no_success_without_processing(self, client: TestClient):
        response = client.post("/credit/some_operation", json={})
        data = response.json()
        assert data.get("result") != 1

    def test_credit_purchase_returns_empty(self, client: TestClient):
        response = client.post("/credit/purchase", json={"item_id": "123"})
        assert response.status_code == 200
        assert response.json() == {}
        assert response.headers["content-type"] == "application/json"

    def test_credit_history_returns_empty(self, client: TestClient):
        response = client.post("/credit/history", json={"player_id": "10010"})
        assert response.status_code == 200
        assert response.json() == {}
        assert response.headers["content-type"] == "application/json"
