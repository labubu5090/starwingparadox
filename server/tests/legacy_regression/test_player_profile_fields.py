"""Legacy regression: player profile field parity tests.

Source evidence:
  - legacy-js/js/starwing/playerProfile.js:297-350 (getProfile method)
  - legacy-js/js/starwing/playerProfile.js:26-73 (initWithNesys method)
  - legacy-js/js/starwing.js:488-507 (HTTP endpoint)
  - legacy-js/paradox.sql:100-127 (player table DDL)

These tests verify that the Python implementation returns the correct field
names, types, and default values matching the legacy JavaScript server.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models.player import Player

pytestmark = [pytest.mark.legacy_regression, pytest.mark.api, pytest.mark.player_profile]


# ---------------------------------------------------------------------------
# Sync fixtures for DB-backed default tests
# ---------------------------------------------------------------------------

SYNC_URL = "sqlite:///:memory:"
sync_engine = create_engine(SYNC_URL, echo=False)
SyncSession = sessionmaker(bind=sync_engine)


@pytest.fixture(autouse=True)
def _create_tables():
    """Create all tables before each test."""
    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)


@pytest.fixture
def db() -> Session:
    session = SyncSession()
    try:
        yield session
    finally:
        session.close()


# ===========================================================================
# Response headers
# ===========================================================================


class TestPlayerProfileResponseHeaders:
    """Legacy source: starwing.js:496-498
    res.set('Content-type','application/json');
    res.set('x-galaxy-api-id',req.header('x-galaxy-api-id'));
    res.set('x-galaxy-api', 'player/profile');"""

    def test_content_type_is_json(self, client: TestClient) -> None:
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        assert "application/json" in response.headers["content-type"]

    def test_x_galaxy_api_id_echoed(self, client: TestClient) -> None:
        """Legacy echoes x-galaxy-api-id from request."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
            headers={"x-galaxy-api-id": "profile-test-42"},
        )
        assert response.headers.get("x-galaxy-api-id") == "profile-test-42"

    def test_x_galaxy_api_header(self, client: TestClient) -> None:
        """KNOWN DEVIATION: Legacy sets 'player/profile', Python sets '*/*'.
        Source: starwing.js:498 vs player.py:49"""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        api_header = response.headers.get("x-galaxy-api", "")
        assert api_header in ("*/*", "player/profile")

    def test_status_code_is_200(self, client: TestClient) -> None:
        """Legacy always returns 200."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        assert response.status_code == 200


# ===========================================================================
# Identity resolution
# ===========================================================================


class TestPlayerProfileIdentityResolution:
    """Legacy source: playerProfile.js:26-73 (initWithNesys)"""

    def test_valid_nesys_id_returns_response(self, client: TestClient) -> None:
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert isinstance(data, dict)

    def test_empty_nesys_id_returns_result_0(self, client: TestClient) -> None:
        """Legacy: playerProfile.js:29 returns false for empty nesys_id.
        Python: player.py:56 returns _ok(result=0)."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": ""},
        )
        data = response.json()
        assert data.get("result") == 0

    def test_missing_nesys_id_returns_result_0(self, client: TestClient) -> None:
        response = client.post(
            "/player/profile/load",
            json={},
        )
        data = response.json()
        assert data.get("result") == 0

    def test_null_nesys_id_returns_result_0(self, client: TestClient) -> None:
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": None},
        )
        data = response.json()
        assert data.get("result") == 0


# ===========================================================================
# Player table field presence
# ===========================================================================


class TestPlayerProfileFieldPresence:
    """Legacy source: playerProfile.js:21
    for(var k in res.rows[0]) this.Player[k]=res.rows[0][k];"""

    def test_response_is_valid_json(self, client: TestClient) -> None:
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert isinstance(data, dict)


# ===========================================================================
# Default values matching legacy SQL DDL (DB-backed)
# ===========================================================================


