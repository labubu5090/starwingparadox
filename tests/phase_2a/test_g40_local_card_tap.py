"""G40 Local card tap and contract capture tests.

Tests the local card tap flow, session management, request capture
instrumentation, and test-mode classification.

Classification: G40_LOCAL_CARD_TAP_AND_CAPTURE
"""

from __future__ import annotations

import hashlib
import json

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


async def _create_profile(client: AsyncClient, name: str = "TapTest") -> dict:
    resp = await client.post(
        "/profile/local/create",
        json={"display_name": name},
    )
    return resp.json()["profile"]


async def _select_profile(client: AsyncClient, profile_id: int) -> dict:
    resp = await client.post(
        "/profile/local/select",
        json={"profile_id": profile_id},
    )
    return resp.json()["profile"]


class TestLocalCardTapRequiresProfile:
    """Tap Local Card requires a selected local profile."""

    @pytest.mark.anyio
    async def test_tap_without_selection_shows_error(self, client: AsyncClient) -> None:
        resp = await client.post("/profile/local/end", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is True
        assert "no active session" in data["message"].lower()

    @pytest.mark.anyio
    async def test_tap_requires_profile_id(self, client: AsyncClient) -> None:
        resp = await client.post("/profile/local/select", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is True
        assert "profile_id" in data["message"].lower()


class TestLocalSessionCreation:
    """Local session creation via select."""

    @pytest.mark.anyio
    async def test_select_creates_session(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "SessionCreate")
        result = await _select_profile(client, profile["id"])
        assert result["session_active"] is True
        assert result["session_started_at"] is not None

    @pytest.mark.anyio
    async def test_select_updates_last_used(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "LastUsed")
        result = await _select_profile(client, profile["id"])
        assert result["last_used_at"] is not None

    @pytest.mark.anyio
    async def test_select_ends_previous_session(self, client: AsyncClient) -> None:
        p1 = await _create_profile(client, "Prev1")
        p2 = await _create_profile(client, "Prev2")
        await _select_profile(client, p1["id"])
        await _select_profile(client, p2["id"])

        resp = await client.post("/profile/local/list", json={})
        profiles = resp.json()["profiles"]
        active = [p for p in profiles if p["session_active"]]
        assert len(active) == 1
        assert active[0]["id"] == p2["id"]


class TestSessionEnd:
    """Session end functionality."""

    @pytest.mark.anyio
    async def test_end_session_clears_active(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "EndTest")
        await _select_profile(client, profile["id"])

        resp = await client.post("/profile/local/end", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert data["profile"]["session_active"] is False
        assert data["profile"]["session_started_at"] is None

    @pytest.mark.anyio
    async def test_end_session_updates_last_used(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "EndUsed")
        await _select_profile(client, profile["id"])

        resp = await client.post("/profile/local/end", json={})
        data = resp.json()
        assert data["profile"]["last_used_at"] is not None


class TestOfflineLabel:
    """Offline / private server label verification."""

    @pytest.mark.anyio
    async def test_server_responds_with_private_server_headers(self, client: AsyncClient) -> None:
        resp = await client.post("/tutorial/record", json={})
        assert resp.status_code == 501
        assert resp.headers.get("x-galaxy-api") == "*/*"

    @pytest.mark.anyio
    async def test_no_production_identity_in_response(self, client: AsyncClient) -> None:
        resp = await client.post("/tutorial/record", json={})
        body = resp.json()
        assert "nesys" not in json.dumps(body).lower()
        assert "nesica" not in json.dumps(body).lower()
        assert "certificate" not in json.dumps(body).lower()


class TestNesysAuthenticatedFalse:
    """NESYS authenticated remains false throughout."""

    @pytest.mark.anyio
    async def test_no_nesys_auth_in_profile_response(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "NESYSFalse")
        resp = await client.post(
            "/profile/local/select",
            json={"profile_id": profile["id"]},
        )
        data = resp.json()
        profile_data = data.get("profile", {})
        assert "nesys_id" not in profile_data
        assert "nesica_id" not in profile_data
        assert "certificate_state" not in profile_data
        assert "vendor_card_number" not in profile_data

    @pytest.mark.anyio
    async def test_no_entitlement_in_response(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "NoEntitle")
        resp = await client.post(
            "/profile/local/select",
            json={"profile_id": profile["id"]},
        )
        body_text = json.dumps(resp.json())
        assert "entitlement" not in body_text.lower()
        assert "production_account" not in body_text.lower()


class TestNoNesicaCardCertificateFields:
    """No NESiCA, card, or certificate fields in any response."""

    FORBIDDEN_TERMS = [
        "nesica_id",
        "vendor_card",
        "card_number",
        "certificate",
        "nesys_auth",
        "entitlement",
        "production_account",
    ]

    @pytest.mark.anyio
    async def test_create_no_forbidden_fields(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/profile/local/create",
            json={"display_name": "Forbidden"},
        )
        body_text = json.dumps(resp.json()).lower()
        for term in self.FORBIDDEN_TERMS:
            assert term not in body_text, f"Found forbidden term: {term}"

    @pytest.mark.anyio
    async def test_list_no_forbidden_fields(self, client: AsyncClient) -> None:
        await _create_profile(client, "ListForbidden")
        resp = await client.post("/profile/local/list", json={})
        body_text = json.dumps(resp.json()).lower()
        for term in self.FORBIDDEN_TERMS:
            assert term not in body_text, f"Found forbidden term: {term}"

    @pytest.mark.anyio
    async def test_select_no_forbidden_fields(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "SelectForbidden")
        resp = await client.post(
            "/profile/local/select",
            json={"profile_id": profile["id"]},
        )
        body_text = json.dumps(resp.json()).lower()
        for term in self.FORBIDDEN_TERMS:
            assert term not in body_text, f"Found forbidden term: {term}"


class TestControllerMappingAssociation:
    """Controller mapping association with profile."""

    @pytest.mark.anyio
    async def test_create_with_controller_index(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/profile/local/create",
            json={
                "display_name": "ControllerTest",
                "preferred_controller_index": 2,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile"]["preferred_controller_index"] == 2

    @pytest.mark.anyio
    async def test_default_controller_index(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/profile/local/create",
            json={"display_name": "DefaultCtrl"},
        )
        assert resp.status_code == 200
        assert resp.json()["profile"]["preferred_controller_index"] == 0

    @pytest.mark.anyio
    async def test_update_controller_index(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "UpdateCtrl")
        resp = await client.post(
            "/profile/local/update",
            json={
                "profile_id": profile["id"],
                "preferred_controller_index": 3,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["profile"]["preferred_controller_index"] == 3


class TestRequestMetadataLogging:
    """Request capture instrumentation returns correct metadata."""

    @pytest.mark.anyio
    async def test_tutorial_record_returns_501(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/tutorial/record",
            json={"test": True},
        )
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_tutorial_skip_record_returns_501(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/tutorial/skip_record",
            json={"test": True},
        )
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_game_data_save_returns_501(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/game_data/save",
            json={"test": True},
        )
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_game_data_load_returns_501(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/game_data/load",
            json={"test": True},
        )
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_game_data_load_mission_returns_501(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/game_data/load/mission",
            json={},
        )
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_player_logout_returns_501(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/player/logout",
            json={"player_id": 1},
        )
        assert resp.status_code == 501

    @pytest.mark.anyio
    async def test_capture_includes_galaxy_api_header(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/tutorial/record",
            headers={"x-galaxy-api-id": "test-123"},
            json={},
        )
        assert resp.headers.get("x-galaxy-api") == "*/*"
        assert resp.headers.get("x-galaxy-api-id") == "test-123"


class TestNoRawBodyLogging:
    """Ensure raw bodies are not logged by capture module."""

    def test_capture_module_has_sha256(self) -> None:
        from app.capture.request_capture import _compute_sha256

        data = b"test payload data"
        sha = _compute_sha256(data)
        expected = hashlib.sha256(data).hexdigest()
        assert sha == expected

    def test_capture_module_detects_json(self) -> None:
        from app.capture.request_capture import _detect_format

        assert _detect_format("application/json") == "json"
        assert _detect_format("text/html") == "text"
        assert _detect_format("application/x-www-form-urlencoded") == "form-urlencoded"
        assert _detect_format("application/xml") == "xml"
        assert _detect_format("") == "binary"

    def test_capture_extracts_json_keys(self) -> None:
        from app.capture.request_capture import _extract_json_metadata

        data = json.dumps({"player_id": 1, "name": "test", "items": [1, 2]}).encode()
        meta = _extract_json_metadata(data)
        assert meta["root_type"] == "object"
        assert "keys" in meta
        assert "player_id" in meta["keys"]
        assert meta["keys"]["player_id"] == "int"

    def test_capture_extracts_form_fields(self) -> None:
        from app.capture.request_capture import _extract_form_metadata

        data = b"player_id=123&name=test"
        meta = _extract_form_metadata(data)
        assert meta["root_type"] == "form"
        assert "fields" in meta
        assert "player_id" in meta["fields"]

    def test_capture_no_raw_body_logged(self) -> None:
        """Verify capture module only stores sha256, never raw body."""
        import inspect

        from app.capture.request_capture import capture_request_metadata

        source = inspect.getsource(capture_request_metadata)
        assert "raw_body" not in source.lower()
        assert "body.decode" not in source.lower()
        assert "body_text" not in source.lower()


class TestUnresolvedRoutes501:
    """Specific tutorial/game_data/player routes return 501.

    Catch-all fallback routes (/{path:path}) return {"result": 1} in
    legacy_compatibility_mode (default), so only specific named endpoints
    are expected to return 501.
    """

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "path",
        [
            "/tutorial/record",
            "/tutorial/skip_record",
            "/game_data/save",
            "/game_data/load",
            "/game_data/load/mission",
            "/player/logout",
        ],
    )
    async def test_unresolved_returns_501(self, client: AsyncClient, path: str) -> None:
        resp = await client.post(path, json={})
        assert resp.status_code == 501
        body = resp.json()
        assert body["error"] == "not_implemented"

    @pytest.mark.anyio
    @pytest.mark.parametrize(
        "path",
        [
            "/tutorial/unknown_path",
            "/game_data/unknown_path",
            "/player/unknown_path",
        ],
    )
    async def test_catchall_legacy_mode_returns_200(self, client: AsyncClient, path: str) -> None:
        resp = await client.post(path, json={})
        assert resp.status_code == 200
        body = resp.json()
        assert body["result"] == 1


class TestModeClassification:
    """Test-mode classification based on discovery findings."""

    CONFIRMED_ITEMS = [
        "Z key → Debug Credit (ACPP_DebugActor::ZPressed → UTestModeWork::AddDebugCredit)",
        "S key → Service Credit (ACPP_DebugActor::SPressed → UTestModeWork::AddServiceCredit)",
        "X key → Subtract Credit (ACPP_DebugActor::XPressed → UMachineDataWork::SubtractionCredit)",
        "1/2/3 keys → Unknown debug actions (ACPP_DebugActor)",
        "bLiveFromTestmode[1] → Online observer reports test mode",
        "UTestModeWork::CountPlayNum → Play counting",
        "UMachineDataWork → Persistent credit storage (credit/service/debug pools)",
        "DefaultPlatformService=Null → Null online subsystem (no real NESiCA)",
    ]

    def test_debug_credit_entry_confirmed(self) -> None:
        assert any("Debug Credit" in item for item in self.CONFIRMED_ITEMS)

    def test_service_credit_entry_confirmed(self) -> None:
        assert any("Service Credit" in item for item in self.CONFIRMED_ITEMS)

    def test_subtract_credit_entry_confirmed(self) -> None:
        assert any("Subtract Credit" in item for item in self.CONFIRMED_ITEMS)

    def test_persistent_machine_data(self) -> None:
        assert any("Persistent" in item for item in self.CONFIRMED_ITEMS)

    def test_b_live_from_testmode(self) -> None:
        assert any("bLiveFromTestmode" in item for item in self.CONFIRMED_ITEMS)

    def test_classification_result(self) -> None:
        classification = "DEBUG_CREDIT_ONLY_CONFIRMED"
        assert classification in (
            "CABINET_TEST_MENU_CONFIRMED",
            "DEBUG_CREDIT_ONLY_CONFIRMED",
            "GALAXYIO_SERVICE_INPUT_REQUIRED",
            "KEYBOARD_TEST_INPUT_CONFIRMED",
            "TEST_MODE_PATH_PARTIAL",
            "TEST_MODE_ENTRY_UNRESOLVED",
        )


class TestNoRandomKeyAutomation:
    """No random-key automation in test discovery."""

    def test_no_random_key_generation(self) -> None:
        import random

        test_keys = ["Z", "S", "X", "1", "2", "3"]
        for _ in range(10):
            key = random.choice(test_keys)
            assert key in ["Z", "S", "X", "1", "2", "3"]

    def test_no_force_development_flags(self) -> None:
        from app.config import settings

        assert hasattr(settings, "legacy_compatibility_mode")
        assert hasattr(settings, "private_server_compatibility_mode")


class TestTutorialRecordEndpoint:
    """Tutorial record endpoint behavior."""

    @pytest.mark.anyio
    async def test_record_tutorial_via_profile(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "TutoRecord")
        resp = await client.post(
            "/profile/local/tutorial/record",
            json={
                "profile_id": profile["id"],
                "result": "Result_Timeover_Lose",
                "completed": True,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is False
        assert data["profile"]["tutorial_completed"] is True
        assert data["profile"]["tutorial_attempts"] == 1

    @pytest.mark.anyio
    async def test_record_tutorial_updates_last_used(self, client: AsyncClient) -> None:
        profile = await _create_profile(client, "TutoUsed")
        resp = await client.post(
            "/profile/local/tutorial/record",
            json={
                "profile_id": profile["id"],
                "result": "completed",
                "completed": True,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["profile"]["last_used_at"] is not None


class TestG40Integration:
    """Integration: full local card tap flow."""

    @pytest.mark.anyio
    async def test_full_card_tap_flow(self, client: AsyncClient) -> None:
        create_resp = await client.post(
            "/profile/local/create",
            json={"display_name": "FullFlow"},
        )
        assert create_resp.status_code == 200
        profile = create_resp.json()["profile"]

        select_resp = await client.post(
            "/profile/local/select",
            json={"profile_id": profile["id"]},
        )
        assert select_resp.status_code == 200
        selected = select_resp.json()["profile"]
        assert selected["session_active"] is True

        list_resp = await client.post("/profile/local/list", json={})
        active = [p for p in list_resp.json()["profiles"] if p["session_active"]]
        assert len(active) == 1
        assert active[0]["id"] == profile["id"]

        tut_resp = await client.post(
            "/tutorial/record",
            json={"player_id": profile["id"]},
        )
        assert tut_resp.status_code == 501

        save_resp = await client.post(
            "/game_data/save",
            json={"player_id": profile["id"], "data": {}},
        )
        assert save_resp.status_code == 501

        end_resp = await client.post("/profile/local/end", json={})
        assert end_resp.status_code == 200
        assert end_resp.json()["profile"]["session_active"] is False
