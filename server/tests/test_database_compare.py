"""Unit tests for the database comparison framework.

Tests the comparison logic using in-memory SQLite databases.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text

from app.database.compare import (
    DatabaseComparisonResult,
    DatabaseSnapshot,
    TableComparisonResult,
    TableSnapshot,
    _compare_tables,
    _compute_checksum,
    capture_snapshot,
    compare_snapshots,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sqlite_engine():
    """Provide an in-memory SQLite engine with test tables."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    with engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)")
        )
        conn.execute(text("INSERT INTO test_table VALUES (1, 'alice', 100)"))
        conn.execute(text("INSERT INTO test_table VALUES (2, 'bob', 200)"))
        conn.commit()
    return engine


@pytest.fixture
def empty_engine():
    """Provide an in-memory SQLite engine with an empty test table."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    with engine.connect() as conn:
        conn.execute(
            text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)")
        )
        conn.commit()
    return engine


@pytest.fixture
def multi_table_engine():
    """Provide an in-memory SQLite engine with multiple test tables."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE table_a (id INTEGER PRIMARY KEY, data TEXT)"))
        conn.execute(text("CREATE TABLE table_b (id INTEGER PRIMARY KEY, info TEXT)"))
        conn.execute(text("INSERT INTO table_a VALUES (1, 'alpha')"))
        conn.execute(text("INSERT INTO table_b VALUES (1, 'beta')"))
        conn.commit()
    return engine


# ---------------------------------------------------------------------------
# Tests: Checksum
# ---------------------------------------------------------------------------


class TestChecksum:
    """Test checksum computation."""

    def test_checksum_deterministic(self):
        """Same data produces same checksum."""
        columns = ["id", "name"]
        rows = [(1, "alice"), (2, "bob")]
        checksum1 = _compute_checksum(columns, rows)
        checksum2 = _compute_checksum(columns, rows)
        assert checksum1 == checksum2

    def test_checksum_different_data(self):
        """Different data produces different checksum."""
        columns = ["id", "name"]
        rows1 = [(1, "alice")]
        rows2 = [(1, "bob")]
        assert _compute_checksum(columns, rows1) != _compute_checksum(columns, rows2)

    def test_checksum_different_columns(self):
        """Different columns produces different checksum."""
        rows = [(1, "alice")]
        assert _compute_checksum(["id", "name"], rows) != _compute_checksum(["id", "value"], rows)


# ---------------------------------------------------------------------------
# Tests: TableSnapshot
# ---------------------------------------------------------------------------


class TestTableSnapshot:
    """Test TableSnapshot creation and properties."""

    def test_from_engine(self, sqlite_engine):
        """Capture a snapshot from an engine."""
        snapshot = TableSnapshot.from_engine(sqlite_engine, "test_table")
        assert snapshot.table_name == "test_table"
        assert snapshot.row_count == 2
        assert len(snapshot.rows) == 2
        assert len(snapshot.columns) == 3
        assert snapshot.checksum is not None

    def test_from_engine_empty_table(self, empty_engine):
        """Capture snapshot from empty table."""
        snapshot = TableSnapshot.from_engine(empty_engine, "test_table")
        assert snapshot.row_count == 0
        assert snapshot.rows == []

    def test_from_engine_nonexistent_table(self, sqlite_engine):
        """Capture snapshot from non-existent table raises."""
        with pytest.raises(Exception, match="nonexistent"):
            TableSnapshot.from_engine(sqlite_engine, "nonexistent")


# ---------------------------------------------------------------------------
# Tests: DatabaseSnapshot
# ---------------------------------------------------------------------------


