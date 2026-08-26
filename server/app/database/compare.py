"""Database comparison framework for Starwing Paradox.

Provides snapshot-based comparison of database state before and after
request handling. Used to verify that the Python server produces identical
database effects to the legacy JavaScript server.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


class DatabaseComparisonResult(str, Enum):
    """Classification of database comparison results."""

    EXACT_DATABASE_MATCH = "EXACT_DATABASE_MATCH"
    SEMANTIC_DATABASE_MATCH = "SEMANTIC_DATABASE_MATCH"
    DATABASE_MISMATCH = "DATABASE_MISMATCH"
    TRANSACTION_MISMATCH = "TRANSACTION_MISMATCH"
    DATABASE_NOT_AVAILABLE = "DATABASE_NOT_AVAILABLE"


# ---------------------------------------------------------------------------
# Snapshot types
# ---------------------------------------------------------------------------


@dataclass
class TableSnapshot:
    """A snapshot of a single table's state."""

    table_name: str
    columns: list[str]
    rows: list[tuple[Any, ...]]
    row_count: int
    checksum: str

    @classmethod
    def from_engine(cls, engine: Engine, table_name: str) -> TableSnapshot:
        """Capture a snapshot of the named table."""
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name} ORDER BY 1"))
            columns = list(result.keys())
            rows = [tuple(row) for row in result.fetchall()]
            row_count = len(rows)
            checksum = _compute_checksum(columns, rows)
        return cls(
            table_name=table_name,
            columns=columns,
            rows=rows,
            row_count=row_count,
            checksum=checksum,
        )


@dataclass
class DatabaseSnapshot:
    """A complete snapshot of all relevant database tables."""

    tables: dict[str, TableSnapshot] = field(default_factory=dict)
    timestamp: float = 0.0
    available: bool = True

    def get_table(self, table_name: str) -> TableSnapshot | None:
        return self.tables.get(table_name)

    def to_dict(self) -> dict[str, Any]:
        """Serialize snapshot to a JSON-serializable dict."""
        return {
            "available": self.available,
            "tables": {
                name: {
                    "table_name": snap.table_name,
                    "columns": snap.columns,
                    "rows": [list(row) for row in snap.rows],
                    "row_count": snap.row_count,
                    "checksum": snap.checksum,
                }
                for name, snap in self.tables.items()
            },
        }


# ---------------------------------------------------------------------------
# Comparison result
# ---------------------------------------------------------------------------


@dataclass
class ComparisonResult:
    """Result of comparing two database snapshots."""

    classification: DatabaseComparisonResult
    table_results: dict[str, TableComparisonResult] = field(default_factory=dict)
    details: list[str] = field(default_factory=list)

    @property
    def is_match(self) -> bool:
        return self.classification in (
            DatabaseComparisonResult.EXACT_DATABASE_MATCH,
            DatabaseComparisonResult.SEMANTIC_DATABASE_MATCH,
        )


@dataclass
class TableComparisonResult:
    """Result of comparing a single table."""

    table_name: str
    row_count_before: int
    row_count_after: int
    rows_added: int
    rows_removed: int
    rows_modified: int
    checksum_match: bool
    semantic_match: bool

    @property
    def is_exact_match(self) -> bool:
        return self.checksum_match and self.rows_added == 0 and self.rows_removed == 0

    @property
    def is_semantic_match(self) -> bool:
        return self.semantic_match and self.rows_added == 0 and self.rows_removed == 0


# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------


