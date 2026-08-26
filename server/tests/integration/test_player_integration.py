"""Player integration tests for the Starwing Paradox Python server.

These tests run against a real PostgreSQL database. They are skipped with
a clear reason when:
  - TEST_DATABASE_URL is not set
  - The database name does not end with _test suffix
  - PostgreSQL is unreachable

Environment:
    TEST_DATABASE_URL=postgresql+psycopg://paradox:changeme@localhost:5432/paradox_test

Source: legacy-js/paradox.sql, legacy-js/js/starwing/playerProfile.js
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

pytestmark = [pytest.mark.integration, pytest.mark.db]


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")


def _get_db_name(url: str) -> str:
    """Extract database name from URL."""
    parsed = urlparse(url)
    return parsed.path.lstrip("/")


def _db_available() -> bool:
    """Check if TEST_DATABASE_URL is set and valid."""
    if not TEST_DATABASE_URL:
        return False
    db_name = _get_db_name(TEST_DATABASE_URL)
    return db_name.endswith("_test")


def _connect_engine():
    """Create engine and attempt connection. Returns engine or raises."""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def db_engine():
    """Provide a SQLAlchemy engine connected to the test database.

    Skips all tests in this module if:
      - TEST_DATABASE_URL not set
      - Database name doesn't end with _test
      - PostgreSQL is unreachable
    """
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL environment variable not set")
    db_name = _get_db_name(TEST_DATABASE_URL)
    if not db_name.endswith("_test"):
        pytest.skip(f"Database name must end with '_test' suffix for safety. Got: {db_name}")
    try:
        engine = _connect_engine()
    except Exception as e:
        pytest.skip(f"PostgreSQL unavailable: {e}")
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def db_session(db_engine) -> Session:
    """Provide a transactional database session that rolls back after tests.

    Uses a single connection + transaction per module to isolate test data.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


# ---------------------------------------------------------------------------
# Tests: Player CRUD Operations
# ---------------------------------------------------------------------------


