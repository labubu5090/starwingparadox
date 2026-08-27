# Phase 2A Initial Baseline

## 1. Git State

| Item | Value |
|------|-------|
| HEAD | `acca2c6` |
| Commit message | `test: establish pre-cabinet reliability baseline` |
| Working tree | Clean |

## 2. Test Collection

| Metric | Count |
|--------|-------|
| Tests collected | 823 |
| Tests passed | 822 |
| Tests skipped | 1 |
| Tests failed | 0 |

## 3. Quality Gates

| Gate | Result |
|------|--------|
| Ruff | 0 errors |
| Mypy | 0 errors (64 files) |

## 4. SQLite Baseline

| Item | Value |
|------|-------|
| Migration head | 001_initial_sqlite_schema |
| Tables | 17 + alembic_version |
| WAL mode | Enabled |
| foreign_keys | ON (per-connection) |
| busy_timeout | 10000ms (per-connection) |
| Integrity | OK |

## 5. Server Configuration

| Setting | Value |
|---------|-------|
| HTTP bind | 0.0.0.0:4001 |
| TCP bind | 0.0.0.0:6666 |
| Database | sqlite+aiosqlite:///./data/starwing.db |
| Capture | Disabled by default |
| Matching | 501 NOT_IMPLEMENTED |
| Battle | 501 NOT_IMPLEMENTED |

## 6. Skipped Test

| Item | Value |
|------|-------|
| Test | `test_unknown_message_type_raw_mode` |
| File | `tests/unit/test_codec_edge_cases.py:156` |
| Classification | OPTIONAL_EXTERNAL_TOOL |
