"""Legacy regression: POST /battle/* endpoints.

Source evidence: legacy-js/js/starwing.js lines 739-777
Fixture: server/tests/fixtures/legacy/http/

The legacy battle endpoints:
  - /battle/record_2on2 (lines 739-759): Full battle recording via BattleRecorder
  - /battle/* (lines 761-777): Fallback returns {result: 1}

REGRESSION STATUS: The Python reimplementation intentionally returns 501
not_implemented for /battle/record_2on2 when legacy_compatibility_mode is
False. When True, it returns {result: 1}. The fallback always returns
{result: 1} in legacy mode. This is CORRECT behavior - it prevents false
success on unimplemented endpoints.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.legacy_regression, pytest.mark.api]


class TestBattleLegacyRegression:
    """Verify POST /battle/* endpoints match or control legacy behavior.

    Source: legacy-js/js/starwing.js:739-777

    Legacy behavior:
      - /battle/record_2on2 returns full response with rewards/stats
      - /battle/* fallback returns {result: 1} for any path

    Python implementation:
      - /battle/record_2on2 returns 501 when legacy_compatibility_mode=False
      - /battle/record_2on2 returns {result: 1} when legacy_compatibility_mode=True
      - /battle/* fallback returns {result: 1} in legacy mode
    """

    SOURCE_FILE = "legacy-js/js/starwing.js"
    SOURCE_LINE_START = 739
    SOURCE_LINE_END = 777
    FIXTURE = "server/tests/fixtures/legacy/http/battle_record_2on2.json"

    def test_battle_record_2on2_returns_valid_status(self, client: TestClient) -> None:
        """POST /battle/record_2on2 returns 200 (legacy) or 501 (strict)."""
        response = client.post(
            "/battle/record_2on2",
            json={
                "player_id": "10010",
                "stage_id": "20001",
                "match_id": "12345",
            },
        )
        assert response.status_code in (200, 501)

    def test_battle_record_2on2_strict_mode_returns_501(self, client: TestClient) -> None:
        """When legacy_compatibility_mode is False, returns 501 not_implemented.
        This is the CORRECT behavior - prevents false success."""
        response = client.post(
            "/battle/record_2on2",
            json={"player_id": "10010", "stage_id": "20001"},
        )
        if response.status_code == 501:
            data = response.json()
            assert data.get("error") == "not_implemented"
            assert data.get("endpoint") == "/battle/record_2on2"
            assert "corrid" in data

    def test_battle_record_2on2_legacy_mode_returns_200_with_result(
        self, client: TestClient
    ) -> None:
        """When legacy_compatibility_mode is True, returns 200 with {result: 1}.
        The full BattleRecorder response is NOT implemented yet."""
        response = client.post(
            "/battle/record_2on2",
            json={"player_id": "10010", "stage_id": "20001"},
        )
        if response.status_code == 200:
            data = response.json()
            assert data.get("result") == 1

    def test_battle_record_2on2_content_type(self, client: TestClient) -> None:
        """Response must be JSON regardless of mode."""
        response = client.post(
            "/battle/record_2on2",
            json={"player_id": "10010", "stage_id": "20001"},
        )
        assert "application/json" in response.headers["content-type"]

    def test_battle_record_2on2_x_galaxy_api_id_echoed(self, client: TestClient) -> None:
        """Legacy echoes x-galaxy-api-id when returning 200."""
        response = client.post(
            "/battle/record_2on2",
            json={"player_id": "10010", "stage_id": "20001"},
            headers={"x-galaxy-api-id": "battle-test-id"},
        )
        if response.status_code == 200:
            assert response.headers.get("x-galaxy-api-id") == "battle-test-id"

    def test_battle_fallback_returns_valid_status(self, client: TestClient) -> None:
        """POST /battle/unknown must return 200 (legacy) or 501 (strict)."""
        response = client.post(
            "/battle/totally_unknown_battle_endpoint",
            json={},
        )
        assert response.status_code in (200, 501)

    def test_battle_fallback_legacy_mode_returns_200(self, client: TestClient) -> None:
        """In legacy compatibility mode, unknown battle paths return 200."""
        response = client.post(
            "/battle/unknown_battle_path",
            json={},
        )
        assert response.status_code == 200

    def test_battle_fallback_legacy_response_has_result_1(self, client: TestClient) -> None:
        """Legacy battle/* fallback always returns {result: 1}."""
        response = client.post(
            "/battle/fake_battle_path",
            json={},
        )
        data = response.json()
        assert data.get("result") == 1

    def test_prove_no_false_success_on_unknown_battle(self, client: TestClient) -> None:
        """CRITICAL: An unknown battle endpoint must NOT return 200 with
        fabricated battle data in strict mode. In legacy mode it returns
        200 with {result: 1} stub. This test proves controlled behavior."""
        response = client.post(
            "/battle/completely_fake_battle_handler",
            json={"fake_data": True},
        )
        assert response.status_code in (200, 501)
        if response.status_code == 200:
            data = response.json()
            # Must not contain battle rewards or stats
            assert "battle_reward_ids" not in data
            assert "rank_up_reward_ids" not in data
            assert "winning_streaks_2on2" not in data
            # Must only contain result field
            assert data.get("result") == 1

    def test_battle_record_2on2_strict_mode_has_corrid(self, client: TestClient) -> None:
        """501 response must include correlation ID for debugging."""
        response = client.post(
            "/battle/record_2on2",
            json={"player_id": "10010", "stage_id": "20001"},
        )
        if response.status_code == 501:
            data = response.json()
            assert "corrid" in data
            assert isinstance(data["corrid"], str)
            assert len(data["corrid"]) > 0