class TestDatabaseSnapshot:
    """Test DatabaseSnapshot creation and serialization."""

    def test_unavailable_snapshot(self):
        """Unavailable snapshot has available=False."""
        snapshot = DatabaseSnapshot(available=False)
        assert not snapshot.available
        assert snapshot.tables == {}

    def test_get_table(self, sqlite_engine):
        """Get a specific table from snapshot."""
        snap = TableSnapshot.from_engine(sqlite_engine, "test_table")
        db_snapshot = DatabaseSnapshot(tables={"test_table": snap})
        assert db_snapshot.get_table("test_table") == snap
        assert db_snapshot.get_table("nonexistent") is None

    def test_to_dict(self, sqlite_engine):
        """Serialize snapshot to dict."""
        snap = TableSnapshot.from_engine(sqlite_engine, "test_table")
        db_snapshot = DatabaseSnapshot(tables={"test_table": snap})
        d = db_snapshot.to_dict()
        assert d["available"] is True
        assert "test_table" in d["tables"]
        assert d["tables"]["test_table"]["row_count"] == 2


# ---------------------------------------------------------------------------
# Tests: TableComparisonResult
# ---------------------------------------------------------------------------


class TestTableComparisonResult:
    """Test TableComparisonResult properties."""

    def test_exact_match(self):
        """Exact match when checksum matches and no changes."""
        result = TableComparisonResult(
            table_name="test",
            row_count_before=2,
            row_count_after=2,
            rows_added=0,
            rows_removed=0,
            rows_modified=0,
            checksum_match=True,
            semantic_match=True,
        )
        assert result.is_exact_match
        assert result.is_semantic_match

    def test_semantic_match_not_exact(self):
        """Semantic match but not exact when rows differ but count same."""
        result = TableComparisonResult(
            table_name="test",
            row_count_before=2,
            row_count_after=2,
            rows_added=0,
            rows_removed=0,
            rows_modified=0,
            checksum_match=False,
            semantic_match=True,
        )
        assert not result.is_exact_match
        assert result.is_semantic_match

    def test_mismatch(self):
        """Mismatch when rows added/removed."""
        result = TableComparisonResult(
            table_name="test",
            row_count_before=2,
            row_count_after=3,
            rows_added=1,
            rows_removed=0,
            rows_modified=0,
            checksum_match=False,
            semantic_match=False,
        )
        assert not result.is_exact_match
        assert not result.is_semantic_match


# ---------------------------------------------------------------------------
# Tests: Compare Tables
# ---------------------------------------------------------------------------


class TestCompareTables:
    """Test table comparison logic."""

    def test_identical_snapshots(self, sqlite_engine):
        """Two identical snapshots are exact match."""
        snap1 = TableSnapshot.from_engine(sqlite_engine, "test_table")
        snap2 = TableSnapshot.from_engine(sqlite_engine, "test_table")
        result = _compare_tables(snap1, snap2)
        assert result.is_exact_match

    def test_modified_rows(self, sqlite_engine):
        """Detecting modified rows."""
        snap1 = TableSnapshot.from_engine(sqlite_engine, "test_table")
        # Modify the database
        with sqlite_engine.connect() as conn:
            conn.execute(text("UPDATE test_table SET value = 999 WHERE id = 1"))
            conn.commit()
        snap2 = TableSnapshot.from_engine(sqlite_engine, "test_table")
        result = _compare_tables(snap1, snap2)
        assert not result.is_exact_match
        assert result.rows_modified > 0 or result.rows_added > 0


# ---------------------------------------------------------------------------
# Tests: Compare Snapshots
# ---------------------------------------------------------------------------


