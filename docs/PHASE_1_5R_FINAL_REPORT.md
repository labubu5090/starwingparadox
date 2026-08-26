# Phase 1.5R: PostgreSQL Runtime Validation Resume — Final Report

## Status: COMPLETE

**Date:** 2026-08-27
**Commit:** `405ddaf` (fix: correct integration test assertions for PostgreSQL runtime validation)

## Runtime Verification

| Property | Value |
|----------|-------|
| Classification | **NATIVE_READY** |
| PostgreSQL version | 16.15 |
| psql version | 16.15 |
| Installation path | `C:\Program Files\PostgreSQL\16\bin` |
| Windows service | `postgresql-x64-16` (Running) |
| Port | 5432 (LISTENING) |
| Authentication | scram-sha-256 |
| Encoding | UTF-8 |

## Test Database

| Property | Value |
|----------|-------|
| Database name | `starwing_test` |
| Host | localhost |
| Port | 5432 |
| Owner | `starwing_test_user` |
| Role privileges | Not superuser |
| Encoding | UTF-8 |

## Schema Import

| Metric | Value |
|--------|-------|
| Source file | `legacy-js/paradox.sql` |
| Tables created | 17 |
| Sequences created | All auto-increment sequences |
| Indexes created | All legacy indexes |
| Seed rows | 2 players (10010, 10011) |
| Errors | 0 |
| Warnings | 0 |

## Integration Test Results

### Before (Phase 1.5 — BLOCKED)
- 43 tests skipped (PostgreSQL not available)

### After (Phase 1.5R — COMPLETE)
- 42 integration tests executed
- 42 integration tests passed
- 0 integration tests failed

### Full Test Suite

| Metric | Phase 1.5 | Phase 1.5R |
|--------|-----------|------------|
| Tests collected | 877 | 878 |
| Tests passed | 834 | 876 |
| Tests skipped | 43 | 1 |
| Tests failed | 0 | 0 |
| Coverage | 74% | 74% |
| Ruff errors | 0 | 0 |
| Mypy errors | 0 | 0 |

### Previously Skipped → Now Passing (42 tests)

All 42 PostgreSQL integration tests that were previously skipped now pass:

- **Database connectivity** (6 tests): URL validation, connection, PostgreSQL detection, schema existence
- **Seed data** (4 tests): Player 10010/10011 existence, NESYS IDs, buddy relationships
- **Basic CRUD** (6 tests): Select by ID/NESYS, nonexistent lookups, buddy queries, login counts
- **Legacy SQL quirks** (5 tests): UPSERT patterns, date_trunc, inet type, auto-increment
- **Rollback isolation** (1 test): Transaction rollback doesn't persist
- **Player CRUD** (8 tests): Create, read, update name/rank, delete, default values, nesys_id behavior
- **Player progress** (6 tests): Upsert insert/update, read, count, delete, key max length
- **Player missions** (6 tests): Insert, upsert, read, delete, count, unique constraint

## Test Defects Fixed

### 1. `test_player_nesys_id_uniqueness` → `test_player_nesys_id_no_db_constraint`

**Root cause:** Test assumed `nesys_id` had a UNIQUE constraint at the database level. Legacy `paradox.sql` does not define this constraint — uniqueness is enforced at the application layer.

**Fix:** Rewritten to verify that duplicate `nesys_id` inserts succeed at the DB level, confirming the legacy schema behavior.

### 2. `test_mission_unique_constraint`

**Root cause:** Regex `match="UNIQUE"` did not match psycopg's actual error message which contains `UniqueViolation`.

**Fix:** Changed regex to `match="[Uu]nique|already exists"` to match both SQLAlchemy and psycopg error formats.

### 3. `test_capture_without_engine`

**Root cause:** Test assumed `TEST_DATABASE_URL` env var was unset. When running with real PostgreSQL, the env var is set, causing `snapshot.available=True` instead of `False`.

**Fix:** Added `monkeypatch.delenv("TEST_DATABASE_URL", raising=False)` to ensure the env var is unset during this specific test.

## Git History

```
405ddaf fix: correct integration test assertions for PostgreSQL runtime validation
9de39b9 chore: prepare PostgreSQL runtime validation
8e768e1 feat: establish PostgreSQL and player profile parity foundation
0aefebd test: establish legacy parity regression baseline
ce7d30d chore: establish verified Phase 1.2 compatibility baseline
```

## No Claims of

- Real cabinet compatibility
- Matching implementation
- Battle implementation
- Cabinet compatibility
- Player profile field computation (6 unknown fields remain)

## Next Steps

Phase 1.5R is complete. The PostgreSQL runtime validation exit criteria are now satisfied:

1. ✅ PostgreSQL runtime verified (NATIVE_READY)
2. ✅ Isolated test database created (`starwing_test`)
3. ✅ Legacy-compatible schema imported (17 tables)
4. ✅ All 42 integration tests pass
5. ✅ Full test suite passes (876 passed, 1 skipped, 0 failed)
6. ✅ Quality gates pass (ruff: 0, mypy: 0)
7. ✅ Test defects documented and fixed
8. ✅ No production databases affected