def _compute_checksum(columns: list[str], rows: list[tuple[Any, ...]]) -> str:
    """Compute a deterministic checksum for table data."""
    data = json.dumps(
        {"columns": columns, "rows": [list(row) for row in rows]},
        default=str,
        sort_keys=True,
    )
    return hashlib.sha256(data.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Snapshot capture
# ---------------------------------------------------------------------------

RELEVANT_TABLES = [
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


def _get_engine_from_env() -> Engine | None:
    """Create engine from TEST_DATABASE_URL if available."""
    url = os.environ.get("TEST_DATABASE_URL", "")
    if not url:
        return None
    parsed = urlparse(url)
    db_name = parsed.path.lstrip("/")
    if not db_name.endswith("_test"):
        return None
    try:
        engine = create_engine(url, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception:
        return None


def capture_snapshot(
    tables: list[str] | None = None,
    engine: Engine | None = None,
) -> DatabaseSnapshot:
    """Capture a snapshot of all relevant tables.

    Args:
        tables: List of table names to capture. Defaults to RELEVANT_TABLES.
        engine: Optional pre-configured engine. If None, uses TEST_DATABASE_URL.

    Returns:
        DatabaseSnapshot with all requested tables, or unavailable snapshot.
    """
    import time

    if engine is None:
        engine = _get_engine_from_env()
    if engine is None:
        return DatabaseSnapshot(available=False, timestamp=time.time())

    target_tables = tables or RELEVANT_TABLES
    snapshots: dict[str, TableSnapshot] = {}

    for table_name in target_tables:
        try:
            snapshots[table_name] = TableSnapshot.from_engine(engine, table_name)
        except Exception:
            # Table may not exist
            continue

    return DatabaseSnapshot(
        tables=snapshots,
        timestamp=time.time(),
        available=True,
    )


def capture_pre_request(
    tables: list[str] | None = None,
    engine: Engine | None = None,
) -> DatabaseSnapshot:
    """Capture a snapshot before a request is processed."""
    return capture_snapshot(tables=tables, engine=engine)


def capture_post_request(
    tables: list[str] | None = None,
    engine: Engine | None = None,
) -> DatabaseSnapshot:
    """Capture a snapshot after a request is processed."""
    return capture_snapshot(tables=tables, engine=engine)


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


def _compare_tables(
    before: TableSnapshot,
    after: TableSnapshot,
) -> TableComparisonResult:
    """Compare two table snapshots."""
    # Convert rows to sets for comparison
    before_set = set(before.rows)
    after_set = set(after.rows)

    rows_added = len(after_set - before_set)
    rows_removed = len(before_set - after_set)

    # Rows modified = rows that exist in both but differ
    common_before = before_set & after_set
    common_after = after_set & before_set
    rows_modified = len(common_before) - len(common_before & common_after)

    checksum_match = before.checksum == after.checksum

    # Semantic match: same row count and same checksums (ignoring order)
    semantic_match = before.row_count == after.row_count and before.checksum == after.checksum

    return TableComparisonResult(
        table_name=before.table_name,
        row_count_before=before.row_count,
        row_count_after=after.row_count,
        rows_added=rows_added,
        rows_removed=rows_removed,
        rows_modified=rows_modified,
        checksum_match=checksum_match,
        semantic_match=semantic_match,
    )


def compare_snapshots(
    before: DatabaseSnapshot,
    after: DatabaseSnapshot,
) -> ComparisonResult:
    """Compare two database snapshots and classify the result.

    Classification logic:
    - EXACT_DATABASE_MATCH: All table checksums identical, no row changes
    - SEMANTIC_DATABASE_MATCH: Row counts match but order may differ
    - DATABASE_MISMATCH: Rows added/removed/modified
    - TRANSACTION_MISMATCH: Different tables affected
    - DATABASE_NOT_AVAILABLE: Database not reachable
    """
    if not before.available or not after.available:
        return ComparisonResult(
            classification=DatabaseComparisonResult.DATABASE_NOT_AVAILABLE,
            details=["One or both snapshots are unavailable (database not reachable)"],
        )

    # Check if same tables were captured
    before_tables = set(before.tables.keys())
    after_tables = set(after.tables.keys())
    if before_tables != after_tables:
        return ComparisonResult(
            classification=DatabaseComparisonResult.TRANSACTION_MISMATCH,
            details=[
                f"Tables differ: before={sorted(before_tables)}, after={sorted(after_tables)}"
            ],
        )

    table_results: dict[str, TableComparisonResult] = {}
    all_exact = True
    all_semantic = True
    any_mismatch = False

    for table_name in sorted(before_tables):
        before_snap = before.tables[table_name]
        after_snap = after.tables[table_name]
        result = _compare_tables(before_snap, after_snap)
        table_results[table_name] = result

        if not result.is_exact_match:
            all_exact = False
        if not result.is_semantic_match:
            all_semantic = False
        if result.rows_added > 0 or result.rows_removed > 0 or result.rows_modified > 0:
            any_mismatch = True

    details: list[str] = []
    for name, tr in table_results.items():
        if tr.is_exact_match:
            details.append(f"{name}: EXACT match ({tr.row_count_before} rows)")
        else:
            details.append(
                f"{name}: changed (+{tr.rows_added}/-{tr.rows_removed}"
                f"/~{tr.rows_modified} rows, {tr.row_count_before} -> {tr.row_count_after})"
            )

    if all_exact:
        classification = DatabaseComparisonResult.EXACT_DATABASE_MATCH
    elif all_semantic and not any_mismatch:
        classification = DatabaseComparisonResult.SEMANTIC_DATABASE_MATCH
    elif any_mismatch:
        classification = DatabaseComparisonResult.DATABASE_MISMATCH
    else:
        classification = DatabaseComparisonResult.SEMANTIC_DATABASE_MATCH

    return ComparisonResult(
        classification=classification,
        table_results=table_results,
        details=details,
    )