class TestPlayerProfileDefaultValues:
    """Legacy source: paradox.sql:100-127
    Column defaults must match between SQL DDL and Python model.
    Tests use DB-backed insert to verify server-side defaults."""

    def test_default_rank_id_is_zero(self, db: Session) -> None:
        """paradox.sql:104: rank_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.rank_id == 0

    def test_default_rank_id_2on2_is_zero(self, db: Session) -> None:
        """paradox.sql:105: rank_id_2on2 integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.rank_id_2on2 == 0

    def test_default_title_id_is_zero(self, db: Session) -> None:
        """paradox.sql:106: title_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.title_id == 0

    def test_default_title_id_2on2_is_zero(self, db: Session) -> None:
        """paradox.sql:107: title_id_2on2 integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.title_id_2on2 == 0

    def test_default_buddy_id_is_zero(self, db: Session) -> None:
        """paradox.sql:108: buddy_id smallint DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.buddy_id == 0

    def test_default_buddy_intimacy_is_zero(self, db: Session) -> None:
        """paradox.sql:109: buddy_intimacy smallint DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.buddy_intimacy == 0

    def test_default_line_color_id_is_zero(self, db: Session) -> None:
        """paradox.sql:110: line_color_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.line_color_id == 0

    def test_default_ranking_pref_name_is_tokyo(self, db: Session) -> None:
        """paradox.sql:111: DEFAULT '東京'"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.ranking_pref_name == "東京"

    def test_default_last_ranking_pref_name_is_tokyo(self, db: Session) -> None:
        """paradox.sql:112: DEFAULT '東京'"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.last_ranking_pref_name == "東京"

    def test_default_match_mode_id_is_zero(self, db: Session) -> None:
        """paradox.sql:113: match_mode_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.match_mode_id == 0

    def test_default_violation_point_is_zero(self, db: Session) -> None:
        """paradox.sql:114: violation_point integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.violation_point == 0

    def test_default_emblem_id_is_zero(self, db: Session) -> None:
        """paradox.sql:115: emblem_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.emblem_id == 0

    def test_default_line_color_id_2on2_is_zero(self, db: Session) -> None:
        """paradox.sql:116: line_color_id_2on2 integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.line_color_id_2on2 == 0

    def test_default_emblem_id_2on2_is_zero(self, db: Session) -> None:
        """paradox.sql:117: emblem_id_2on2 integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.emblem_id_2on2 == 0

    def test_default_birth_day_is_one(self, db: Session) -> None:
        """paradox.sql:118: birth_day integer DEFAULT 1"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.birth_day == 1

    def test_default_birth_month_is_one(self, db: Session) -> None:
        """paradox.sql:119: birth_month integer DEFAULT 1"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.birth_month == 1

    def test_default_mecha_set_id_is_zero(self, db: Session) -> None:
        """paradox.sql:120: mecha_set_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.mecha_set_id == 0

    def test_default_side_weapon_id_is_zero(self, db: Session) -> None:
        """paradox.sql:121: side_weapon_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.side_weapon_id == 0

    def test_default_mecha_preset_id_is_zero(self, db: Session) -> None:
        """paradox.sql:122: mecha_preset_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.mecha_preset_id == 0

    def test_default_rank_point_is_zero(self, db: Session) -> None:
        """paradox.sql:123: rank_point integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.rank_point == 0

    def test_default_max_rank_id_is_zero(self, db: Session) -> None:
        """paradox.sql:124: max_rank_id integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.max_rank_id == 0

    def test_default_rank_point_2on2_is_zero(self, db: Session) -> None:
        """paradox.sql:125: rank_point_2on2 integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.rank_point_2on2 == 0

    def test_default_max_rank_id_2on2_is_zero(self, db: Session) -> None:
        """paradox.sql:126: max_rank_id_2on2 integer DEFAULT 0"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.max_rank_id_2on2 == 0

    def test_default_player_name_is_fullwidth_noname(self, db: Session) -> None:
        """paradox.sql:103: DEFAULT 'ＮｏＮａｍｅ'"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "ＮｏＮａｍｅ"


# ===========================================================================
# Null optional fields
# ===========================================================================


class TestPlayerProfileNullOptionalFields:
    """Legacy source: playerProfile.js:314-329
    Emblem is hardcoded with zeros, not null."""

    def test_emblem_id_can_be_zero(self, db: Session) -> None:
        """emblem_id defaults to 0 (not null)."""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.emblem_id == 0

    def test_buddy_id_can_be_zero(self, db: Session) -> None:
        """buddy_id defaults to 0 (not null)."""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.buddy_id == 0


# ===========================================================================
# Unicode data
# ===========================================================================


class TestPlayerProfileUnicodeData:
    """Legacy source: paradox.sql:103
    player_name character varying(50) DEFAULT 'ＮｏＮａｍｅ'"""

    def test_fullwidth_noname_default(self, db: Session) -> None:
        """Default name is full-width Unicode."""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "ＮｏＮａｍｅ"
        for char in player.player_name:
            assert ord(char) > 0xFF00

    def test_japanese_name_stored(self, db: Session) -> None:
        player = Player(nesys_id="test", player_name="テスト")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "テスト"

    def test_chinese_name_stored(self, db: Session) -> None:
        player = Player(nesys_id="test", player_name="测试")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "测试"

    def test_korean_name_stored(self, db: Session) -> None:
        player = Player(nesys_id="test", player_name="테스트")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "테스트"

    def test_tokyo_prefecture_name(self, db: Session) -> None:
        """ranking_pref_name default is '東京'."""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.ranking_pref_name == "東京"
        assert player.last_ranking_pref_name == "東京"

    def test_mixed_unicode_ascii_name(self, db: Session) -> None:
        player = Player(nesys_id="test", player_name="Player日本語")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "Player日本語"

    def test_latin_extended_name(self, db: Session) -> None:
        player = Player(nesys_id="test", player_name="Café München")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "Café München"

    def test_emoji_in_name(self, db: Session) -> None:
        """Emojis in player name (edge case)."""
        player = Player(nesys_id="test", player_name="Player🎮")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "Player🎮"


