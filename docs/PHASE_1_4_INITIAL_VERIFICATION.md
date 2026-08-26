# Phase 1.4 Initial Verification

**Date:** 2026-08-26
**Status:** VERIFIED

---

## 1. Git State

| Metric | Value |
|--------|-------|
| HEAD | 0aefebd |
| Commit message | `test: establish legacy parity regression baseline` |
| Working tree | 2 untracked files (`docs/POSTGRESQL_ENVIRONMENT_DISCOVERY.md`, `tools/`) |
| Commits in repo | 2 |

```
$ git log --oneline -5
0aefebd test: establish legacy parity regression baseline
ce7d30d chore: establish verified Phase 1.2 compatibility baseline
```

```
$ git status --short
?? docs/POSTGRESQL_ENVIRONMENT_DISCOVERY.md
?? tools/
```

## 2. Environment

| Metric | Value |
|--------|-------|
| Python | 3.10.6 |
| Platform | win32 |

## 3. Test Results

| Metric | Value |
|--------|-------|
| Test collection | 414 |
| Test pass | 392 |
| Test skip | 22 |
| Test fail | 0 |
| Success rate | 94.7% |
| Warnings | 3 |

```
$ python -m pytest tests/ --collect-only -q
414 tests collected in 0.13s
```

```
$ python -m pytest tests/ -ra --tb=short -q
392 passed, 22 skipped, 3 warnings in 0.92s
```

### Skipped Test Details

All 22 skipped tests are in `tests/integration/test_database_integration.py` — skipped because `TEST_DATABASE_URL` environment variable is not set (no PostgreSQL available).

```
SKIPPED [1] tests/integration/test_database_integration.py:111: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:119: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:127: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:133: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:172: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:185: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:223: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:230: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:237: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:243: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:263: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:275: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:285: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:293: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:310: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:328: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:352: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:395: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:438: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:450: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:462: TEST_DATABASE_URL environment variable not set
SKIPPED [1] tests/integration/test_database_integration.py:484: TEST_DATABASE_URL environment variable not set
```

## 4. Coverage

| Metric | Value |
|--------|-------|
| Overall coverage | 39% |

## 5. Linting & Type Checking

| Tool | Result |
|------|--------|
| Ruff | 0 errors |
| Mypy | 0 errors in handwritten code |

## 6. Legacy Regression Tests

| Metric | Value |
|--------|-------|
| Total legacy regression tests | 107 |

```
| File                        | Test Count |
|-----------------------------|------------|
| test_version_legacy.py      | 13         |
| test_resource_legacy.py     | 10         |
| test_player_legacy.py       | 8          |
| test_game_data_legacy.py    | 12         |
| test_matching_legacy.py     | 10         |
| test_battle_legacy.py       | 10         |
| test_tcp_legacy.py          | 44         |
| **Total**                   | **107**    |
```

## 7. SHA-256 Manifest

| Metric | Value |
|--------|-------|
| Fixture manifest entries | 9 |
| Total project files hashed | 145 (from LEGACY_SOURCE_SHA256.txt) |

## 8. Legacy Files

| Category | Count |
|----------|-------|
| LEGACY_ORIGINAL | 34 |
| PYTHON_REWRITE | 60 |
| TEST | 21 |
| GENERATED | 2 |
| DOCUMENTATION | 15 |
| UNCLASSIFIED | 13 |
| **Total** | **145** |

## 9. Endpoint Classifications

| Metric | Value |
|--------|-------|
| Total HTTP routes classified | 27 |
| TCP message types documented | 7 |
| Database tables read | 17 |
| Database tables written | 17 |

## 10. Parity Status

| Metric | Value |
|--------|-------|
| Parity confirmed | 4 |
| Parity downgraded | 3 |

### Confirmed (4)
- `/version` — Exact match
- `/resource` — Exact match
- `/mission/*` — Semantic match
- `/credit/*` — Semantic match

### Downgraded (3)
- `/player/profile/load` → LEGACY_DB_BEHAVIOR_PARTIAL
- `/game_data/load` → CONTROLLED_NOT_IMPLEMENTED
- `/battle/record_2on2` → CONTROLLED_NOT_IMPLEMENTED

## 11. Exit Criteria

| Criterion | Status |
|-----------|--------|
| Git HEAD verified | ✅ 0aefebd |
| Working tree clean (aside from untracked) | ✅ |
| 414 tests collected | ✅ |
| 392 tests pass | ✅ |
| 22 tests skip (no PostgreSQL) | ✅ |
| 0 tests fail | ✅ |
| Coverage 39% | ✅ |
| Ruff 0 errors | ✅ |
| Mypy 0 errors | ✅ |
| 107 legacy regression tests | ✅ |
| SHA-256 manifest present | ✅ |
| 27 endpoints classified | ✅ |
| 4 parity confirmed | ✅ |
| 3 parity downgraded | ✅ |

**All Phase 1.4 initial verification checks PASSED.**

---

*Report generated by Phase 1.4 Initial Verification process*
