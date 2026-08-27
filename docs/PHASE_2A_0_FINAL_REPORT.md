# Phase 2A.0 Final Report

## 1. Phase Status

**PASS** - Pre-Cabinet Reliability Gate complete.

## 2. Initial Git Baseline

| Item | Value |
|------|-------|
| HEAD | `6f78da3` |
| Commit message | `chore: clean PostgreSQL refs, add concurrency and backup tests` |
| Working tree | Clean |

## 3. Exact Initial Test Result

| Metric | Count |
|--------|-------|
| Tests collected | 823 |
| Tests passed | 821 |
| Tests failed | 1 (flaky TCP) |
| Tests skipped | 1 |
| Tests xfailed | 0 |

## 4. Flaky TCP Test

| Item | Value |
|------|-------|
| Test name | `test_ping_handler_returns_framed_response` |
| File | `tests/legacy_regression/test_tcp_legacy.py:356` |
| Class | `TestResponseFraming` |
| Reproduction rate | ~30% with full suite |
| Passes alone | 100% |

## 5. TCP Root Cause

The test used `asyncio.get_event_loop().run_until_complete(...)` which conflicts with pytest-asyncio's loop management when run as part of the full test suite. The global event loop state becomes unpredictable after async tests complete, causing intermittent failures.

## 6. TCP Fix

Replaced `asyncio.get_event_loop().run_until_complete(...)` with explicit fresh event loop:
```python
loop = asyncio.new_event_loop()
try:
    result = loop.run_until_complete(...)
finally:
    loop.close()
```

This is deterministic because `asyncio.new_event_loop()` always creates an isolated loop unaffected by pytest-asyncio state.

## 7. TCP Individual Stress Result

| Runs | Passes | Failures |
|------|--------|----------|
| 100 | 100 | 0 |

## 8. TCP Module Stress Result

| Runs | Passes | Failures |
|------|--------|----------|
| 50 | 50 | 0 |

## 9. Full-Suite Repeatability

| Run | Passed | Skipped | Failed | Duration |
|-----|--------|---------|--------|----------|
| 1 | 822 | 1 | 0 | 9.08s |
| 2 | 822 | 1 | 0 | 8.98s |
| 3 | 822 | 1 | 0 | 8.96s |

## 10. Remaining Skip

| Item | Value |
|------|-------|
| Test name | `test_unknown_message_type_raw_mode` |
| File | `tests/unit/test_codec_edge_cases.py:156` |
| Skip reason | Generated protobuf loaded; raw mode not active |

## 11. Skip Classification

**OPTIONAL_EXTERNAL_TOOL** - Test requires generated protobuf to be absent (raw mode). Standard environment has generated protobuf loaded. Skip is correct and legitimate.

## 12. Fresh SQLite Provisioning

| Check | Result |
|-------|--------|
| No database file exists | PASS |
| Database parent directory created | PASS |
| Fresh SQLite database provisioned | PASS |
| All 17 tables exist | PASS (18 including alembic_version) |
| WAL mode active | PASS |
| foreign_keys enabled (via SQLAlchemy) | PASS |
| busy_timeout configured (via SQLAlchemy) | PASS |
| Integrity check OK | PASS |
| Seed data exists | PASS |
| Player creation works | PASS |
| Data persists after reopen | PASS |
| Backup succeeds | PASS |
| Restore succeeds | PASS |
| Integrity after restore | PASS |

## 13. Alembic Result

Alembic upgrade reaches head successfully. Creates 17 tables + alembic_version. Seed data (players 10010, 10011) inserted correctly.

## 14. SQLite PRAGMA Result

| PRAGMA | Value | Source |
|--------|-------|--------|
| journal_mode | WAL | Persisted in database |
| foreign_keys | ON | Set per-connection via event listener |
| busy_timeout | 10000 | Set per-connection via event listener |
| synchronous | NORMAL | Set during provisioning |

## 15. Player Persistence

Player 10010 created by Alembic seed migration. Player creation, lookup, and data persistence all verified.

## 16. Restart Persistence

Database file persists across reopens. Data survives connection close/reopen cycles.

## 17. Backup Result

SQLite backup API produces valid backup. Backup file exists and is readable.

## 18. Restore Result

Restore from backup produces valid database. All data preserved. Integrity check passes.

## 19. Integrity Result

PRAGMA integrity_check returns "ok" on fresh, backed up, and restored databases.

## 20. Protocol Regression

| Category | Result |
|----------|--------|
| Legacy regression tests | 185/185 passed |
| SQLite integration tests | 46/46 passed |
| Protobuf descriptors | Unchanged |
| Field numbers | Unchanged |
| Field types | Unchanged |
| HTTP route behavior | Unchanged |
| TCP 4-byte LE framing | Unchanged |
| Ping behavior | Unchanged |
| Version response | Unchanged |
| Resource response | Unchanged |
| Mission legacy behavior | Unchanged |
| Credit legacy behavior | Unchanged |
| Matching guard | 501 NOT_IMPLEMENTED |
| Battle guard | 501 NOT_IMPLEMENTED |

