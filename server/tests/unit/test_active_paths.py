"""Tests for credit and mission active code paths."""

from fastapi.testclient import TestClient


class TestCreditActivePaths:
    def test_credit_purchase(self, client: TestClient):
        resp = client.post("/credit/purchase", json={"item": "test"})
        assert resp.status_code == 200
        assert resp.json() == {}

    def test_credit_history(self, client: TestClient):
        resp = client.post("/credit/history", json={"player_id": "10010"})
        assert resp.status_code == 200
        assert resp.json() == {}

    def test_credit_balance(self, client: TestClient):
        resp = client.post("/credit/balance", json={})
        assert resp.status_code == 200

    def test_credit_unknown_path(self, client: TestClient):
        resp = client.post("/credit/unknown_path", json={})
        assert resp.status_code == 200

    def test_credit_galaxy_headers_present(self, client: TestClient):
        resp = client.post("/credit/test", json={})
        assert "x-galaxy-api" in resp.headers

    def test_credit_galaxy_api_id_forwarded(self, client: TestClient):
        resp = client.post(
            "/credit/test",
            json={},
            headers={"x-galaxy-api-id": "test-id-123"},
        )
        assert resp.headers.get("x-galaxy-api-id") == "test-id-123"


class TestMissionActivePaths:
    def test_mission_fallback(self, client: TestClient):
        resp = client.post("/mission/some_operation", json={})
        assert resp.status_code == 200
        assert resp.json() == {}

    def test_mission_empty_body(self, client: TestClient):
        resp = client.post("/mission/progress", json={})
        assert resp.status_code == 200

    def test_mission_galaxy_headers(self, client: TestClient):
        resp = client.post("/mission/test", json={})
        assert "x-galaxy-api" in resp.headers

    def test_mission_with_api_id(self, client: TestClient):
        resp = client.post(
            "/mission/query",
            json={"player_id": 10010},
            headers={"x-galaxy-api-id": "mission-id"},
        )
        assert resp.headers.get("x-galaxy-api-id") == "mission-id"

    def test_mission_multiple_paths(self, client: TestClient):
        for path in ["start", "update", "complete", "status"]:
            resp = client.post(f"/mission/{path}", json={})
            assert resp.status_code == 200


class TestBattleActivePaths:
    def test_battle_record_2on2_not_implemented(self, client: TestClient):
        resp = client.post("/battle/record_2on2", json={})
        assert resp.status_code == 501

    def test_battle_fallback_legacy_mode(self, client: TestClient):
        resp = client.post("/battle/random_endpoint", json={})
        assert resp.status_code == 200
        assert resp.json()["result"] == 1

    def test_battle_record_2on2_corrid(self, client: TestClient):
        resp = client.post("/battle/record_2on2", json={})
        assert "corrid" in resp.json()

    def test_battle_record_2on2_legacy_compat(self, client: TestClient):
        resp = client.post("/battle/record_2on2", json={})
        assert resp.headers.get("x-legacy-compat") == "false"

    def test_battle_unknown_op_result(self, client: TestClient):
        resp = client.post("/battle/unknown_op", json={})
        assert resp.json()["result"] == 1


class TestMatchingActivePaths:
    def test_matching_server(self, client: TestClient):
        resp = client.post("/matching/server", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "ip_addr" in data

    def test_matching_server_contains_port(self, client: TestClient):
        resp = client.post("/matching/server", json={})
        data = resp.json()
        assert ":" in data["ip_addr"]

    def test_match_id_generate(self, client: TestClient):
        resp = client.post("/matching/match_id/generate", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "match_id" in data
        assert 10000 <= data["match_id"] <= 99999

    def test_match_id_uniqueish(self, client: TestClient):
        ids = set()
        for _ in range(10):
            resp = client.post("/matching/match_id/generate", json={})
            ids.add(resp.json()["match_id"])
        assert len(ids) > 1

    def test_matching_fallback(self, client: TestClient):
        resp = client.post("/matching/unknown", json={})
        assert resp.status_code == 200


class TestRankingActivePaths:
    def test_ranking_national(self, client: TestClient):
        resp = client.post("/ranking/national", json={})
        assert resp.status_code == 501

    def test_ranking_location(self, client: TestClient):
        resp = client.post("/ranking/location", json={})
        assert resp.status_code == 501

    def test_ranking_prefecture(self, client: TestClient):
        resp = client.post("/ranking/prefecture", json={})
        assert resp.status_code == 501

    def test_ranking_event(self, client: TestClient):
        resp = client.post("/ranking/event", json={})
        assert resp.status_code == 501

    def test_ranking_weapon(self, client: TestClient):
        resp = client.post("/ranking/weapon", json={})
        assert resp.status_code == 501

    def test_ranking_fallback_legacy(self, client: TestClient):
        resp = client.post("/ranking/unknown", json={})
        assert resp.status_code == 200

    def test_ranking_not_implemented_has_corrid(self, client: TestClient):
        resp = client.post("/ranking/national", json={})
        assert "corrid" in resp.json()


class TestGameDataActivePaths:
    def test_game_data_load(self, client: TestClient):
        resp = client.post("/game_data/load", json={})
        assert resp.status_code == 501

    def test_game_data_load_mission(self, client: TestClient):
        resp = client.post("/game_data/load/mission", json={})
        assert resp.status_code == 501

    def test_game_data_save(self, client: TestClient):
        resp = client.post("/game_data/save", json={})
        assert resp.status_code == 501

    def test_game_data_fallback_legacy(self, client: TestClient):
        resp = client.post("/game_data/other", json={})
        assert resp.status_code == 200
        assert resp.json()["result"] == 1

    def test_game_data_not_implemented_endpoint(self, client: TestClient):
        resp = client.post("/game_data/load", json={})
        data = resp.json()
        assert data["endpoint"] == "/game_data/load"


class TestTutorialActivePaths:
    def test_tutorial_fallback(self, client: TestClient):
        resp = client.post("/tutorial/intro", json={})
        assert resp.status_code == 200

    def test_tutorial_result_field(self, client: TestClient):
        resp = client.post("/tutorial/any", json={})
        assert resp.json()["result"] == 1


class TestHealthEndpoints:
    def test_health(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_ready(self, client: TestClient):
        resp = client.get("/ready")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data


class TestVersionEndpoint:
    def test_version(self, client: TestClient):
        resp = client.post("/version", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "client_version" in data
        assert "data_version" in data
        assert "stage_ids" in data

    def test_version_galaxy_header(self, client: TestClient):
        resp = client.post(
            "/version",
            json={},
            headers={"x-galaxy-api-id": "ver-test"},
        )
        assert resp.headers.get("x-galaxy-api-id") == "ver-test"


class TestPlayerExtended:
    def test_profile_load_no_nesys(self, client: TestClient):
        resp = client.post("/player/profile/load", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("result") == 0

    def test_player_login_no_player_id(self, client: TestClient):
        resp = client.post("/player/login", json={})
        assert resp.status_code == 200

    def test_player_register_with_name(self, client: TestClient):
        resp = client.post(
            "/player/register",
            json={"nesys_id": "TEST_REG", "name": "TestReg"},
        )
        assert resp.status_code == 200

    def test_player_login_updates_last_login(self, client: TestClient):
        resp = client.post(
            "/player/login",
            json={"player_id": 10010},
        )
        assert resp.status_code == 200

    def test_player_profile_load_galaxy_api_header(self, client: TestClient):
        resp = client.post(
            "/player/profile/load",
            json={"nesys_id": "TEST"},
            headers={"x-galaxy-api-id": "test-id"},
        )
        assert resp.headers.get("x-galaxy-api-id") == "test-id"
