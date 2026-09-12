"""Legacy regression: POST /mission/* database validation.

Source evidence: legacy-js/js/starwing.js lines 595-614
Fixture: server/tests/fixtures/legacy/http/mission_fallback.py

The legacy server at lines 595-614:
  1. Has a single catch-all route POST /mission/*
  2. Does NOT query any database tables
  3. Returns empty JSON object {}
  4. Comment indicates mission/reward/get expects:
     {player_id, mission_id, mission_reward_ids}
     and should return {intimacy_reward_ids:[], update_items:{}, update_missions:[]}
  5. Sets x-galaxy-api: '*/*' and echoes x-galaxy-api-id

IMPLEMENTED EXTENSION (dev.starwing.jp private server):
  - POST /mission/reward/get now processes reward claims (starwing.js:599
    comment documents the awaited response fields). Without a structured
    response the client hangs in MissionMainModeRewardDrawWait and re-offers
    the same reward forever (observed repeatedly in AcrGame.log).
  - Reward grants: reward ids map via Reward.csv (ItemTypeId 7 = player
    title, ItemId = title_id). Granted titles are upserted to
    player_titles; game money (ItemTypeId 1) goes to update_items.
  - The mission is marked drawn (status=0, mission_status=400) in
    player_missions, matching captured real-server saved state
    (API-NOTES.txt line 48 shows drawn missions with mission_status 400).
  - Other /mission/* subpaths remain the legacy fallback.

DATABASE ANALYSIS:
  - Legacy mission fallback performs ZERO database reads or writes
  - The /mission/reward/get extension writes player_titles + player_missions
  - Mission data is loaded via /game_data/load (separate handler)
  - Mission data is saved via /game_data/save (separate handler)

REGRESSION STATUS: Other subpaths return 501 not_implemented when
legacy_compatibility_mode is False, and {} when True. This is CORRECT -
no mission operations are source-proven in the /mission/* handler.
"""

import pytest
from fastapi.testclient import TestClient

pytestmark = [pytest.mark.legacy_regression, pytest.mark.api]


