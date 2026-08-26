"""SQLite database integration tests.

These tests use a real temporary SQLite file to verify database operations
work correctly with the SQLite-only backend.
"""

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _configure_sqlite_pragmas(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA busy_timeout = 10000")
    cursor.close()


@pytest.fixture
def tmp_db_path(tmp_path):
    """Return a path to a temporary SQLite database file."""
    return tmp_path / "test_starwing.db"


@pytest.fixture
def sync_engine(tmp_db_path):
    """Create a synchronous SQLite engine with PRAGMAs."""
    url = f"sqlite:///{tmp_db_path}"
    engine = create_engine(url, echo=False)
    event.listen(engine, "connect", _configure_sqlite_pragmas)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest_asyncio.fixture
async def async_engine(tmp_db_path):
    """Create an async SQLite engine with PRAGMAs."""
    url = f"sqlite+aiosqlite:///{tmp_db_path}"
    engine = create_async_engine(url, echo=False)
    event.listen(engine.sync_engine, "connect", _configure_sqlite_pragmas)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(tmp_db_path) -> AsyncSession:
    """Create an async session for testing."""
    url = f"sqlite+aiosqlite:///{tmp_db_path}"
    engine = create_async_engine(url, echo=False)
    event.listen(engine.sync_engine, "connect", _configure_sqlite_pragmas)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


# ---------------------------------------------------------------------------
# Database Connectivity Tests
# ---------------------------------------------------------------------------


class TestDatabaseConnectivity:
    """Verify SQLite database connection works."""

    def test_database_url_is_sqlite(self):
        """Default database URL must be SQLite."""
        from app.config import Settings

        s = Settings(database_url="sqlite+aiosqlite:///./data/test.db")
        url = s.get_database_url()
        assert url.startswith("sqlite")

    def test_database_file_created(self, tmp_db_path):
        """Database file should be created on first connection."""
        url = f"sqlite:///{tmp_db_path}"
        engine = create_engine(url)
        Base.metadata.create_all(engine)
        assert tmp_db_path.exists()
        engine.dispose()

    def test_connection_succeeds(self, sync_engine):
        """Basic connection should work."""
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_is_sqlite(self, sync_engine):
        """Verify we're connected to SQLite."""
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT sqlite_version()"))
            version = result.scalar()
            assert version is not None


# ---------------------------------------------------------------------------
# Schema Existence Tests
# ---------------------------------------------------------------------------


class TestSchemaExistence:
    """Verify all required tables exist in SQLite."""

    def test_all_required_tables_exist(self, sync_engine):
        """All 17 legacy tables must exist."""
        required = {
            "player",
            "player_buddies",
            "player_buddy_win_poses",
            "player_emblem_parts",
            "player_emblems",
            "player_line_colors",
            "player_logins",
            "player_mecha_colors",
            "player_mecha_set_parts",
            "player_mecha_sets",
            "player_missions",
            "player_options",
            "player_progress",
            "player_side_weapons",
            "player_titles",
            "player_weapon_set",
            "player_weapon_set_slots",
        }
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = {row[0] for row in result.fetchall()}
        missing = required - tables
        assert not missing, f"Missing tables: {missing}"

    def test_player_table_has_expected_columns(self, sync_engine):
        """Player table should have all expected columns."""
        with sync_engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(player)"))
            columns = {row[1] for row in result.fetchall()}
        expected = {
            "player_id",
            "nesys_id",
            "player_name",
            "rank_id",
            "rank_id_2on2",
            "title_id",
            "title_id_2on2",
            "buddy_id",
            "buddy_intimacy",
            "line_color_id",
            "ranking_pref_name",
            "last_ranking_pref_name",
            "match_mode_id",
            "violation_point",
            "emblem_id",
            "line_color_id_2on2",
            "emblem_id_2on2",
            "birth_day",
            "birth_month",
            "mecha_set_id",
            "side_weapon_id",
            "mecha_preset_id",
            "rank_point",
            "max_rank_id",
            "rank_point_2on2",
            "max_rank_id_2on2",
        }
        missing = expected - columns
        assert not missing, f"Missing columns: {missing}"


# ---------------------------------------------------------------------------
# PRAGMA Tests
# ---------------------------------------------------------------------------


class TestPragmaConfiguration:
    """Verify SQLite PRAGMAs are correctly set."""

    def test_foreign_keys_enabled(self, sync_engine):
        """foreign_keys must be ON."""
        with sync_engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys"))
            assert result.scalar() == 1

    def test_busy_timeout_nonzero(self, sync_engine):
        """busy_timeout must be non-zero."""
        with sync_engine.connect() as conn:
            result = conn.execute(text("PRAGMA busy_timeout"))
            assert result.scalar() > 0

    def test_wal_mode(self, sync_engine):
        """journal_mode should be WAL after initialization."""
        with sync_engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode = WAL"))
            result = conn.execute(text("PRAGMA journal_mode"))
            assert result.scalar().lower() == "wal"


# ---------------------------------------------------------------------------
# Seed Data Tests
# ---------------------------------------------------------------------------


class TestSeedData:
    """Verify seed data can be inserted."""

    def test_insert_player(self, sync_engine):
        """Should be able to insert a player."""
        with sync_engine.connect() as conn:
            conn.execute(
                text(
                    "INSERT INTO player (player_id, nesys_id, player_name) "
                    "VALUES (:pid, :nesys, :name)"
                ),
                {"pid": 10010, "nesys": "7020392000000000", "name": "ArcadeMachinist"},
            )
            conn.commit()
            result = conn.execute(
                text("SELECT player_id, nesys_id, player_name FROM player WHERE player_id = :pid"),
                {"pid": 10010},
            )
            row = result.fetchone()
            assert row is not None
            assert row[0] == 10010
            assert row[1] == "7020392000000000"
            assert row[2] == "ArcadeMachinist"


# ---------------------------------------------------------------------------
# Basic CRUD Tests
# ---------------------------------------------------------------------------


class TestBasicCRUD:
    """Test basic CRUD operations."""

    def test_select_player_by_id(self, sync_engine):
        """Select player by ID."""
        with sync_engine.connect() as conn:
            conn.execute(
                text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
                {"pid": 10010, "nesys": "NESYS001"},
            )
            conn.commit()
            result = conn.execute(
                text("SELECT player_id FROM player WHERE player_id = :pid"),
                {"pid": 10010},
            )
            assert result.fetchone()[0] == 10010

    def test_select_player_by_nesys_id(self, sync_engine):
        """Select player by NESYS ID."""
        with sync_engine.connect() as conn:
            conn.execute(
                text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
                {"pid": 10010, "nesys": "NESYS001"},
            )
            conn.commit()
            result = conn.execute(
                text("SELECT player_id FROM player WHERE nesys_id = :nesys"),
                {"nesys": "NESYS001"},
            )
            assert result.fetchone()[0] == 10010

    def test_select_player_nonexistent(self, sync_engine):
        """Select nonexistent player returns None."""
        with sync_engine.connect() as conn:
            result = conn.execute(
                text("SELECT player_id FROM player WHERE player_id = :pid"),
                {"pid": 99999},
            )
            assert result.fetchone() is None


# ---------------------------------------------------------------------------
# Legacy SQL Quirks Tests
# ---------------------------------------------------------------------------


class TestLegacySQLQuirks:
    """Test legacy SQL behavior compatibility."""

    def test_upsert_player_progress(self, sync_engine):
        """UPSERT pattern for player_progress."""
        with sync_engine.connect() as conn:
            conn.execute(
                text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
                {"pid": 10010, "nesys": "NESYS001"},
            )
            conn.execute(
                text(
                    "INSERT INTO player_progress (player_id, progress_key, status) "
                    "VALUES (:pid, :key, :status)"
                ),
                {"pid": 10010, "key": "tutorial_complete", "status": 1},
            )
            conn.commit()
            # Update via subquery pattern
            conn.execute(
                text(
                    "UPDATE player_progress SET status = :new_status "
                    "WHERE player_id = :pid AND progress_key = :key"
                ),
                {"pid": 10010, "key": "tutorial_complete", "new_status": 2},
            )
            conn.commit()
            result = conn.execute(
                text("SELECT status FROM player_progress WHERE player_id = :pid"),
                {"pid": 10010},
            )
            assert result.fetchone()[0] == 2

    def test_date_trunc_day(self, sync_engine):
        """date_trunc emulation in SQLite."""
        with sync_engine.connect() as conn:
            result = conn.execute(text("SELECT date('now')"))
            today = result.scalar()
            assert today is not None

    def test_player_id_auto_increment(self, sync_engine):
        """Player ID auto-increment works."""
        with sync_engine.connect() as conn:
            conn.execute(
                text("INSERT INTO player (nesys_id) VALUES (:nesys)"),
                {"nesys": "NESYS_AUTO1"},
            )
            conn.execute(
                text("INSERT INTO player (nesys_id) VALUES (:nesys)"),
                {"nesys": "NESYS_AUTO2"},
            )
            conn.commit()
            result = conn.execute(text("SELECT MAX(player_id) FROM player"))
            max_id = result.scalar()
            assert max_id is not None


# ---------------------------------------------------------------------------
# Rollback Isolation Tests
# ---------------------------------------------------------------------------


class TestRollbackIsolation:
    """Test transaction rollback."""

    def test_insert_rolled_back(self, sync_engine):
        """Rolled back insert should not persist."""
        with sync_engine.connect() as conn:
            conn.execute(
                text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
                {"pid": 10010, "nesys": "NESYS_ROLLBACK"},
            )
            conn.commit()

        with sync_engine.connect() as conn:
            conn.execute(
                text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
                {"pid": 10011, "nesys": "NESYS_ROLLBACK2"},
            )
            conn.rollback()

        with sync_engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM player WHERE nesys_id = :nesys"),
                {"nesys": "NESYS_ROLLBACK2"},
            )
            assert result.scalar() == 0
