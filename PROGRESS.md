# Starwing Paradox Server - Progress Tracker

## Phase 1.5R: PostgreSQL Runtime Validation (COMPLETE)

**Commit**: `405ddaf`
**Status**: Complete - PostgreSQL 16.15 validated

## SQLite-Only Migration (COMPLETE)

**Commit**: `881abf2` (docs) / `970828d` (code)
**Status**: Complete - SQLite is the only supported database backend

## Current State

| Metric | Value |
|--------|-------|
| Tests passed | 821 |
| Tests failed | 0 (1 flaky TCP test) |
| Tests skipped | 1 |
| Ruff errors | 0 |
| Mypy errors | 0 |
| Database | SQLite-only |

## PostgreSQL References

- Config validation: Rejected (correct behavior)
- Test rejection tests: Present (correct behavior)
- compare.py: Updated (docstrings cleaned)
- Archived: All tools in `archive/postgresql/`

## SQLite Architecture

- **Backend**: aiosqlite + SQLAlchemy 2.0
- **Default URL**: `sqlite+aiosqlite:///./data/starwing.db`
- **PRAGMAs**: foreign_keys=ON, busy_timeout=10000
- **WAL mode**: Configured in `init_database()`
- **Schema**: 17 tables, Alembic migrations

## Exit Criteria Met

- [x] SQLite is only active backend
- [x] PostgreSQL not a runtime requirement
- [x] psycopg removed from dependencies
- [x] Alembic upgrade succeeds
- [x] WAL mode enabled
- [x] Foreign keys enabled
- [x] busy_timeout enabled
- [x] Player identity works
- [x] Profile load works
- [x] Transactions/rollback work
- [x] Concurrency validated
- [x] Backup/restore validated
- [x] Ruff 0 errors
- [x] Mypy 0 errors
- [x] No active PostgreSQL dependency

## Remaining Unknowns

- 6 computed player profile fields
- Real cabinet wire compatibility
- Matching implementation
- Battle implementation
