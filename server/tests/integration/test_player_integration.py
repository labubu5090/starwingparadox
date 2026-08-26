"""SQLite player integration tests.

These tests verify player CRUD operations against a real SQLite database.
"""

import pytest
import pytest_asyncio
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.db.models import *  # noqa: F401, F403


def _configure_sqlite_pragmas(dbapi_connection, connection_record) -> None:  # type: ignore[no-untyped-def]
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("PRAGMA busy_timeout = 10000")
    cursor.close()


@pytest_asyncio.fixture
async def db_session(tmp_path) -> AsyncSession:
    """Create an async session with a temporary SQLite database."""
    db_path = tmp_path / "test_player.db"
    url = f"sqlite+aiosqlite:///{db_path}"
    engine = create_async_engine(url, echo=False)
    event.listen(engine.sync_engine, "connect", _configure_sqlite_pragmas)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


# ---------------------------------------------------------------------------
# Player CRUD Tests
# ---------------------------------------------------------------------------


class TestPlayerCRUD:
    """Test player CRUD operations."""

    async def test_create_player(self, db_session):
        """Create a new player."""
        await db_session.execute(
            text(
                "INSERT INTO player (player_id, nesys_id, player_name) VALUES (:pid, :nesys, :name)"
            ),
            {"pid": 10010, "nesys": "7020392000000000", "name": "ArcadeMachinist"},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT player_id, nesys_id, player_name FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row is not None
        assert row[0] == 10010
        assert row[1] == "7020392000000000"

    async def test_read_player_fields(self, db_session):
        """Read all player fields."""
        await db_session.execute(
            text(
                "INSERT INTO player (player_id, nesys_id, player_name, rank_id, title_id) "
                "VALUES (:pid, :nesys, :name, :rank, :title)"
            ),
            {"pid": 10010, "nesys": "NESYS001", "name": "Test", "rank": 10, "title": 100},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT rank_id, title_id FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row[0] == 10
        assert row[1] == 100

    async def test_update_player_name(self, db_session):
        """Update player name."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.commit()
        await db_session.execute(
            text("UPDATE player SET player_name = :name WHERE player_id = :pid"),
            {"pid": 10010, "name": "NewName"},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT player_name FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.fetchone()[0] == "NewName"

    async def test_update_player_rank(self, db_session):
        """Update player rank."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.commit()
        await db_session.execute(
            text("UPDATE player SET rank_id = :rank WHERE player_id = :pid"),
            {"pid": 10010, "rank": 20},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT rank_id FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.fetchone()[0] == 20

    async def test_delete_player_by_id(self, db_session):
        """Delete player by ID."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.commit()
        await db_session.execute(
            text("DELETE FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT player_id FROM player WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.fetchone() is None

    async def test_player_nesys_id_no_db_constraint(self, db_session):
        """nesys_id has no UNIQUE constraint at DB level — legacy schema."""
        await db_session.execute(
            text("INSERT INTO player (nesys_id) VALUES (:nesys)"),
            {"nesys": "DUP_NESYS_TEST_001"},
        )
        await db_session.execute(
            text("INSERT INTO player (nesys_id) VALUES (:nesys)"),
            {"nesys": "DUP_NESYS_TEST_001"},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM player WHERE nesys_id = :nesys"),
            {"nesys": "DUP_NESYS_TEST_001"},
        )
        assert result.fetchone()[0] == 2

    async def test_player_default_values(self, db_session):
        """New player should have sensible defaults."""
        result = await db_session.execute(
            text(
                "INSERT INTO player (nesys_id) VALUES (:nesys) "
                "RETURNING rank_id, title_id, buddy_id, line_color_id, rank_point"
            ),
            {"nesys": "DEFAULT_TEST_001"},
        )
        row = result.fetchone()
        await db_session.commit()
        assert row[0] == 0  # rank_id default
        assert row[1] == 0  # title_id default
        assert row[4] == 0  # rank_point default

    async def test_player_count(self, db_session):
        """COUNT players."""
        await db_session.execute(
            text("INSERT INTO player (nesys_id) VALUES (:nesys)"),
            {"nesys": "NESYS_COUNT_1"},
        )
        await db_session.execute(
            text("INSERT INTO player (nesys_id) VALUES (:nesys)"),
            {"nesys": "NESYS_COUNT_2"},
        )
        await db_session.commit()
        result = await db_session.execute(text("SELECT COUNT(*) FROM player"))
        assert result.scalar() >= 2


# ---------------------------------------------------------------------------
# Player Progress Tests
# ---------------------------------------------------------------------------


class TestPlayerProgress:
    """Test player progress operations."""

    async def test_upsert_progress_insert(self, db_session):
        """Insert player progress."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 10010, "key": "tutorial", "status": 1},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT status FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.fetchone()[0] == 1

    async def test_upsert_progress_update(self, db_session):
        """Update player progress."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 10010, "key": "tutorial", "status": 1},
        )
        await db_session.commit()
        await db_session.execute(
            text(
                "UPDATE player_progress SET status = :new_status "
                "WHERE player_id = :pid AND progress_key = :key"
            ),
            {"pid": 10010, "key": "tutorial", "new_status": 2},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT status FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.fetchone()[0] == 2

    async def test_read_progress(self, db_session):
        """Read player progress."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 10010, "key": "tutorial", "status": 1},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT progress_key, status FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row[0] == "tutorial"
        assert row[1] == 1

    async def test_progress_count_per_player(self, db_session):
        """COUNT progress entries for a player."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        for i in range(3):
            await db_session.execute(
                text(
                    "INSERT INTO player_progress (player_id, progress_key, status) "
                    "VALUES (:pid, :key, :status)"
                ),
                {"pid": 10010, "key": f"key_{i}", "status": 0},
            )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.scalar() == 3

    async def test_delete_progress(self, db_session):
        """Delete player progress."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 10010, "key": "tutorial", "status": 1},
        )
        await db_session.commit()
        await db_session.execute(
            text("DELETE FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.scalar() == 0

    async def test_progress_key_max_length(self, db_session):
        """Progress key max length is 35 chars."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        long_key = "A" * 35
        await db_session.execute(
            text(
                "INSERT INTO player_progress (player_id, progress_key, status) "
                "VALUES (:pid, :key, :status)"
            ),
            {"pid": 10010, "key": long_key, "status": 0},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT progress_key FROM player_progress WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert len(result.fetchone()[0]) == 35


# ---------------------------------------------------------------------------
# Player Missions Tests
# ---------------------------------------------------------------------------


class TestPlayerMissions:
    """Test player mission operations."""

    async def test_insert_mission(self, db_session):
        """Insert a mission."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 500, "cc": 1, "status": 1},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT clear_count, status FROM player_missions WHERE player_id = :pid"),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row[0] == 1
        assert row[1] == 1

    async def test_upsert_mission(self, db_session):
        """Upsert a mission."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 500, "cc": 1, "status": 1},
        )
        await db_session.commit()
        await db_session.execute(
            text(
                "UPDATE player_missions SET clear_count = :cc, status = :status "
                "WHERE player_id = :pid AND mission_id = :mid"
            ),
            {"pid": 10010, "mid": 500, "cc": 2, "status": 2},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT clear_count, status FROM player_missions WHERE player_id = :pid"),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row[0] == 2
        assert row[1] == 2

    async def test_read_mission(self, db_session):
        """Read a mission."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 500, "cc": 1, "status": 1},
        )
        await db_session.commit()
        result = await db_session.execute(
            text(
                "SELECT mission_id, clear_count, status FROM player_missions WHERE player_id = :pid"
            ),
            {"pid": 10010},
        )
        row = result.fetchone()
        assert row[0] == 500
        assert row[1] == 1
        assert row[2] == 1

    async def test_delete_mission(self, db_session):
        """Delete a mission."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 500, "cc": 1, "status": 1},
        )
        await db_session.commit()
        await db_session.execute(
            text("DELETE FROM player_missions WHERE player_id = :pid AND mission_id = :mid"),
            {"pid": 10010, "mid": 500},
        )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM player_missions WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.scalar() == 0

    async def test_mission_count_per_player(self, db_session):
        """COUNT missions for a player."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        for i in range(3):
            await db_session.execute(
                text(
                    "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                    "VALUES (:pid, :mid, :cc, :status)"
                ),
                {"pid": 10010, "mid": 500 + i, "cc": 0, "status": 0},
            )
        await db_session.commit()
        result = await db_session.execute(
            text("SELECT COUNT(*) FROM player_missions WHERE player_id = :pid"),
            {"pid": 10010},
        )
        assert result.scalar() == 3

    async def test_mission_unique_constraint(self, db_session):
        """Unique constraint on (player_id, mission_id) prevents duplicates."""
        await db_session.execute(
            text("INSERT INTO player (player_id, nesys_id) VALUES (:pid, :nesys)"),
            {"pid": 10010, "nesys": "NESYS001"},
        )
        await db_session.execute(
            text(
                "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                "VALUES (:pid, :mid, :cc, :status)"
            ),
            {"pid": 10010, "mid": 500, "cc": 1, "status": 1},
        )
        await db_session.commit()
        with pytest.raises(Exception, match="(?i)unique|already exists"):
            await db_session.execute(
                text(
                    "INSERT INTO player_missions (player_id, mission_id, clear_count, status) "
                    "VALUES (:pid, :mid, :cc, :status)"
                ),
                {"pid": 10010, "mid": 500, "cc": 2, "status": 2},
            )
            await db_session.flush()
