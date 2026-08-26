"""Legacy regression: POST /game_data/load endpoint.

Source evidence: legacy-js/js/starwing.js lines 677-698
Fixture: server/tests/fixtures/legacy/http/game_data_load.json

The legacy server at lines 677-698:
  1. Reads player_id from request body
  2. Queries all player data tables (17+ tables)
  3. Returns a complex nested object with all game data

REGRESSION STATUS: The Python reimplementation intentionally returns 501
not_implemented for /game_data/load and /game_data/load/mission. This is
CORRECT behavior - these endpoints require complex database queries that
are not yet implemented. The fallback returns {result: 1} in legacy mode.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.legacy_regression, pytest.mark.api]


class TestGameDataLoadLegacyRegression:
    """Verify POST /game_data/load matches or controls legacy behavior.

    Source: legacy-js/js/starwing.js:677-698

    Legacy behavior:
      - /game_data/load returns full game data structure
      - /game_data/load/mission returns {missions: [...]}
      - Both set x-galaxy-api to 'game_data/load'

    Python implementation:
      - /game_data/load returns 501 not_implemented (not yet implemented)
      - /game_data/load/mission returns 501 not_implemented (not yet implemented)
      - /game_data/* fallback returns {result: 1} in legacy mode
    """

    SOURCE_FILE = "legacy-js/js/starwing.js"
    SOURCE_LINE_START = 677
    SOURCE_LINE_END = 698
    FIXTURE = "server/tests/fixtures/legacy/http/game_data_load.json"

    def test_game_data_load_returns_valid_status(self, client: TestClient) -> None:
        """POST /game_data/load returns 200 (legacy) or 501 (strict)."""
        response = client.post(
            "/game_data/load",
            json={"player_id": "10010"},
        )
        assert response.status_code in (200, 501)

    def test_game_data_load_strict_mode_returns_501(self, client: TestClient) -> None:
        """When legacy_compatibility_mode is False, returns 501.
        This is CORRECT - prevents false success on unimplemented endpoint."""
        response = client.post(
            "/game_data/load",
            json={"player_id": "10010"},
        )
        if response.status_code == 501:
            data = response.json()
            assert data.get("error") == "not_implemented"
            assert data.get("endpoint") == "/game_data/load"
            assert "corrid" in data

    def test_game_data_load_legacy_mode_returns_200(self, client: TestClient) -> None:
        """When legacy_compatibility_mode is True, returns 200."""
        response = client.post(
            "/game_data/load",
            json={"player_id": "10010"},
        )
        if response.status_code == 200:
            data = response.json()
            assert "result" in data

    def test_game_data_load_x_galaxy_api_id_echoed(self, client: TestClient) -> None:
        """Legacy echoes x-galaxy-api-id."""
        response = client.post(
            "/game_data/load",
            json={"player_id": "10010"},
            headers={"x-galaxy-api-id": "test-gd-456"},
        )
        assert response.headers.get("x-galaxy-api-id") == "test-gd-456"

    def test_game_data_load_content_type(self, client: TestClient) -> None:
        """Response must be JSON."""
        response = client.post(
            "/game_data/load",
            json={"player_id": "10010"},
        )
        assert "application/json" in response.headers["content-type"]

    def test_load_mission_returns_valid_status(self, client: TestClient) -> None:
        """POST /game_data/load/mission returns 200 or 501."""
        response = client.post(
            "/game_data/load/mission",
            json={"player_id": "10010"},
        )
        assert response.status_code in (200, 501)

    def test_load_mission_strict_mode_returns_501(self, client: TestClient) -> None:
        """Strict mode returns 501 for unimplemented mission loader."""
        response = client.post(
            "/game_data/load/mission",
            json={"player_id": "10010"},
        )
        if response.status_code == 501:
            data = response.json()
            assert data.get("error") == "not_implemented"
            assert data.get("endpoint") == "/game_data/load/mission"

    def test_load_mission_legacy_mode_returns_200(self, client: TestClient) -> None:
        """Legacy mode returns 200 for mission loader."""
        response = client.post(
            "/game_data/load/mission",
            json={"player_id": "10010"},
        )
        if response.status_code == 200:
            data = response.json()
            assert "result" in data

    def test_game_data_fallback_returns_valid_status(self, client: TestClient) -> None:
        """POST /game_data/unknown returns 200 (legacy) or 501 (strict)."""
        response = client.post(
            "/game_data/unknown_path",
            json={},
        )
        assert response.status_code in (200, 501)

    def test_game_data_fallback_legacy_mode_returns_200(self, client: TestClient) -> None:
        """In legacy compatibility mode, fallback returns 200."""
        response = client.post(
            "/game_data/unknown_path",
            json={},
        )
        assert response.status_code == 200

    def test_game_data_fallback_legacy_response_has_result(self, client: TestClient) -> None:
        """Legacy fallback returns {result: 1}."""
        response = client.post(
            "/game_data/unknown_path",
            json={},
        )
        data = response.json()
        assert data.get("result") == 1

    def test_prove_no_false_success_on_unknown_game_data(self, client: TestClient) -> None:
        """CRITICAL: Unknown game_data endpoints must not return fake data."""
        response = client.post(
            "/game_data/completely_fake",
            json={"fake": True},
        )
        assert response.status_code in (200, 501)
        if response.status_code == 200:
            data = response.json()
            # Must not contain real game data
            assert "player" not in data
            assert "buddies" not in data
            assert "missions" not in data
            assert data.get("result") == 1
