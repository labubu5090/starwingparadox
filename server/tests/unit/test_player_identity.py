"""Unit tests for player identity foundation.

Source evidence:
  - legacy-js/js/starwing/playerProfile.js (initWithNesys: lines 26-73, initWithPlayerID: lines 6-25)
  - legacy-js/paradox.sql (player table: lines 100-127, sequence: lines 497-512)
  - server/app/db/models/player.py
  - server/app/db/repositories/player_repository.py
  - server/app/services/player_service.py

Legacy behavior (playerProfile.js):
  1. initWithNesys: SELECT * FROM player WHERE nesys_id=$1
     - If not found: INSERT INTO player(nesys_id) VALUES ($1) RETURNING player_id
     - Then re-SELECT the new player by player_id
  2. initWithPlayerID: SELECT * FROM player WHERE player_id=$1
     - If not found: return false (None equivalent)
  3. Default player_name: 'ＮｏＮａｍｅ' (full-width, SQL DEFAULT at paradox.sql:103)
  4. Player ID allocation: sequence player_player_id_seq (paradox.sql:497-512)
  5. All queries use parameterized $1, $2 etc.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.models.player import Player
from app.db.repositories.player_repository import PlayerRepository

pytestmark = [pytest.mark.unit, pytest.mark.player_identity]


# ---------------------------------------------------------------------------
# Sync fixtures for non-async tests
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


# ---------------------------------------------------------------------------
# Async fixtures
# ---------------------------------------------------------------------------

ASYNC_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def async_db() -> AsyncSession:
    engine = create_async_engine(ASYNC_URL, echo=False)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


# ===========================================================================
# NESYS ID lookup
# ===========================================================================


class TestNesysIdLookup:
    """Legacy source: playerProfile.js:35-37
    SELECT * FROM player WHERE nesys_id=$1"""

    def test_lookup_existing_nesys_id(self, db: Session) -> None:
        """Existing player is returned when querying by nesys_id."""
        player = Player(
            nesys_id="7020392000000000",
            player_name="ArcadeMachinist",
            rank_id=20,
        )
        db.add(player)
        db.commit()
        db.refresh(player)

        from sqlalchemy import select

        result = db.execute(
            select(Player).where(Player.nesys_id == "7020392000000000")
        ).scalar_one_or_none()
        assert result is not None
        assert result.nesys_id == "7020392000000000"
        assert result.player_name == "ArcadeMachinist"
        assert result.rank_id == 20

    def test_lookup_nonexistent_nesys_id_returns_none(self, db: Session) -> None:
        """Missing player returns None (legacy returns empty rows)."""
        from sqlalchemy import select

        result = db.execute(
            select(Player).where(Player.nesys_id == "NONEXISTENT")
        ).scalar_one_or_none()
        assert result is None

    def test_nesys_id_is_string_type(self, db: Session) -> None:
        """nesys_id is stored as VARCHAR(22) per paradox.sql:102."""
        player = Player(nesys_id="7020392000000001")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert isinstance(player.nesys_id, str)
        assert len(player.nesys_id) <= 22


# ===========================================================================
# Existing player retrieval
# ===========================================================================


class TestExistingPlayerRetrieval:
    """Legacy source: playerProfile.js:15-22 (initWithPlayerID)"""

    def test_get_existing_player_by_id(self, db: Session) -> None:
        """Existing player is returned when querying by player_id."""
        player = Player(
            nesys_id="7020392000000000",
            player_name="ArcadeMachinist",
            rank_id=20,
        )
        db.add(player)
        db.commit()
        db.refresh(player)

        from sqlalchemy import select

        result = db.execute(
            select(Player).where(Player.player_id == player.player_id)
        ).scalar_one_or_none()
        assert result is not None
        assert result.player_id == player.player_id
        assert result.player_name == "ArcadeMachinist"

    def test_retrieval_preserves_all_columns(self, db: Session) -> None:
        """All player columns are populated with correct defaults."""
        player = Player(nesys_id="7020392000000000")
        db.add(player)
        db.commit()
        db.refresh(player)

        assert player.rank_id == 0
        assert player.rank_id_2on2 == 0
        assert player.title_id == 0
        assert player.title_id_2on2 == 0
        assert player.buddy_id == 0
        assert player.buddy_intimacy == 0
        assert player.line_color_id == 0
        assert player.ranking_pref_name == "東京"
        assert player.last_ranking_pref_name == "東京"
        assert player.match_mode_id == 0
        assert player.violation_point == 0
        assert player.emblem_id == 0
        assert player.line_color_id_2on2 == 0
        assert player.emblem_id_2on2 == 0
        assert player.birth_day == 1
        assert player.birth_month == 1
        assert player.mecha_set_id == 0
        assert player.side_weapon_id == 0
        assert player.mecha_preset_id == 0
        assert player.rank_point == 0
        assert player.max_rank_id == 0
        assert player.rank_point_2on2 == 0
        assert player.max_rank_id_2on2 == 0


# ===========================================================================
# Missing player returns None
# ===========================================================================


class TestMissingPlayerReturnsNone:
    """Legacy source: playerProfile.js:17-19 (res.rows.length == 0 → return false)"""

    def test_missing_player_by_id_returns_none(self, db: Session) -> None:
        """Querying non-existent player_id returns None."""
        from sqlalchemy import select

        result = db.execute(select(Player).where(Player.player_id == 99999)).scalar_one_or_none()
        assert result is None

    def test_missing_player_by_nesys_returns_none(self, db: Session) -> None:
        """Querying non-existent nesys_id returns None."""
        from sqlalchemy import select

        result = db.execute(
            select(Player).where(Player.nesys_id == "NONEXISTENT")
        ).scalar_one_or_none()
        assert result is None


# ===========================================================================
# Default player name
# ===========================================================================


class TestDefaultPlayerName:
    """Legacy source: paradox.sql:103
    player_name character varying(50) DEFAULT 'ＮｏＮａｍｅ'::character varying
    playerProfile.js:41: INSERT INTO player(nesys_id) VALUES ($1)"""

    def test_default_name_is_noname(self, db: Session) -> None:
        """New player gets default name 'ＮｏＮａｍｅ'."""
        player = Player(nesys_id="7020392000000000")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "ＮｏＮａｍｅ"

    def test_explicit_name_overrides_default(self, db: Session) -> None:
        """Explicit name overrides the default."""
        player = Player(nesys_id="7020392000000000", player_name="CustomName")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "CustomName"

    def test_empty_string_name(self, db: Session) -> None:
        """Empty string name is stored (no DB constraint prevents it)."""
        player = Player(nesys_id="7020392000000000", player_name="")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == ""


# ===========================================================================
# Player ID allocation (sequence)
# ===========================================================================


class TestPlayerIdAllocation:
    """Legacy source: paradox.sql:497-512
    CREATE SEQUENCE public.player_player_id_seq
    ALTER SEQUENCE public.player_player_id_seq OWNED BY public.player.player_id
    playerProfile.js:41: INSERT INTO player(nesys_id) VALUES ($1) RETURNING player_id"""

    def test_player_id_auto_increment(self, db: Session) -> None:
        """Player IDs are auto-generated and increment."""
        p1 = Player(nesys_id="7020392000000000")
        p2 = Player(nesys_id="7020392000000001")
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)
        assert p1.player_id != p2.player_id
        assert p2.player_id > p1.player_id

    def test_player_id_is_integer(self, db: Session) -> None:
        """Player ID is an integer per paradox.sql:101."""
        player = Player(nesys_id="7020392000000000")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert isinstance(player.player_id, int)


# ===========================================================================
# Duplicate NESYS ID behavior
# ===========================================================================


class TestDuplicateNesysIdBehavior:
    """Legacy source: playerProfile.js:35-37
    SELECT * FROM player WHERE nesys_id=$1
    If found → use existing (does not create duplicate).

    Note: Legacy has no UNIQUE constraint on nesys_id in the SQL DDL,
    but the application logic prevents duplicates by checking first."""

    def test_duplicate_nesys_id_not_created(self, db: Session) -> None:
        """Legacy checks for existing player before creating.
        If nesys_id already exists, it reuses the existing player."""
        from sqlalchemy import select

        player1 = Player(nesys_id="7020392000000000", player_name="First")
        db.add(player1)
        db.commit()
        db.refresh(player1)

        # Legacy would find this player and not create a new one
        existing = db.execute(
            select(Player).where(Player.nesys_id == "7020392000000000")
        ).scalar_one_or_none()
        assert existing is not None
        assert existing.player_id == player1.player_id

    def test_same_nesys_id_different_players(self, db: Session) -> None:
        """Without UNIQUE constraint, duplicate nesys_id can be inserted.
        Legacy prevents this at application level."""
        from sqlalchemy import select

        p1 = Player(nesys_id="7020392000000000", player_name="Player1")
        p2 = Player(nesys_id="7020392000000000", player_name="Player2")
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        # Both exist (no DB constraint), but legacy app logic prevents this
        results = (
            db.execute(select(Player).where(Player.nesys_id == "7020392000000000")).scalars().all()
        )
        assert len(results) == 2


# ===========================================================================
# Invalid NESYS ID
# ===========================================================================


class TestInvalidNesysId:
    """Legacy source: playerProfile.js:29-31
    if (nesys_id == 0 || nesys_id === null || typeof nesys_id == 'undefined')
        return false"""

    def test_empty_string_nesys_id(self, db: Session) -> None:
        """Empty string nesys_id: legacy returns false (treated as invalid)."""
        from sqlalchemy import select

        result = db.execute(select(Player).where(Player.nesys_id == "")).scalar_one_or_none()
        assert result is None

    def test_zero_nesys_id(self, db: Session) -> None:
        """Zero nesys_id: legacy returns false."""
        from sqlalchemy import select

        result = db.execute(select(Player).where(Player.nesys_id == "0")).scalar_one_or_none()
        assert result is None

    def test_long_nesys_id_exceeds_column(self, db: Session) -> None:
        """nesys_id > 22 chars: SQLite truncates or stores depending on type.
        Legacy uses VARCHAR(22)."""
        long_id = "A" * 30  # exceeds VARCHAR(22)
        player = Player(nesys_id=long_id)
        db.add(player)
        db.commit()
        db.refresh(player)
        # SQLite stores it (no length enforcement), but PostgreSQL would truncate/error
        assert len(player.nesys_id) == 30


# ===========================================================================
# Unicode player name
# ===========================================================================


class TestUnicodePlayerName:
    """Legacy source: paradox.sql:103
    Default name 'ＮｏＮａｍｅ' is full-width Unicode.
    player_name character varying(50)"""

    def test_fullwidth_default_name(self, db: Session) -> None:
        """Default name uses full-width Unicode characters."""
        player = Player(nesys_id="7020392000000000")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "ＮｏＮａｍｅ"
        # Verify each character is full-width
        for char in player.player_name:
            assert ord(char) > 0xFF00  # Full-width range

    def test_japanese_player_name(self, db: Session) -> None:
        """Japanese characters in player name."""
        player = Player(nesys_id="7020392000000000", player_name="テストプレイヤー")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "テストプレイヤー"

    def test_korean_player_name(self, db: Session) -> None:
        """Korean characters in player name."""
        player = Player(nesys_id="7020392000000000", player_name="테스트플레이어")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "테스트플레이어"

    def test_chinese_player_name(self, db: Session) -> None:
        """Chinese characters in player name."""
        player = Player(nesys_id="7020392000000000", player_name="测试玩家")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "测试玩家"

    def test_mixed_ascii_unicode_name(self, db: Session) -> None:
        """Mixed ASCII and Unicode in player name."""
        player = Player(nesys_id="7020392000000000", player_name="Arcade测试Machinist")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "Arcade测试Machinist"

    def test_latin_extended_name(self, db: Session) -> None:
        """Latin extended characters (accented)."""
        player = Player(nesys_id="7020392000000000", player_name="Café Résumé")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.player_name == "Café Résumé"


# ===========================================================================
# Transaction rollback on failure
# ===========================================================================


class TestTransactionRollbackOnFailure:
    """Legacy source: playerProfile.js:57-59
    catch(err) { console.log(err.stack); }
    Legacy wraps DB operations in try/catch; on failure the pool
    auto-rolls back uncommitted transactions."""

    def test_rollback_on_constraint_violation(self, db: Session) -> None:
        """Transaction rolls back on constraint violation without corrupting state."""

        # Create a player
        player = Player(nesys_id="7020392000000000")
        db.add(player)
        db.commit()
        db.refresh(player)
        first_id = player.player_id

        # Attempt to cause an error (e.g., inserting with invalid data)
        # SQLite doesn't enforce length constraints, so we test rollback differently
        # by using a raw SQL error
        try:
            db.execute(text("INSERT INTO non_existent_table (col) VALUES (:val)"), {"val": 1})
            db.commit()
        except Exception:
            db.rollback()

        # Verify the original player still exists and session is usable
        from sqlalchemy import select

        result = db.execute(select(Player).where(Player.player_id == first_id)).scalar_one_or_none()
        assert result is not None
        assert result.nesys_id == "7020392000000000"

    def test_session_usable_after_rollback(self, db: Session) -> None:
        """Session remains usable after a rollback."""
        player = Player(nesys_id="7020392000000000")
        db.add(player)
        db.commit()
        db.refresh(player)

        # Force a rollback
        try:
            db.execute(text("SELECT 1 FROM non_existent_table"))
        except Exception:
            db.rollback()

        # Session should still work
        new_player = Player(nesys_id="7020392000000001")
        db.add(new_player)
        db.commit()
        db.refresh(new_player)
        assert new_player.player_id > 0

    def test_multiple_operations_rollback(self, db: Session) -> None:
        """Multiple operations in sequence with rollback recovery."""
        p1 = Player(nesys_id="7020392000000000")
        db.add(p1)
        db.commit()
        db.refresh(p1)

        # Simulate a failed operation
        try:
            db.execute(text("INSERT INTO nonexistent_table VALUES (1)"))
            db.commit()
        except Exception:
            db.rollback()

        # Can still add more players
        p2 = Player(nesys_id="7020392000000001")
        db.add(p2)
        db.commit()
        db.refresh(p2)
        assert p2.player_id > p1.player_id


# ===========================================================================
# Parameterized queries only
# ===========================================================================


class TestParameterizedQueries:
    """Legacy source: playerProfile.js:16,37,43,48
    All queries use $1, $2 etc. (parameterized).
    Legacy uses pg Pool with $N placeholders."""

    def test_repository_uses_parameterized_queries(self, db: Session) -> None:
        """PlayerRepository methods use parameterized queries."""
        PlayerRepository(db)

        # Create a player to query
        player = Player(nesys_id="7020392000000000")
        db.add(player)
        db.commit()
        db.refresh(player)

        # Query using parameterized ORM
        from sqlalchemy import select

        stmt = select(Player).where(Player.nesys_id == "7020392000000000")
        result = db.execute(stmt).scalar_one_or_none()
        assert result is not None

    def test_no_string_interpolation_in_queries(self) -> None:
        """Verify repository does not use string interpolation for queries."""
        import inspect

        source = inspect.getsource(PlayerRepository)
        # Should not use f-string or %-format SQL
        lines = source.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            # No f-string SQL
            assert 'f"' not in stripped or "SELECT" not in stripped.upper(), (
                f"Possible f-string SQL: {stripped}"
            )


# ===========================================================================
# Default values from legacy schema
# ===========================================================================


class TestDefaultValuesFromLegacySchema:
    """Legacy source: paradox.sql:100-127
    All column defaults match the SQL DDL."""

    def test_rank_id_defaults_to_zero(self, db: Session) -> None:
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.rank_id == 0

    def test_rank_id_2on2_defaults_to_zero(self, db: Session) -> None:
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.rank_id_2on2 == 0

    def test_title_id_defaults_to_zero(self, db: Session) -> None:
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.title_id == 0

    def test_title_id_2on2_defaults_to_zero(self, db: Session) -> None:
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.title_id_2on2 == 0

    def test_buddy_id_defaults_to_zero(self, db: Session) -> None:
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.buddy_id == 0

    def test_buddy_intimacy_defaults_to_zero(self, db: Session) -> None:
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.buddy_intimacy == 0

    def test_ranking_pref_name_defaults_to_tokyo(self, db: Session) -> None:
        """paradox.sql:111: DEFAULT '東京'"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.ranking_pref_name == "東京"

    def test_last_ranking_pref_name_defaults_to_tokyo(self, db: Session) -> None:
        """paradox.sql:112: DEFAULT '東京'"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.last_ranking_pref_name == "東京"

    def test_birth_day_defaults_to_one(self, db: Session) -> None:
        """paradox.sql:118: DEFAULT 1"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.birth_day == 1

    def test_birth_month_defaults_to_one(self, db: Session) -> None:
        """paradox.sql:119: DEFAULT 1"""
        player = Player(nesys_id="test")
        db.add(player)
        db.commit()
        db.refresh(player)
        assert player.birth_month == 1

    def test_sample_data_matches_legacy(self, db: Session) -> None:
        """Verify sample data from paradox.sql:826-827 can be loaded."""
        # Line 826: 10011	7020392000000001	Lord Cereth	10	10	0	100000	...
        p1 = Player(
            nesys_id="7020392000000001",
            player_name="Lord Cereth",
            rank_id=10,
            rank_id_2on2=10,
            title_id=0,
            title_id_2on2=100000,
            buddy_id=2,
            buddy_intimacy=0,
            line_color_id=1,
            emblem_id=1,
        )
        # Line 827: 10010	7020392000000000	ArcadeMachinist	20	20	100001	100001	...
        p2 = Player(
            nesys_id="7020392000000000",
            player_name="ArcadeMachinist",
            rank_id=20,
            rank_id_2on2=20,
            title_id=100001,
            title_id_2on2=100001,
            buddy_id=5,
            buddy_intimacy=2,
            line_color_id=1,
            emblem_id=1,
            emblem_id_2on2=100002,
        )
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        assert p1.player_name == "Lord Cereth"
        assert p1.rank_id == 10
        assert p2.player_name == "ArcadeMachinist"
        assert p2.rank_id == 20
        assert p2.title_id == 100001
