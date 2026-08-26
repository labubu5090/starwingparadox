# Database Comparison Guide

## Overview

The database comparison framework provides snapshot-based comparison of PostgreSQL database state before and after request handling. This is used to verify that the Python server produces identical database effects to the legacy JavaScript server.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Request Lifecycle                         │
├─────────────────────────────────────────────────────────────┤
│  1. capture_pre_request()    → DatabaseSnapshot (before)    │
│  2. Process request          → Database mutations            │
│  3. capture_post_request()   → DatabaseSnapshot (after)     │
│  4. compare_snapshots()      → ComparisonResult             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```python
from app.database import capture_pre_request, capture_post_request, compare_snapshots

# Before processing the request
before = capture_pre_request()

# Process the request (database mutations happen here)
process_request(request)

# After processing
after = capture_post_request()

# Compare
result = compare_snapshots(before, after)

if result.classification == "EXACT_DATABASE_MATCH":
    print("Database state is identical to legacy server")
elif result.classification == "DATABASE_MISMATCH":
    print(f"Database mismatch: {result.details}")
```

## Classifications

### EXACT_DATABASE_MATCH

All table checksums are identical before and after. No rows were added, removed, or modified. This is the ideal result when verifying parity.

```python
result.classification == DatabaseComparisonResult.EXACT_DATABASE_MATCH
result.is_match == True
```

### SEMANTIC_DATABASE_MATCH

Row counts match and checksums are identical, but the order of rows may differ. This indicates the same data was written, just in a different order.

```python
result.classification == DatabaseComparisonResult.SEMANTIC_DATABASE_MATCH
result.is_match == True
```

### DATABASE_MISMATCH

Rows were added, removed, or modified. This indicates a difference between the Python and legacy server behavior.

```python
result.classification == DatabaseComparisonResult.DATABASE_MISMATCH
result.is_match == False
```

### TRANSACTION_MISMATCH

Different sets of tables were affected by the request. This usually indicates a missing or extra table write.

```python
result.classification == DatabaseComparisonResult.TRANSACTION_MISMATCH
```

### DATABASE_NOT_AVAILABLE

PostgreSQL is not reachable. This occurs when:
- `TEST_DATABASE_URL` is not set
- The database name doesn't end with `_test`
- PostgreSQL is not running

```python
result.classification == DatabaseComparisonResult.DATABASE_NOT_AVAILABLE
```

## Configuration

### Environment Variables

```bash
# Required for integration tests and database comparison
TEST_DATABASE_URL=postgresql+psycopg://paradox:changeme@localhost:5432/paradox_test
```

### Safety Checks

The framework enforces these safety measures:
1. Database name must end with `_test` suffix
2. Only tables in `RELEVANT_TABLES` are captured
3. Snapshots are read-only (no mutations)

## Usage in Tests

### Integration Test with Comparison

```python
import pytest
from app.database import capture_pre_request, capture_post_request, compare_snapshots

pytestmark = [pytest.mark.integration, pytest.mark.db]

def test_player_profile_request(db_engine):
    """Verify player profile request produces correct database state."""
    # Capture before state
    before = capture_pre_request(engine=db_engine)
    
    # Process the request
    # ... handle player profile request ...
    
    # Capture after state
    after = capture_post_request(engine=db_engine)
    
    # Compare
    result = compare_snapshots(before, after)
    assert result.is_match, f"Database mismatch: {result.details}"
```

### Unit Test with In-Memory SQLite

```python
from sqlalchemy import create_engine
from app.database import capture_snapshot, compare_snapshots

def test_comparison_logic():
    """Test comparison logic with SQLite."""
    engine = create_engine("sqlite:///:memory:")
    
    # Create test tables
    with engine.connect() as conn:
        conn.execute("CREATE TABLE test (id INT, name TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'alice')")
    
    # Capture and compare
    snap1 = capture_snapshot(tables=["test"], engine=engine)
    snap2 = capture_snapshot(tables=["test"], engine=engine)
    
    result = compare_snapshots(snap1, snap2)
    assert result.classification == "EXACT_DATABASE_MATCH"
```

## PostgreSQL-Specific Features

The comparison framework leverages several PostgreSQL-specific features:

### Transaction Isolation

```python
# Snapshots are captured within transactions
with engine.connect() as conn:
    transaction = conn.begin()
    # ... mutations ...
    snapshot = capture_snapshot(engine=engine)
    transaction.rollback()  # Rollback after snapshot
```

### JSONB Support

PostgreSQL JSONB columns are compared using `json.dumps` with `sort_keys=True` for deterministic ordering.

### Timestamp Precision

Timestamps are compared using PostgreSQL's `date_trunc` function for consistent comparison.

### INET Type

IP addresses stored as PostgreSQL INET type are compared as strings.

## Relevant Tables

The framework captures snapshots of these tables:

```python
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
```

## Troubleshooting

### DATABASE_NOT_AVAILABLE

1. Ensure PostgreSQL is installed and running
2. Check `TEST_DATABASE_URL` is set correctly
3. Verify database name ends with `_test`
4. Check network connectivity

### DATABASE_MISMATCH

1. Check the `details` list in `ComparisonResult`
2. Compare specific table differences
3. Review SQL queries in the request handler
4. Check for timing-dependent issues

### TRANSACTION_MISMATCH

1. Verify all expected tables are in `RELEVANT_TABLES`
2. Check for missing table writes in the handler
3. Review table creation order

## References

- `server/app/database/compare.py` - Core comparison framework
- `server/tests/test_database_compare.py` - Unit tests
- `server/tests/integration/test_database_integration.py` - Integration tests
- `server/tests/integration/test_player_integration.py` - Player-specific tests
