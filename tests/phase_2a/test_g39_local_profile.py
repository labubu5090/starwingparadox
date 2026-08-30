"""G39 Local profile API tests.

Tests the local profile CRUD endpoints and tutorial recording.

Classification: LOCAL_PROFILE_IMPLEMENTED
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Async test client for the FastAPI app."""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


class TestLocalProfileCreate:
    """Test profile creation endpoint."""

    @pytest.mark.anyio
    async def test_create_profile_returns_200(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/profile/local/create",
            json={"display_name": "TestPlayer"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert "profile" in data
        assert data["profile"]["display_name"] == "TestPlayer"
        assert "profile_uuid" in data["profile"]

    @pytest.mark.anyio
    async def test_create_profile_default_name(self, client: AsyncClient) -> None:
        resp = await client.post("/profile/local/create", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile"]["display_name"] == "Player"

    @pytest.mark.anyio
    async def test_create_profile_with_notes(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/profile/local/create",
            json={"display_name": "NoteTest", "notes": "test notes"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile"]["notes"] == "test notes"


class TestLocalProfileList:
    """Test profile listing endpoint."""

    @pytest.mark.anyio
    async def test_list_profiles_returns_200(self, client: AsyncClient) -> None:
        resp = await client.post("/profile/local/list", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert "profiles" in data
        assert isinstance(data["profiles"], list)


class TestLocalProfileSelect:
    """Test profile selection endpoint."""

    @pytest.mark.anyio
    async def test_select_profile_returns_200(self, client: AsyncClient) -> None:
        # Create a profile first
        create_resp = await client.post(
            "/profile/local/create",
            json={"display_name": "SelectTest"},
        )
        profile_id = create_resp.json()["profile"]["id"]

        # Select it
        resp = await client.post(
            "/profile/local/select",
            json={"profile_id": profile_id},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert data["profile"]["session_active"] is True

    @pytest.mark.anyio
    async def test_select_nonexistent_profile(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/profile/local/select",
            json={"profile_id": 99999},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is True
        assert "not found" in data["message"].lower()


class TestLocalProfileEndSession:
    """Test session end endpoint."""

    @pytest.mark.anyio
    async def test_end_session_returns_200(self, client: AsyncClient) -> None:
        # Create and select a profile
        create_resp = await client.post(
            "/profile/local/create",
            json={"display_name": "EndSessionTest"},
        )
        profile_id = create_resp.json()["profile"]["id"]
        await client.post(
            "/profile/local/select",
            json={"profile_id": profile_id},
        )

        # End session
        resp = await client.post("/profile/local/end", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert data["profile"]["session_active"] is False


class TestLocalProfileTutorialRecord:
    """Test tutorial recording endpoint."""

    @pytest.mark.anyio
    async def test_record_tutorial_attempt(self, client: AsyncClient) -> None:
        # Create a profile
        create_resp = await client.post(
            "/profile/local/create",
            json={"display_name": "TutorialTest"},
        )
        profile_id = create_resp.json()["profile"]["id"]

        # Record tutorial attempt
        resp = await client.post(
            "/profile/local/tutorial/record",
            json={
                "profile_id": profile_id,
                "result": "Result_Timeover_Lose",
                "completed": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert data["profile"]["tutorial_attempts"] == 1
        assert data["profile"]["tutorial_completed"] is True
        assert data["profile"]["tutorial_last_result"] == "Result_Timeover_Lose"


class TestLocalProfileUpdate:
    """Test profile update endpoint."""

    @pytest.mark.anyio
    async def test_update_profile_name(self, client: AsyncClient) -> None:
        # Create a profile
        create_resp = await client.post(
            "/profile/local/create",
            json={"display_name": "OldName"},
        )
        profile_id = create_resp.json()["profile"]["id"]

        # Update name
        resp = await client.post(
            "/profile/local/update",
            json={"profile_id": profile_id, "display_name": "NewName"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert data["profile"]["display_name"] == "NewName"


class TestLocalProfileDelete:
    """Test profile deletion endpoint."""

    @pytest.mark.anyio
    async def test_delete_profile(self, client: AsyncClient) -> None:
        # Create a profile
        create_resp = await client.post(
            "/profile/local/create",
            json={"display_name": "DeleteTest"},
        )
        profile_id = create_resp.json()["profile"]["id"]

        # Delete it
        resp = await client.post(
            "/profile/local/delete",
            json={"profile_id": profile_id},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert data["deleted"] is True

        # Verify it's gone
        list_resp = await client.post("/profile/local/list", json={})
        profiles = list_resp.json()["profiles"]
        assert all(p["id"] != profile_id for p in profiles)


class TestLocalProfileHealthEndpoint:
    """Test that health endpoint works with new profile table."""

    @pytest.mark.anyio
    async def test_health_endpoint(self, client: AsyncClient) -> None:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("healthy", "ok")