class TestPlayerCRUD:
    """Test player CRUD operations against real PostgreSQL.

    Source: legacy-js/js/starwing/playerProfile.js
    """

    def test_create_player(self, db_session) -> None:
        """INSERT INTO player (nesys_id) VALUES (:nesys) — new player creation."""
        result = db_session.execute(
            text(
                "INSERT INTO player (nesys_id, player_name) "
                "VALUES (:nesys, :name) RETURNING player_id"
            ),
            {"nesys": "TESTNESYS99999", "name": "IntegrationTestPlayer"},
        )
        player_id = result.scalar()
        db_session.flush()
        assert player_id is not None
        assert isinstance(player_id, int)

    def test_read_player_fields(self, db_session) -> None:
        """Read all core player fields from seed data player 10010."""
        result = db_session.execute(
            text(
                "SELECT player_id, nesys_id, player_name, rank_id, title_id, "
                "buddy_id, line_color_id, emblem_id, mecha_set_id, rank_point "
                "FROM player WHERE player_id = :pid"
            ),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == 10010
        assert row[1] == "7020392000000000"
        assert row[2] == "ArcadeMachinist"

    def test_update_player_name(self, db_session) -> None:
        """UPDATE player SET player_name = :name WHERE player_id = :pid."""
        db_session.execute(
            text("UPDATE player SET player_name = :name WHERE player_id = :pid"),
            {"pid": 10010, "name": "UpdatedName"},
        )
        db_session.flush()
        result = db_session.execute(
            text("SELECT player_name FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.fetchone()[0] == "UpdatedName"
        # Restore original
        db_session.execute(
            text("UPDATE player SET player_name = :name WHERE player_id = :pid"),
            {"pid": 10010, "name": "ArcadeMachinist"},
        )
        db_session.flush()

    def test_update_player_rank(self, db_session) -> None:
        """UPDATE player SET rank_point = :rp WHERE player_id = :pid."""
        db_session.execute(
            text("UPDATE player SET rank_point = :rp WHERE player_id = :pid"),
            {"pid": 10010, "rp": 9999},
        )
        db_session.flush()
        result = db_session.execute(
            text("SELECT rank_point FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.fetchone()[0] == 9999
        # Restore original
        db_session.execute(
            text("UPDATE player SET rank_point = :rp WHERE player_id = :pid"),
            {"pid": 10010, "rp": 0},
        )
        db_session.flush()

    def test_delete_player_by_id(self, db_session) -> None:
        """DELETE FROM player WHERE player_id = :pid — cascade delete test."""
        # Insert temp player
        db_session.execute(
            text("INSERT INTO player (nesys_id, player_name) VALUES (:nesys, :name)"),
            {"nesys": "DELETE_ME_001", "name": "ToDelete"},
        )
        db_session.flush()
        result = db_session.execute(
            text("SELECT player_id FROM player WHERE nesys_id = :nesys"),
            {"nesys": "DELETE_ME_001"},
        )
        pid = result.fetchone()[0]
        db_session.execute(text("DELETE FROM player WHERE player_id = :pid"), {"pid": pid})
        db_session.flush()
        result = db_session.execute(
            text("SELECT player_id FROM player WHERE player_id = :pid"), {"pid": pid}
        )
        assert result.fetchone() is None

    def test_player_nesys_id_uniqueness(self, db_session) -> None:
        """nesys_id should be unique per player — legacy paradox.sql constraint."""
        # Attempting to insert a duplicate nesys_id should fail
        with pytest.raises(Exception, match="UNIQUE"):
            db_session.execute(
                text("INSERT INTO player (nesys_id) VALUES (:nesys)"),
                {"nesys": "7020392000000000"},  # Already exists for player 10010
            )
            db_session.flush()

    def test_player_default_values(self, db_session) -> None:
        """New player should have sensible defaults."""
        result = db_session.execute(
            text(
                "INSERT INTO player (nesys_id) VALUES (:nesys) "
                "RETURNING rank_id, title_id, buddy_id, line_color_id, rank_point"
            ),
            {"nesys": "DEFAULT_TEST_001"},
        )
        row = result.fetchone()
        db_session.flush()
        # Defaults should be 0 for numeric fields
        assert row[0] == 0  # rank_id
        assert row[1] == 0  # title_id
        assert row[2] == 0  # buddy_id
        assert row[3] == 0  # line_color_id
        assert row[4] == 0  # rank_point

    def test_player_count(self, db_session) -> None:
        """Verify expected number of seed players."""
        result = db_session.execute(text("SELECT COUNT(*) FROM player"))
        count = result.scalar()
        assert count >= 2, f"Expected at least 2 seed players, got {count}"


# ---------------------------------------------------------------------------
# Tests: Player Progress (Credit/Progress)
# ---------------------------------------------------------------------------


class TestPlayerProgress:
    """Test player progress (credit/progress) operations.

    Source: legacy-js/js/starwing/playerProfile.js (progress saving)
    """

    def test_upsert_progress_insert(self, db_session) -> None:
        """ON CONFLICT DO UPDATE — insert new progress key."""
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status) "
                "ON CONFLICT (player_id, progress_key) DO UPDATE "
                "SET status = excluded.status"
            ),
            {"pid": 10010, "key": "test_credit_key_1", "status": 1},
        )
        db_session.flush()
        result = db_session.execute(
            text(
                "SELECT status FROM player_progress WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": "test_credit_key_1"},
        )
        assert result.fetchone()[0] == 1

    def test_upsert_progress_update(self, db_session) -> None:
        """ON CONFLICT DO UPDATE — update existing progress key."""
        # Insert
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status) "
                "ON CONFLICT (player_id, progress_key) DO UPDATE "
                "SET status = excluded.status"
            ),
            {"pid": 10010, "key": "test_credit_key_2", "status": 5},
        )
        db_session.flush()
        # Upsert with new value
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status) "
                "ON CONFLICT (player_id, progress_key) DO UPDATE "
                "SET status = excluded.status"
            ),
            {"pid": 10010, "key": "test_credit_key_2", "status": 10},
        )
        db_session.flush()
        result = db_session.execute(
            text(
                "SELECT status FROM player_progress WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": "test_credit_key_2"},
        )
        assert result.fetchone()[0] == 10

    def test_read_progress(self, db_session) -> None:
        """Read progress status for a player."""
        result = db_session.execute(
            text(
                "SELECT status FROM player_progress WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": "test_credit_key_1"},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] in (1, 10)  # Depending on test order

    def test_progress_count_per_player(self, db_session) -> None:
        """COUNT progress keys for a player."""
        result = db_session.execute(
            text("SELECT COUNT(*) FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        count = result.scalar()
        assert count >= 0  # May be 0 if no progress seeded

    def test_delete_progress(self, db_session) -> None:
        """DELETE FROM player_progress WHERE player_id = :pid AND progress_key = :key."""
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 10010, "key": "to_delete_key", "status": 1},
        )
        db_session.flush()
        db_session.execute(
            text("DELETE FROM player_progress WHERE player_id = :pid AND progress_key = :key"),
            {"pid": 10010, "key": "to_delete_key"},
        )
        db_session.flush()
        result = db_session.execute(
            text(
                "SELECT COUNT(*) FROM player_progress "
                "WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": "to_delete_key"},
        )
        assert result.scalar() == 0

    def test_progress_key_max_length(self, db_session) -> None:
        """progress_key column supports up to 35 characters."""
        long_key = "A" * 35
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 10010, "key": long_key, "status": 1},
        )
        db_session.flush()
        result = db_session.execute(
            text(
                "SELECT progress_key FROM player_progress "
                "WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": long_key},
        )
        assert result.fetchone()[0] == long_key