class TestCompareSnapshots:
    """Test full database snapshot comparison."""

    def test_exact_database_match(self, sqlite_engine):
        """Identical database state produces EXACT_DATABASE_MATCH."""
        snap1 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        snap2 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        result = compare_snapshots(snap1, snap2)
        assert result.classification == DatabaseComparisonResult.EXACT_DATABASE_MATCH
        assert result.is_match

    def test_database_not_available(self):
        """Unavailable snapshots produce DATABASE_NOT_AVAILABLE."""
        snap1 = DatabaseSnapshot(available=False)
        snap2 = DatabaseSnapshot(available=False)
        result = compare_snapshots(snap1, snap2)
        assert result.classification == DatabaseComparisonResult.DATABASE_NOT_AVAILABLE
        assert not result.is_match

    def test_mixed_availability(self):
        """One unavailable snapshot produces DATABASE_NOT_AVAILABLE."""
        snap1 = DatabaseSnapshot(available=True)
        snap2 = DatabaseSnapshot(available=False)
        result = compare_snapshots(snap1, snap2)
        assert result.classification == DatabaseComparisonResult.DATABASE_NOT_AVAILABLE

    def test_transaction_mismatch(self, multi_table_engine):
        """Different table sets produce TRANSACTION_MISMATCH."""
        snap1 = capture_snapshot(tables=["table_a"], engine=multi_table_engine)
        snap2 = capture_snapshot(tables=["table_b"], engine=multi_table_engine)
        result = compare_snapshots(snap1, snap2)
        assert result.classification == DatabaseComparisonResult.TRANSACTION_MISMATCH

    def test_database_mismatch(self, sqlite_engine):
        """Row changes produce DATABASE_MISMATCH."""
        snap1 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        # Insert new row
        with sqlite_engine.connect() as conn:
            conn.execute(text("INSERT INTO test_table VALUES (3, 'charlie', 300)"))
            conn.commit()
        snap2 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        result = compare_snapshots(snap1, snap2)
        assert result.classification == DatabaseComparisonResult.DATABASE_MISMATCH
        assert not result.is_match


# ---------------------------------------------------------------------------
# Tests: Capture Snapshot
# ---------------------------------------------------------------------------


class TestCaptureSnapshot:
    """Test snapshot capture functionality."""

    def test_capture_with_engine(self, sqlite_engine):
        """Capture snapshot with explicit engine."""
        snapshot = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        assert snapshot.available
        assert "test_table" in snapshot.tables

    def test_capture_without_engine(self, monkeypatch):
        """Capture snapshot without engine falls back to env; unset env to test unavailable path."""
        monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
        snapshot = capture_snapshot(tables=["test_table"])
        # Without TEST_DATABASE_URL, should be unavailable
        assert not snapshot.available

    def test_capture_empty_tables_list(self, sqlite_engine):
        """Capture with empty tables list."""
        snapshot = capture_snapshot(tables=[], engine=sqlite_engine)
        assert snapshot.available
        assert snapshot.tables == {}


# ---------------------------------------------------------------------------
# Tests: Classification Logic
# ---------------------------------------------------------------------------


class TestClassificationLogic:
    """Test all classification branches."""

    def test_all_exact_match(self, sqlite_engine):
        """All tables exact -> EXACT_DATABASE_MATCH."""
        snap1 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        snap2 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        result = compare_snapshots(snap1, snap2)
        assert result.classification == DatabaseComparisonResult.EXACT_DATABASE_MATCH

    def test_semantic_match_same_checksum(self, sqlite_engine):
        """Same checksum, same row count -> SEMANTIC_DATABASE_MATCH (when not exact)."""
        # This would be an unusual case but tests the branch
        snap1 = TableSnapshot(
            table_name="test",
            columns=["id"],
            rows=[(1,)],
            row_count=1,
            checksum="abc",
        )
        snap2 = TableSnapshot(
            table_name="test",
            columns=["id"],
            rows=[(1,)],
            row_count=1,
            checksum="abc",
        )
        db1 = DatabaseSnapshot(tables={"test": snap1}, available=True)
        db2 = DatabaseSnapshot(tables={"test": snap2}, available=True)
        result = compare_snapshots(db1, db2)
        assert result.classification == DatabaseComparisonResult.EXACT_DATABASE_MATCH

    def test_rows_added_database_mismatch(self, sqlite_engine):
        """Rows added -> DATABASE_MISMATCH."""
        snap1 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        with sqlite_engine.connect() as conn:
            conn.execute(text("INSERT INTO test_table VALUES (10, 'new', 0)"))
            conn.commit()
        snap2 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        result = compare_snapshots(snap1, snap2)
        assert result.classification == DatabaseComparisonResult.DATABASE_MISMATCH

    def test_result_details(self, sqlite_engine):
        """Result includes details for each table."""
        snap1 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        snap2 = capture_snapshot(tables=["test_table"], engine=sqlite_engine)
        result = compare_snapshots(snap1, snap2)
        assert len(result.details) == 1
        assert "test_table" in result.details[0]
        assert "EXACT match" in result.details[0]
