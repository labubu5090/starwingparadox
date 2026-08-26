"""Tests for legacy_compatibility_mode behaviour across stub and real endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.config import settings

# ---------------------------------------------------------------------------
# Stub endpoints – legacy mode ON (default)
# ---------------------------------------------------------------------------


class TestStubsLegacyOn:
    def test_tutorial_stub_returns_result(self, client: TestClient):
        response = client.post("/tutorial/some_path", json={})
        assert response.status_code == 200
        assert response.json()["result"] == 1

    def test_matching_server_stub_returns_result(self, client: TestClient):
        response = client.post("/matching/server", json={})
        assert response.status_code == 200
        assert response.json()["result"] == 1

    def test_matching_fallback_stub_returns_result(self, client: TestClient):
        response = client.post("/matching/other", json={})
        assert response.status_code == 200
        assert response.json()["result"] == 1

    def test_player_fallback_stub_returns_result(self, client: TestClient):
        response = client.post("/player/some_endpoint", json={})
        assert response.status_code == 200
        assert response.json()["result"] == 1

    def test_player_login_bonus_stub(self, client: TestClient):
        response = client.post("/player/login_bonus", json={})
        assert response.status_code == 200
        assert response.json()["result"] == 1

    def test_matching_match_id_generate_stub(self, client: TestClient):
        response = client.post("/matching/match_id/generate", json={})
        assert response.status_code == 200
        assert response.json()["result"] == 1


# ---------------------------------------------------------------------------
# Stub endpoints – legacy mode OFF
# ---------------------------------------------------------------------------


class TestStubsLegacyOff:
    def test_tutorial_returns_501(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/tutorial/some_path", json={})
        assert response.status_code == 501
        data = response.json()
        assert data["error"] == "not_implemented"
        assert "corrid" in data
        assert data["endpoint"] == "/tutorial/some_path"

    def test_matching_server_returns_501(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/matching/server", json={})
        assert response.status_code == 501
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/matching/server"

    def test_matching_fallback_returns_501(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/matching/other_path", json={})
        assert response.status_code == 501
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/matching/other_path"

    def test_player_fallback_returns_501(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/player/unimplemented", json={})
        assert response.status_code == 501
        data = response.json()
        assert data["error"] == "not_implemented"
        assert "corrid" in data

    def test_player_login_bonus_returns_501(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/player/login_bonus", json={})
        assert response.status_code == 501
        data = response.json()
        assert data["error"] == "not_implemented"
        assert data["endpoint"] == "/player/login_bonus"

    def test_matching_match_id_generate_returns_501(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/matching/match_id/generate", json={})
        assert response.status_code == 501
        data = response.json()
        assert data["error"] == "not_implemented"


# ---------------------------------------------------------------------------
# Real endpoints – work in both modes
# ---------------------------------------------------------------------------


class TestRealEndpointsBothModes:
    def test_health_in_legacy_mode(self, client: TestClient):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_in_non_legacy_mode(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_version_in_legacy_mode(self, client: TestClient):
        response = client.post("/version", json={})
        assert response.status_code == 200
        assert "client_version" in response.json()

    def test_version_in_non_legacy_mode(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/version", json={})
        assert response.status_code == 200
        assert "client_version" in response.json()

    def test_resource_in_legacy_mode(self, client: TestClient):
        response = client.post("/resource", json={})
        assert response.status_code == 200

    def test_resource_in_non_legacy_mode(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/resource", json={})
        assert response.status_code == 200

    def test_profile_load_in_legacy_mode(self, client: TestClient):
        response = client.post("/player/profile/load", json={"nesys_id": "TEST001"})
        assert response.status_code == 200

    def test_profile_load_in_non_legacy_mode(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/player/profile/load", json={"nesys_id": "TEST001"})
        assert response.status_code == 200

    def test_login_in_legacy_mode(self, client: TestClient):
        response = client.post("/player/login", json={"player_id": 10010})
        assert response.status_code == 200

    def test_login_in_non_legacy_mode(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/player/login", json={"player_id": 10010})
        assert response.status_code == 200

    def test_register_in_legacy_mode(self, client: TestClient):
        response = client.post("/player/register", json={"nesys_id": "REG001", "name": "Tester"})
        assert response.status_code == 200

    def test_register_in_non_legacy_mode(self, client: TestClient, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(settings, "legacy_compatibility_mode", False)
        response = client.post("/player/register", json={"nesys_id": "REG002", "name": "Tester2"})
        assert response.status_code == 200