# ---------------------------------------------------------------------------
# Tests: Player Missions
# ---------------------------------------------------------------------------


class TestPlayerMissions:
    """Test player mission operations against real PostgreSQL.

    Source: legacy-js/paradox.sql (player_missions table)
    """

    def test_insert_mission(self, db_session) -> None:
        """INSERT INTO player_missions (player_id, mission_id, clear_count, status)."""
        db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 1, "cc": 0, "status": 0},
        )
        db_session.flush()
        result = db_session.execute(
            text(
                "SELECT clear_count, status FROM player_missions "
                "WHERE player_id = :pid AND mission_id = :mid"
            ),
            {"pid": 10010, "mid": 1},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == 0
        assert row[1] == 0

    def test_upsert_mission(self, db_session) -> None:
        """ON CONFLICT (player_id, mission_id) DO UPDATE — update clear_count."""
        # Insert
        db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status) "
                "ON CONFLICT (player_id, mission_id) DO UPDATE "
                "SET clear_count = excluded.clear_count, status = excluded.status"
            ),
            {"pid": 10010, "mid": 2, "cc": 3, "status": 1},
        )
        db_session.flush()
        # Upsert with new values
        db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status) "
                "ON CONFLICT (player_id, mission_id) DO UPDATE "
                "SET clear_count = excluded.clear_count, status = excluded.status"
            ),
            {"pid": 10010, "mid": 2, "cc": 5, "status": 2},
        )
        db_session.flush()
        result = db_session.execute(
            text(
                "SELECT clear_count, status FROM player_missions "
                "WHERE player_id = :pid AND mission_id = :mid"
            ),
            {"pid": 10010, "mid": 2},
        )
        row = result.fetchone()
        assert row[0] == 5
        assert row[1] == 2

    def test_read_mission(self, db_session) -> None:
        """Read mission data for a player."""
        result = db_session.execute(
            text(
                "SELECT mission_id, clear_count, status FROM player_missions "
                "WHERE player_id = :pid AND mission_id = :mid"
            ),
            {"pid": 10010, "mid": 2},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == 2

    def test_delete_mission(self, db_session) -> None:
        """DELETE FROM player_missions WHERE player_id = :pid AND mission_id = :mid."""
        db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 999, "cc": 0, "status": 0},
        )
        db_session.flush()
        db_session.execute(
            text("DELETE FROM player_missions WHERE player_id = :pid AND mission_id = :mid"),
            {"pid": 10010, "mid": 999},
        )
        db_session.flush()
        result = db_session.execute(
            text(
                "SELECT COUNT(*) FROM player_missions WHERE player_id = :pid AND mission_id = :mid"
            ),
            {"pid": 10010, "mid": 999},
        )
        assert result.scalar() == 0

    def test_mission_count_per_player(self, db_session) -> None:
        """COUNT missions for a player."""
        result = db_session.execute(
            text("SELECT COUNT(*) FROM player_missions WHERE player_id = :pid"),
            {"pid": 10010},
        )
        count = result.scalar()
        assert count >= 1  # At least the ones we inserted

    def test_mission_unique_constraint(self, db_session) -> None:
        """Unique constraint on (player_id, mission_id) prevents duplicates."""
        # Insert first
        db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 500, "cc": 1, "status": 1},
        )
        db_session.flush()
        # Attempt duplicate should fail
        with pytest.raises(Exception, match="UNIQUE"):
            db_session.execute(
                text(
                    "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                    "VALUES (:pid, :mid, :cc, :status)"
                ),
                {"pid": 10010, "mid": 500, "cc": 2, "status": 2},
            )
            db_session.flush()