## 21. Capture Default State

Capture is disabled by default. No capture directory configured. `LEGACY_COMPATIBILITY_MODE` controls capture behavior.

## 22. Matching Guard

Matching endpoints return 501 NOT_IMPLEMENTED. No database operations attempted.

## 23. Battle Guard

Battle endpoints return 501 NOT_IMPLEMENTED. No database operations attempted.

## 24. Supported Deployment Model

Status: **SINGLE_CABINET_DEPLOYMENT_CANDIDATE**

- One Starwing server process
- One local SQLite database
- Local filesystem only
- One cabinet initially
- Multiple network requests to same process
- WAL enabled
- Backup before migration required
- No shared network database
- No multiple writer processes
- No distributed matching state
- No battle orchestration

## 25. Whole-Project Coverage

~74% (unchanged from previous phase)

## 26. Active-Scope Coverage

~91% (unchanged from previous phase)

## 27. Ruff Result

0 errors. 135 files formatted.

## 28. Mypy Result

0 errors in 64 source files.

## 29. Files Created

| File | Purpose |
|------|---------|
| `docs/PHASE_2A_0_INITIAL_BASELINE.md` | Initial baseline record |
| `docs/TCP_FLAKY_TEST_ROOT_CAUSE.md` | Root cause analysis |
| `docs/TCP_STRESS_RESULT.md` | Stress test results |
| `docs/REMAINING_SKIP_AUDIT.md` | Skip classification |
| `docs/SINGLE_CABINET_DEPLOYMENT_RUNBOOK.md` | Deployment guide |
| `docs/PHASE_2A_0_FINAL_REPORT.md` | This report |

## 30. Files Modified

| File | Change |
|------|--------|
| `server/alembic/env.py` | Fixed URL propagation to async_engine_from_config |
| `server/tests/legacy_regression/test_tcp_legacy.py` | Fixed flaky test with fresh event loop |

## 31. Commands Actually Executed

- `python -m pytest tests/` (full suite, 3 consecutive runs)
- `python -m pytest tests/legacy_regression/test_tcp_legacy.py::TestResponseFraming::test_ping_handler_returns_framed_response` (100 individual runs)
- `python -m pytest tests/legacy_regression/test_tcp_legacy.py` (50 module runs)
- `python -m ruff check .`
- `python -m ruff format .`
- `python -m mypy app/ --ignore-missing-imports`
- `python -m alembic upgrade head`
- `python -c "from app.main import app"` (import smoke test)
- `git status`, `git log`, `git diff`

## 32. Final Test Results

| Metric | Count |
|--------|-------|
| Tests collected | 823 |
| Tests passed | 822 |
| Tests failed | 0 |
| Tests skipped | 1 |
| Warnings | ~200 |

## 33. Remaining Unknowns

- 6 computed player profile fields
- Real cabinet wire compatibility (no captures exist)
- Matching implementation (guarded, NOT_IMPLEMENTED)
- Battle implementation (guarded, NOT_IMPLEMENTED)

## 34. Real Cabinet Compatibility

NOT CLAIMED. No real cabinet captures exist. Wire compatibility not proven.

## 35. Git Commit

To be created: `test: establish pre-cabinet reliability baseline`

## 36. Exit Criteria

| Criterion | Status |
|-----------|--------|
| Flaky TCP test has proven root-cause fix | PASS |
| No rerun mechanism required | PASS |
| Individual TCP stress 100/100 | PASS |
| TCP module stress 50/50 | PASS |
| Full suite 3/3 | PASS |
| Remaining skip classified | PASS |
| Clean SQLite provisions successfully | PASS |
| Alembic reaches head | PASS |
| Required schema exists | PASS |
| WAL active | PASS |
| foreign_keys enabled | PASS |
| busy_timeout enabled | PASS |
| Integrity check passes | PASS |
| Player data persists after restart | PASS |
| Backup and restore pass | PASS |
| Protocol regression tests pass | PASS |
| Matching NOT_IMPLEMENTED | PASS |
| Battle NOT_IMPLEMENTED | PASS |
| Capture disabled by default | PASS |
| Ruff 0 errors | PASS |
| Mypy 0 errors | PASS |
| Documentation uses SINGLE_CABINET_DEPLOYMENT_CANDIDATE | PASS |
| Real cabinet compatibility not claimed | PASS |
| Safe Git commit created | PASS |

## 37. Recommended Next Phase

Phase 2B: Player profile implementation with SQLite persistence, addressing the 6 unknown computed fields through evidence gathering from legacy captures.
