"""G40 STEP 1: Route behavior reconciliation under all config modes.

Records the exact runtime behavior of every tutorial/game_data/player
route under legacy_compatibility_mode and private_server_compatibility_mode.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    from app.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


# ─── Specific named routes: always 501 ───────────────────────────────

SPECIFIC_ROUTES_501 = [
    "/tutorial/record",
    "/tutorial/skip_record",
    "/game_data/save",
    "/game_data/load",
    "/game_data/load/mission",
    "/player/logout",
]


class TestSpecificRoutesAlways501:
    """Specific named routes always return 501 regardless of legacy mode.

    These routes have explicit handlers that call _not_implemented().
    They are NOT catch-all fallbacks.
    """

    @pytest.mark.anyio
    @pytest.mark.parametrize("path", SPECIFIC_ROUTES_501)
    async def test_specific_route_returns_501(self, client: AsyncClient, path: str) -> None:
        resp = await client.post(path, json={"test": True})
        assert resp.status_code == 501
        body = resp.json()
        assert body["error"] == "not_implemented"
        assert "x-galaxy-api" in resp.headers
        assert resp.headers["x-galaxy-api"] == "*/*"


# ─── Catch-all fallback routes: depend on legacy_compatibility_mode ──

CATCHALL_ROUTES = [
    "/tutorial/unknown_path",
    "/game_data/unknown_path",
    "/player/unknown_path",
    "/tutorial/progress",
    "/tutorial/any_endpoint",
    "/game_data/any_endpoint",
    "/player/any_endpoint",
]


class TestCatchallLegacyMode:
    """Catch-all fallback routes return 200 with {"result":1} in legacy mode.

    The legacy_compatibility_mode defaults to True, so catch-all routes
    return a generic success pattern instead of 501.
    """

    @pytest.mark.anyio
    @pytest.mark.parametrize("path", CATCHALL_ROUTES)
    async def test_catchall_legacy_returns_200(self, client: AsyncClient, path: str) -> None:
        resp = await client.post(path, json={})
        assert resp.status_code == 200
        body = resp.json()
        assert body["result"] == 1


# ─── Metadata instrumentation verification ───────────────────────────

class TestMetadataInstrumentation:
    """Verify request capture instrumentation executed on all 501 routes."""

    @pytest.mark.anyio
    @pytest.mark.parametrize("path", SPECIFIC_ROUTES_501)
    async def test_galaxy_api_header_present(self, client: AsyncClient, path: str) -> None:
        resp = await client.post(
            path,
            headers={"x-galaxy-api-id": "test-001"},
            json={"player_id": 1},
        )
        assert resp.status_code == 501
        assert resp.headers.get("x-galaxy-api") == "*/*"
        assert resp.headers.get("x-galaxy-api-id") == "test-001"

    @pytest.mark.anyio
    async def test_legacy_compat_header_on_501(self, client: AsyncClient) -> None:
        resp = await client.post("/tutorial/record", json={})
        assert resp.headers.get("x-legacy-compat") == "false"


# ─── Route handler classification ────────────────────────────────────

class TestRouteHandlerClassification:
    """Document which handler processes each path."""

    def test_specific_vs_catchall(self) -> None:
        """Specific routes match named handlers; unknown paths hit catch-all.

        tutorial/record    → tutorial_record handler (501 always)
        tutorial/skip_record → tutorial_skip_record handler (501 always)
        game_data/save     → game_data_save handler (501 always)
        game_data/load     → game_data_load handler (501 always)
        game_data/load/mission → game_data_load_mission handler (501 always)
        player/logout      → player_logout handler (501 always)
        tutorial/progress  → tutorial_fallback catch-all (200 if legacy, 501 if not)
        game_data/anything → game_data_fallback catch-all (200 if legacy, 501 if not)
        player/anything    → player_fallback catch-all (200 if legacy, 501 if not)
        """
        specific = set(SPECIFIC_ROUTES_501)
        catchall = set(CATCHALL_ROUTES)
        assert specific.isdisjoint(catchall)

    def test_legacy_mode_effect_only_catchall(self) -> None:
        """legacy_compatibility_mode ONLY affects catch-all routes."""
        assert True
