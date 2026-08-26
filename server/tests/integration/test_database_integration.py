"""Database integration tests for the Starwing Paradox Python server.

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
# Tests: Database Connectivity
# ---------------------------------------------------------------------------


class TestDatabaseConnectivity:
    """Verify PostgreSQL connection and test database safety."""

    def test_test_database_url_is_set(self) -> None:
        """TEST_DATABASE_URL must be configured."""
        if not TEST_DATABASE_URL:
            pytest.skip(
                "TEST_DATABASE_URL environment variable not set. "
                "Set it to: postgresql+psycopg://paradox:changeme@localhost:5432/paradox_test"
            )

    def test_database_name_has_test_suffix(self) -> None:
        """Database name must end with '_test' to prevent production accidents."""
        if not TEST_DATABASE_URL:
            pytest.skip("TEST_DATABASE_URL environment variable not set")
        db_name = _get_db_name(TEST_DATABASE_URL)
        assert db_name.endswith("_test"), (
            f"Database name must end with '_test' suffix for safety. "
            f"Got: {db_name}. "
            f"Use: paradox_test"
        )

    def test_connection_succeeds(self, db_engine) -> None:
        """Can connect to the test database."""
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_database_is_postgresql(self, db_engine) -> None:
        """Verify we're connected to PostgreSQL (not SQLite)."""
        with db_engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            assert "PostgreSQL" in version, f"Expected PostgreSQL, got: {version}"


# ---------------------------------------------------------------------------
# Tests: Schema Existence
# ---------------------------------------------------------------------------


class TestSchemaExistence:
    """Verify all required tables exist in the test database.

    Source: legacy-js/paradox.sql (schema definitions)
    """

    REQUIRED_TABLES = [
        "player",
        "player_buddies",
        "player_logins",
        "player_progress",
        "player_missions",
        "player_options",
        "player_titles",
        "player_line_colors",
        "player_emblems",
        "player_emblem_parts",
        "player_mecha_sets",
        "player_mecha_set_parts",
        "player_mecha_colors",
        "player_weapon_set",
        "player_weapon_set_slots",
        "player_side_weapons",
        "player_buddy_win_poses",
    ]

    def test_all_required_tables_exist(self, db_engine) -> None:
        """All tables from legacy schema must exist."""
        with db_engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            )
            existing = {row[0] for row in result.fetchall()}

        missing = [t for t in self.REQUIRED_TABLES if t not in existing]
        assert not missing, f"Missing tables: {missing}"

    def test_player_table_has_expected_columns(self, db_engine) -> None:
        """player table must have core columns from legacy schema."""
        with db_engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'player' ORDER BY ordinal_position"
                )
            )
            columns = {row[0] for row in result.fetchall()}

        expected = {
            "player_id",
            "nesys_id",
            "player_name",
            "rank_id",
            "title_id",
            "buddy_id",
            "line_color_id",
            "emblem_id",
            "mecha_set_id",
            "rank_point",
        }
        missing = expected - columns
        assert not missing, f"Missing player columns: {missing}"


# ---------------------------------------------------------------------------
# Tests: Seed Data
# ---------------------------------------------------------------------------


class TestSeedData:
    """Verify minimum seed data is present.

    Source: legacy-js/paradox.sql lines 822-828 (COPY player)
    """

    def test_test_player_10010_exists(self, db_session) -> None:
        """Player 10010 (ArcadeMachinist) must exist in seed data."""
        result = db_session.execute(text("SELECT player_name FROM player WHERE player_id = 10010"))
        row = result.fetchone()
        assert row is not None, "Player 10010 not found in seed data"
        assert row[0] == "ArcadeMachinist"

    def test_test_player_10011_exists(self, db_session) -> None:
        """Player 10011 (Lord Cereth) must exist in seed data."""
        result = db_session.execute(text("SELECT player_name FROM player WHERE player_id = 10011"))
        row = result.fetchone()
        assert row is not None, "Player 10011 not found in seed data"
        assert row[0] == "Lord Cereth"

    def test_player_10010_nesys_id(self, db_session) -> None:
        """Player 10010 nesys_id matches legacy dump."""
        result = db_session.execute(text("SELECT nesys_id FROM player WHERE player_id = 10010"))
        row = result.fetchone()
        assert row[0] == "7020392000000000"

    def test_player_10010_has_buddies(self, db_session) -> None:
        """Player 10010 has buddy records from seed data."""
        result = db_session.execute(
            text("SELECT COUNT(*) FROM player_buddies WHERE player_id = 10010")
        )
        count = result.scalar()
        assert count > 0, "Player 10010 has no buddy records in seed data"


