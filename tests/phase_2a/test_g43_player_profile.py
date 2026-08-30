"""G43 tests: /player/profile/load handler and related endpoints."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Async test client for the FastAPI app."""
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),         base_url="http://testserver"
    ) as c:
        yield c


class TestProfileLoadDedicatedHandler:
    """Verify /player/profile/load uses a dedicated handler, not the catch-all."""

    @pytest.mark.anyio
    async def test_profile_load_returns_200(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-001"},
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_profile_load_returns_player_id(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-002"},
        )
        data = resp.json()
        assert "player_id" in data
        assert isinstance(data["player_id"], int)
        assert data["player_id"] > 0

    @pytest.mark.anyio
    async def test_profile_load_returns_nesys_id(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-003"},
        )
        data = resp.json()
        assert data.get("nesys_id") == "test-g43-nesys-003"

    @pytest.mark.anyio
    async def test_profile_load_returns_player_name(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-004"},
        )
        data = resp.json()
        assert "player_name" in data
        assert isinstance(data["player_name"], str)

    @pytest.mark.anyio
    async def test_profile_load_returns_rank_fields(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-005"},
        )
        data = resp.json()
        for field in ["rank_id", "rank_id_2on2", "title_id", "title_id_2on2"]:
            assert field in data
            assert isinstance(data[field], int)

    @pytest.mark.anyio
    async def test_profile_load_returns_emblem_fields(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-006"},
        )
        data = resp.json()
        for field in ["emblem_id", "emblem_id_2on2", "line_color_id", "line_color_id_2on2"]:
            assert field in data
            assert isinstance(data[field], int)

    @pytest.mark.anyio
    async def test_profile_load_returns_progresses(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-007"},
        )
        data = resp.json()
        assert "progresses" in data
        assert isinstance(data["progresses"], list)

    @pytest.mark.anyio
    async def test_profile_load_no_empty_nesys_id(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": ""},
        )
        data = resp.json()
        assert data.get("result") == 0

    @pytest.mark.anyio
    async def test_profile_load_no_missing_nesys_id(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={},
        )
        data = resp.json()
        assert data.get("result") == 0

    @pytest.mark.anyio
    async def test_profile_load_deterministic(self, client: AsyncClient) -> None:
        r1 = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-deterministic"},
        )
        r2 = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-deterministic"},
        )
        assert r1.json().get("player_id") == r2.json().get("player_id")

    @pytest.mark.anyio
    async def test_profile_load_galaxy_api_header(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-nesys-008"},
            headers={"x-galaxy-api-id": "g43-test-001"},
        )
        assert resp.headers.get("x-galaxy-api") == "*/*"
        assert resp.headers.get("x-galaxy-api-id") == "g43-test-001"


class TestProfileLoadSecurityClassification:
    """Verify no NESYS/NESiCA/certificate/entitlement fields leak."""

    @pytest.mark.anyio
    async def test_no_nesys_auth_fields(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-security-001"},
        )
        data = resp.json()
        forbidden = [
            "nesys_authenticated",
            "nesys_token",
            "certificate",
            "entitlement",
            "vendor_card_number",
            "card_serial",
            "production_account_id",
            "is_nesica",
        ]
        for field in forbidden:
            assert field not in data, f"Forbidden field present: {field}"

    @pytest.mark.anyio
    async def test_no_production_data(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/profile/load",
            json={"nesys_id": "test-g43-security-002"},
        )
        data = resp.json()
        assert data.get("violation_point", 0) == 0


class TestMatchingServerDedicatedHandler:
    """Verify /matching/server uses dedicated handler returning ip_addr."""

    @pytest.mark.anyio
    async def test_matching_server_returns_ip_addr(self, client: AsyncClient) -> None:
        resp = await client.post("/matching/server", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "ip_addr" in data
        assert isinstance(data["ip_addr"], str)

    @pytest.mark.anyio
    async def test_matching_server_ip_contains_port(self, client: AsyncClient) -> None:
        resp = await client.post("/matching/server", json={})
        data = resp.json()
        assert ":" in data["ip_addr"]

    @pytest.mark.anyio
    async def test_matching_server_not_result_only(self, client: AsyncClient) -> None:
        resp = await client.post("/matching/server", json={})
        data = resp.json()
        assert "result" not in data, "matching/server should return ip_addr, not result"


class TestPlayerLoginHandler:
    """Verify /player/login handler works correctly."""

    @pytest.mark.anyio
    async def test_login_returns_200(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/login",
            json={"player_id": 1},
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_login_returns_required_fields(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/login",
            json={"player_id": 1},
        )
        data = resp.json()
        for field in ["player_id", "progresses", "greeting_ids", "battle_count"]:
            assert field in data

    @pytest.mark.anyio
    async def test_login_greeting_ids_is_list(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/login",
            json={"player_id": 1},
        )
        data = resp.json()
        assert isinstance(data["greeting_ids"], list)


class TestPlayerRegisterHandler:
    """Verify /player/register handler creates player correctly."""

    @pytest.mark.anyio
    async def test_register_returns_200(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/register",
            json={"nesys_id": "test-g43-register-001", "name": "G43Test"},
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_register_returns_player_id(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/register",
            json={"nesys_id": "test-g43-register-002", "name": "G43Test2"},
        )
        data = resp.json()
        assert "player_id" in data


class TestGameDataLoadRemainsUnimplemented:
    """Verify /game_data/load remains unimplemented until eligible."""

    @pytest.mark.anyio
    async def test_game_data_load_still_501(self, client: AsyncClient) -> None:
        resp = await client.post("/game_data/load", json={"player_id": 1})
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_game_data_save_still_501(self, client: AsyncClient) -> None:
        resp = await client.post("/game_data/save", json={"player_id": 1})
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_tutorial_still_501(self, client: AsyncClient) -> None:
        resp = await client.post("/tutorial/record", json={})
        assert resp.status_code == 501