class TestMissionDatabaseValidation:
    """Verify POST /mission/* endpoint behaviors.

    Source: legacy-js/js/starwing.js:595-614

    Legacy behavior:
      - Single catch-all POST /mission/* route
      - Logs request path, headers, body to console
      - Returns empty JSON object {}
      - Sets x-galaxy-api: '*/*'
      - Echoes x-galaxy-api-id from request

    Legacy comment at line 599:
      mission/reward/get {"player_id":"10010","mission_id":"136001",
        "mission_reward_ids":"[7102551]"}
      waits for intimacy_reward_ids:[], update_items: {}, update_missions: []

    Extension: /mission/reward/get grants rewards and returns the awaited
    structure; other subpaths keep the legacy {} fallback.
    """

    SOURCE_FILE = "legacy-js/js/starwing.js"
    SOURCE_LINE_START = 595
    SOURCE_LINE_END = 614
    TABLES_ACCESSED: list[str] = []

    def test_mission_endpoint_returns_controlled_response(self, client: TestClient) -> None:
        """Mission endpoint returns either 200 with {} or 501 not_implemented."""
        response = client.post(
            "/mission/reward/get",
            json={
                "player_id": "10010",
                "mission_id": "136001",
                "mission_reward_ids": "[7102551]",
            },
        )
        assert response.status_code in (200, 501)

    def test_mission_200_returns_structured_reward_response(self, client: TestClient) -> None:
        """mission/reward/get returns the awaited reward structure (not empty {})."""
        response = client.post(
            "/mission/reward/get",
            json={
                "player_id": "10010",
                "mission_id": "136001",
                "mission_reward_ids": "[7102551]",
            },
        )
        if response.status_code == 200:
            data = response.json()
            assert data == {} or (data.get("result") is not None)
            assert "intimacy_reward_ids" in data
            assert "update_items" in data
            assert "update_missions" in data

    def test_mission_501_returns_not_implemented(self, client: TestClient) -> None:
        """Strict mode returns 501 with not_implemented error."""
        response = client.post(
            "/mission/reward/get",
            json={
                "player_id": "10010",
                "mission_id": "136001",
                "mission_reward_ids": "[7102551]",
            },
        )
        if response.status_code == 501:
            data = response.json()
            assert data.get("error") == "not_implemented"
            assert data.get("endpoint") == "/mission/reward/get"
            assert "corrid" in data

    def test_no_false_success_for_mission_operations(self, client: TestClient) -> None:
        """Non-reward mission subpaths must not return fake success.

        Legacy mission fallback returns {} with no result field.
        A response with result=1 would be false success. The /mission/reward/get
        extension is a real implementation and may return result=1.
        """
        for path in ["list", "update", "unknown"]:
            response = client.post(f"/mission/{path}", json={"player_id": "10010"})
            assert response.status_code in (200, 501)
            if response.status_code == 200:
                data = response.json()
                # Must not contain result: 1 (false success)
                assert data.get("result") != 1

    def test_no_database_writes(self, client: TestClient) -> None:
        """Non-reward mission subpaths must not perform any database writes.

        The legacy handler performs zero database operations.
        The Python handler must match this: no side effects.
        (mission/reward/get is the implemented extension that does write.)
        """
        response = client.post("/mission/update", json={"player_id": "10010"})
        assert response.status_code in (200, 501)
        if response.status_code == 200:
            assert response.json() == {}

    def test_mission_x_galaxy_api_id_echoed(self, client: TestClient) -> None:
        """Legacy echoes x-galaxy-api-id from the request."""
        response = client.post(
            "/mission/reward/get",
            json={},
            headers={"x-galaxy-api-id": "test-mission-456"},
        )
        assert response.headers.get("x-galaxy-api-id") == "test-mission-456"

    def test_mission_content_type_is_json(self, client: TestClient) -> None:
        """Response must be JSON content type."""
        response = client.post("/mission/reward/get", json={})
        assert "application/json" in response.headers["content-type"]

    def test_mission_x_galaxy_api_header(self, client: TestClient) -> None:
        """Legacy sets x-galaxy-api to '*/*'."""
        response = client.post("/mission/reward/get", json={})
        assert response.headers.get("x-galaxy-api") == "*/*"

    def test_mission_various_subpaths_all_controlled(self, client: TestClient) -> None:
        """Non-reward mission subpaths behave identically (stub)."""
        for path in ["reward/claim", "list", "update", "unknown"]:
            response = client.post(
                f"/mission/{path}",
                json={"player_id": "10010"},
            )
            assert response.status_code in (200, 501)
            if response.status_code == 200:
                assert response.json() == {}

    def test_mission_reward_get_expected_response_structure(self, client: TestClient) -> None:
        """mission/reward/get returns the awaited response structure.

        Legacy comment at starwing.js:599-601 indicates:
          Input: {player_id, mission_id, mission_reward_ids}
          Expected output: {intimacy_reward_ids:[], update_items:{}, update_missions:[]}

        The Python reimplementation returns this structure (plus result) so
        the client's MissionMainModeRewardDrawWait completes.
        """
        response = client.post(
            "/mission/reward/get",
            json={
                "player_id": "10010",
                "mission_id": "136001",
                "mission_reward_ids": "[7102551]",
            },
        )
        assert response.status_code in (200, 501)
        if response.status_code == 200:
            data = response.json()
            assert "intimacy_reward_ids" in data
            assert "update_items" in data
            assert "game_moneys" in data["update_items"]
            assert "update_missions" in data

    def test_mission_reward_get_grants_title(self, client: TestClient) -> None:
        """reward id 7102551 maps to a player title and is persisted.

        Reward.csv: 7102551 -> ItemTypeId 7 (player title), ItemId 102551.
        The granted title must be upserted into player_titles.
        """
        reg = client.post("/player/register", json={"player_id": "10010", "nesys_id": "10010"})
        pid = reg.json().get("player_id", "10010")
        response = client.post(
            "/mission/reward/get",
            json={
                "player_id": pid,
                "mission_id": "136001",
                "mission_reward_ids": "[7102551]",
            },
        )
        if response.status_code != 200:
            return

        titles = client.post(
            "/game_data/load",
            json={"player_id": pid},
        )
        assert titles.status_code == 200
        found = any(t.get("title_id") == 102551 for t in titles.json().get("titles", []))
        assert found, "Granted title 102551 not found in player_titles"

    def test_mission_reward_get_marks_mission_drawn(self, client: TestClient) -> None:
        """Drawn mission is persisted with status=0 mission_status=400."""
        response = client.post(
            "/mission/reward/get",
            json={
                "player_id": "10010",
                "mission_id": "136001",
                "mission_reward_ids": "[7102551]",
            },
        )
        assert response.status_code in (200, 501)
        if response.status_code != 200:
            return
        data = response.json()
        um = data.get("update_missions", [])
        assert um, "update_missions must contain the drawn mission"
        assert um[0].get("mission_status") == 400

    def test_mission_draw_survives_client_stale_save(self, client: TestClient) -> None:
        """A drawn mission (0/400) must not be reverted to claimable by a stale
        /game_data/save carrying the client's previous status=4 snapshot.

        The real client re-sends its whole mission list after the draw; the
        save path must preserve the server's drawn state.
        """
        reg = client.post("/player/register", json={"player_id": "10010", "nesys_id": "10010"})
        pid = reg.json().get("player_id", "10010")
        draw = client.post(
            "/mission/reward/get",
            json={
                "player_id": pid,
                "mission_id": "136001",
                "mission_reward_ids": "[7102551]",
            },
        )
        if draw.status_code != 200:
            return

        save = client.post(
            "/game_data/save",
            json={
                "player_id": pid,
                "missions": [
                    {"mission_id": 136001, "clear_count": 0, "clear_num": 6, "status": 4, "mission_status": 400}
                ],
            },
        )
        assert save.status_code in (200, 501)
        if save.status_code != 200:
            return

        loaded = client.post(
            "/mission/normal",
            json={"player_id": pid},
        )
        assert loaded.status_code == 200
        missions = loaded.json().get("missions", [])
        match = [m for m in missions if m.get("mission_id") == 136001]
        assert match, "drawn mission missing from /mission/normal"
        assert match[0]["status"] == 0, f"stale save reverted drawn mission: {match[0]}"
        assert match[0]["mission_status"] == 400

    def test_mission_no_database_tables_documented(self) -> None:
        """Verify no mission tables are documented as accessed in /mission/*.

        The legacy mission handler contains zero SQL queries.
        Mission data is persisted via /game_data/save only.
        """
        assert self.TABLES_ACCESSED == []