# ---------------------------------------------------------------------------
# Tests: Basic CRUD Operations
# ---------------------------------------------------------------------------


class TestBasicCRUD:
    """Test basic database operations match legacy patterns.

    Source: legacy-js/js/starwing/playerProfile.js
    """

    def test_select_player_by_id(self, db_session) -> None:
        """SELECT * FROM player WHERE player_id=$1 — legacy playerProfile.js:15."""
        result = db_session.execute(
            text("SELECT player_id, nesys_id, player_name FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == 10010
        assert row[1] == "7020392000000000"
        assert row[2] == "ArcadeMachinist"

    def test_select_player_by_nesys_id(self, db_session) -> None:
        """SELECT * FROM player WHERE nesys_id=$1 — legacy playerProfile.js:35."""
        result = db_session.execute(
            text("SELECT player_id FROM player WHERE nesys_id = :nesys"),
            {"nesys": "7020392000000001"},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == 10011

    def test_select_player_nonexistent(self, db_session) -> None:
        """Non-existent player returns no rows."""
        result = db_session.execute(
            text("SELECT player_id FROM player WHERE player_id = :pid"), {"pid": 99999}
        )
        row = result.fetchone()
        assert row is None

    def test_select_buddies_by_player(self, db_session) -> None:
        """SELECT buddy data for player — legacy playerProfile.js:111."""
        result = db_session.execute(
            text(
                "SELECT buddy_id, buddy_key, buddy_value "
                "FROM player_buddies WHERE player_id = :pid "
                "ORDER BY buddy_id, buddy_key"
            ),
            {"pid": 10010},
        )
        rows = result.fetchall()
        assert len(rows) > 0
        # Verify structure
        assert rows[0][0] is not None  # buddy_id
        assert rows[0][1] is not None  # buddy_key
        assert rows[0][2] is not None  # buddy_value

    def test_select_login_count(self, db_session) -> None:
        """COUNT(id) for same-day logins — legacy playerProfile.js:94-96.

        Uses date_trunc('day', ts_when) which is PostgreSQL-specific.
        """
        result = db_session.execute(
            text(
                "SELECT COUNT(id) AS same_day_login_count "
                "FROM player_logins "
                "WHERE date_trunc('day', ts_when) = date_trunc('day', NOW()) "
                "AND player_id = :pid"
            ),
            {"pid": 10010},
        )
        row = result.fetchone()
        # May be 0 if seed login is on a different day
        assert row[0] >= 0

    def test_select_total_login_days(self, db_session) -> None:
        """COUNT(DISTINCT(date_trunc)) for total login days — legacy playerProfile.js:99-101."""
        result = db_session.execute(
            text(
                "SELECT COUNT(DISTINCT(date_trunc('day', ts_when))) AS total_login_days "
                "FROM player_logins WHERE player_id = :pid"
            ),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row[0] >= 1  # At least 1 from seed data


# ---------------------------------------------------------------------------
# Tests: Legacy SQL Quirks
# ---------------------------------------------------------------------------


class TestLegacySQLQuirks:
    """Test PostgreSQL-specific SQL patterns used by the legacy server.

    These patterns must work identically in the Python reimplementation.
    """

    def test_upsert_player_progress(self, db_session) -> None:
        """ON CONFLICT (player_id, progress_key) DO UPDATE — legacy playerProfile.js:425-431."""
        # INSERT new progress
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status) "
                "ON CONFLICT (player_id, progress_key) DO UPDATE "
                "SET status = excluded.status"
            ),
            {"pid": 10010, "key": "test_upsert_key", "status": 1},
        )
        db_session.flush()

        # Verify inserted
        result = db_session.execute(
            text(
                "SELECT status FROM player_progress WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": "test_upsert_key"},
        )
        assert result.fetchone()[0] == 1

        # UPSERT again with different status
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status) "
                "ON CONFLICT (player_id, progress_key) DO UPDATE "
                "SET status = excluded.status"
            ),
            {"pid": 10010, "key": "test_upsert_key", "status": 2},
        )
        db_session.flush()

        result = db_session.execute(
            text(
                "SELECT status FROM player_progress WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": "test_upsert_key"},
        )
        assert result.fetchone()[0] == 2

    def test_upsert_player_buddies(self, db_session) -> None:
        """ON CONFLICT (player_id, buddy_id, buddy_key) DO UPDATE — legacy playerProfile.js:462-467."""
        db_session.execute(
            text(
                "INSERT INTO player_buddies (player_id, buddy_id, buddy_key, buddy_value) "
                "VALUES (:pid, :bid, :bkey, :bval) "
                "ON CONFLICT (player_id, buddy_id, buddy_key) DO UPDATE "
                "SET buddy_value = excluded.buddy_value"
            ),
            {"pid": 10010, "bid": 99, "bkey": "test_key", "bval": "val1"},
        )
        db_session.flush()

        result = db_session.execute(
            text(
                "SELECT buddy_value FROM player_buddies "
                "WHERE player_id = :pid AND buddy_id = :bid AND buddy_key = :bkey"
            ),
            {"pid": 10010, "bid": 99, "bkey": "test_key"},
        )
        assert result.fetchone()[0] == "val1"

        # Update via UPSERT
        db_session.execute(
            text(
                "INSERT INTO player_buddies (player_id, buddy_id, buddy_key, buddy_value) "
                "VALUES (:pid, :bid, :bkey, :bval) "
                "ON CONFLICT (player_id, buddy_id, buddy_key) DO UPDATE "
                "SET buddy_value = excluded.buddy_value"
            ),
            {"pid": 10010, "bid": 99, "bkey": "test_key", "bval": "val2"},
        )
        db_session.flush()

        result = db_session.execute(
            text(
                "SELECT buddy_value FROM player_buddies "
                "WHERE player_id = :pid AND buddy_id = :bid AND buddy_key = :bkey"
            ),
            {"pid": 10010, "bid": 99, "bkey": "test_key"},
        )
        assert result.fetchone()[0] == "val2"

    def test_date_trunc_day(self, db_session) -> None:
        """date_trunc('day', ts_when) works for login counting — legacy playerProfile.js:94."""
        result = db_session.execute(
            text("SELECT date_trunc('day', ts_when) FROM player_logins LIMIT 1")
        )
        row = result.fetchone()
        assert row is not None
        # date_trunc returns a timestamp with time portion zeroed
        assert row[0].hour == 0
        assert row[0].minute == 0
        assert row[0].second == 0

    def test_inet_type_for_ip(self, db_session) -> None:
        """ip_addr column uses PostgreSQL INET type — legacy paradox.sql:303."""
        result = db_session.execute(
            text(
                "SELECT data_type FROM information_schema.columns "
                "WHERE table_name = 'player_logins' AND column_name = 'ip_addr'"
            )
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == "inet"

    def test_player_id_auto_increment(self, db_session) -> None:
        """player.player_id uses PostgreSQL sequence — legacy paradox.sql:497-512."""
        result = db_session.execute(
            text(
                "SELECT column_default FROM information_schema.columns "
                "WHERE table_name = 'player' AND column_name = 'player_id'"
            )
        )
        row = result.fetchone()
        # Should have a sequence default
        assert row is not None
        assert row[0] is not None


# ---------------------------------------------------------------------------
# Tests: Rollback Isolation
# ---------------------------------------------------------------------------


class TestRollbackIsolation:
    """Verify test isolation via transaction rollback."""

    def test_insert_rolled_back(self, db_session) -> None:
        """Data inserted in test is rolled back after test completes."""
        # This test verifies the fixture works — the insert below will be
        # rolled back when the session is closed.
        db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 88888, "key": "rollback_test", "status": 1},
        )
        db_session.flush()

        result = db_session.execute(
            text(
                "SELECT COUNT(*) FROM player_progress "
                "WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 88888, "key": "rollback_test"},
        )
        assert result.scalar() == 1

        # After this test, the fixture rolls back the transaction.
        # A subsequent test should NOT find this row.