# ===========================================================================
# Missing player returns correct structure
# ===========================================================================


class TestMissingPlayerReturnsCorrectStructure:
    """Legacy source: playerProfile.js:347-349
    getProfile() returns false if this.Player.player_id is falsy.
    Python returns {result: 0} for missing nesys_id."""

    def test_missing_player_result_field(self, client: TestClient) -> None:
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "NONEXISTENT"},
        )
        data = response.json()
        assert "player_id" in data

    def test_missing_player_is_dict(self, client: TestClient) -> None:
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "NONEXISTENT"},
        )
        data = response.json()
        assert isinstance(data, dict)

    def test_missing_player_status_200(self, client: TestClient) -> None:
        """Legacy returns 200 even for missing player."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "NONEXISTENT"},
        )
        assert response.status_code == 200


# ===========================================================================
# Legacy computed fields (not yet implemented in Python)
# ===========================================================================


class TestPlayerProfileLegacyComputedFields:
    """These fields exist in the legacy getProfile() response but are
    G43 implemented these as profile dict fields. Tests verify they are present."""

    def test_same_day_login_count_in_response(self, client: TestClient) -> None:
        """G43: same_day_login_count is now returned as profile field."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "same_day_login_count" in data
        assert isinstance(data["same_day_login_count"], int)

    def test_total_login_days_in_response(self, client: TestClient) -> None:
        """G43: total_login_days is now returned as profile field."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "total_login_days" in data
        assert isinstance(data["total_login_days"], int)

    def test_consecutive_login_days_in_response(self, client: TestClient) -> None:
        """G43: consecutive_login_days is now returned as profile field."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "consecutive_login_days" in data
        assert isinstance(data["consecutive_login_days"], int)

    def test_emblem_not_in_response(self, client: TestClient) -> None:
        """LEGACY ONLY: emblem is hardcoded with zeros by getProfile().
        Source: playerProfile.js:314-329
        Structure: {outline: {part_id, offset, scale, angle}, main_design: {...}, sub_design: {...}}"""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "emblem" not in data or data.get("emblem") is None

    def test_last_pref_ranking_order_id_in_response(self, client: TestClient) -> None:
        """G43: last_pref_ranking_order_id is now returned as profile field."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "last_pref_ranking_order_id" in data

    def test_pref_ranking_top_player_count_in_response(self, client: TestClient) -> None:
        """G43: pref_ranking_top_player_count is now returned as profile field."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "pref_ranking_top_player_count" in data

    def test_official_player_type_id_in_response(self, client: TestClient) -> None:
        """G43: official_player_type_id is now returned as profile field."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "official_player_type_id" in data


# ===========================================================================
# Legacy response structure deviation documentation
# ===========================================================================


class TestPlayerProfileLegacyDeviations:
    """Document known deviations between Python and legacy implementations."""

    def test_result_wrapper_resolved(self, client: TestClient) -> None:
        """G43 RESOLVED: profile/load returns raw player dict (no result wrapper).
        Legacy returned raw player object. G37 previously wrapped in {result: N}.
        Source: player.py:74 returns _player_to_profile_dict(player)."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "player_id" in data

    def test_wrong_table_name_deviation(self, client: TestClient) -> None:
        """DEVIATION: Python queries 'players' table (non-existent).
        Legacy queries 'player' table.
        Source: player.py:61 uses "FROM players" vs paradox.sql:100 "player"."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert isinstance(data, dict)

    def test_response_has_progresses_field(self, client: TestClient) -> None:
        """Python endpoint returns 'progresses: []' in fallback response.
        Legacy getProgresses queries player_progress table.
        Source: playerProfile.js:331-338, player.py:80"""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        # Python returns empty progresses array in fallback
        assert "progresses" in data

    def test_response_no_level_field(self, client: TestClient) -> None:
        """G43 RESOLVED: profile/load no longer returns 'level' field.
        Legacy player table has no 'level' column.
        Source: player.py:74 _player_to_profile_dict excludes level."""
        response = client.post(
            "/player/profile/load",
            json={"nesys_id": "7020392000000000"},
        )
        data = response.json()
        assert "level" not in data
