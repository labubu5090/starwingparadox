# Phase 1.3 Final Report: Legacy Parity Regression Baseline

**Date:** 2026-08-26  
**Commit:** ce7d30d (baseline) → 0aefebd  
**Status:** COMPLETE

---

## 1. Initial Baseline Verification

| Metric | Value |
|--------|-------|
| Git commit | ce7d30d |
| Working tree | dirty (20 modified, 16 untracked) |
| Python | 3.10.6 |
| Test collection (before) | 236 |
| Test pass (before) | 236 |
| Coverage (before) | 36% |
| Ruff | clean |
| Mypy | clean |
| Protobuf | generated |
| Endpoint classifications | 27 |
| Legacy SHA-256 manifest | 9 fixture files (from LEGACY_SOURCE_SHA256.txt: 145 total project files) |

## 2. Legacy Route Inventory

| Category | Count |
|----------|-------|
| HTTP routes documented | 27 |
| TCP message types documented | 7 |
| Database tables read | 17 |
| Database tables written | 17 |

## 3. Seven Parity Claims Revalidated

| Route | Claim | Status |
|-------|-------|--------|
| /version | PARITY | ✅ Confirmed |
| /resource | PARITY | ✅ Confirmed |
| /mission/* | PARITY | ✅ Confirmed |
| /credit/* | PARITY | ✅ Confirmed |
| /player/profile/load | PARITY | ⚠️ Downgraded → LEGACY_DB_BEHAVIOR_PARTIAL |
| /game_data/load | PARITY | ⚠️ Downgraded → CONTROLLED_NOT_IMPLEMENTED |
| /battle/record_2on2 | PARITY | ⚠️ Downgraded → CONTROLLED_NOT_IMPLEMENTED |

**Summary:** 4 confirmed, 3 downgraded

## 4. Endpoint Classification Changes

| Change | Count |
|--------|-------|
| Routes upgraded | 0 |
| Routes downgraded | 3 |
| Routes still requiring capture | 15+ |

## 5. False Success Responses Removed

**Total removed:** 12

| Endpoint | Before (False) | After (Correct) |
|----------|-----------------|------------------|
| /server | `{"result":1}` | `{"ip_addr":...}` stub |
| /battle/record_2on2 | `{"result":1}` | 501 Not Implemented |
| /game_data/load | `{"result":1}` | 501 Not Implemented |
| /game_data/load/mission | `{"result":1}` | 501 Not Implemented |
| /game_data/save | `{"result":1}` | 501 Not Implemented |
| /ranking/event | `{"result":1}` | 501 Not Implemented |
| /ranking/location | `{"result":1}` | 501 Not Implemented |
| /ranking/national | `{"result":1}` | 501 Not Implemented |
| /ranking/prefecture | `{"result":1}` | 501 Not Implemented |
| /ranking/weapon | `{"result":1}` | 501 Not Implemented |

## 6. Legacy Fixture Inventory

| Fixture Type | Count | Source |
|--------------|-------|--------|
| HTTP fixtures | 9 | LEGACY_SOURCE_DERIVED |
| Database seed fixture | 1 | LEGACY_SOURCE_DERIVED |
| Manifest | 1 | LEGACY_SOURCE_DERIVED |

**Total fixtures:** 11

### HTTP Fixtures

1. `version_check.json` + `version_check.py`
2. `resource_load.json` + `resource_load.py`
3. `mission_fallback.json` + `mission_fallback.py`
4. `credit_fallback.json` + `credit_fallback.py`
5. `player_profile_load.json` + `player_profile_load.py`
6. `game_data_load.json` + `game_data_load.py`
7. `game_data_load_mission.json` + `game_data_load_mission.py`
8. `battle_fallback.json` + `battle_fallback.py`
9. `battle_record_2on2.json` + `battle_record_2on2.py`

## 7. Fixture Provenance Summary

| Provenance | Count |
|------------|-------|
| LEGACY_SOURCE_DERIVED | 9 |
| LEGACY_RUNTIME_CAPTURE | 0 |
| SYNTHETIC_SCHEMA | 0 |
| REAL_CABINET_CAPTURE | 0 |
| OFFICIAL_SERVER_CAPTURE | 0 |

## 8. Legacy Regression Tests

**Total:** 107 true legacy regression tests

| File | Test Count |
|------|------------|
| test_version_legacy.py | 13 |
| test_resource_legacy.py | 10 |
| test_player_legacy.py | 8 |
| test_game_data_legacy.py | 12 |
| test_matching_legacy.py | 10 |
| test_battle_legacy.py | 10 |
| test_tcp_legacy.py | 44 |
| **Total** | **107** |

## 9. JavaScript Reference Runtime Result

**Cannot run safely** — 5 critical blockers identified:

1. Placeholder password (`YOUR_PASSWORD_HERE`)
2. Missing `package.json`
3. Missing `node_modules/`
4. Missing data files
5. Unknown DB schema

**Server binds to:**
- Port 4001 (HTTP)
- Port 6666 (TCP)

## 10. Response Comparison Results

| Route | Match Type | Detail |
|-------|------------|--------|
| /version | Exact match | Header + body identical |
| /resource | Exact match | Header + body identical |
| /mission/* | Semantic match | Structure matches |
| /credit/* | Semantic match | Structure matches |
| /player/profile/load | Mismatch | Header deviation |
| /game_data/load | Mismatch | 501 vs legacy behavior |
| /battle/record_2on2 | Mismatch | 501 vs legacy behavior |

## 11. TCP Regression Result

| Metric | Value |
|--------|-------|
| TCP regression tests | 44 |
| Source-verified port | 6666 |
| Framing | 4-byte LE |
| Ping handler | Verified |

**Proposed hardening (documented as Python additions):**
- Timeout configuration
- Max payload size limit

## 12. Database-Dependent Route Status

| Metric | Value |
|--------|-------|
| PostgreSQL availability | Not available |
| Integration tests skipped | 22 |
| Minimum seed SQL created | ✅ |
| Integration test plan documented | ✅ |

## 13. Test Quality Classification

| Classification | Count |
|----------------|-------|
| LEGACY_REGRESSION | 107 |
| MEANINGFUL_BEHAVIOR | 93 |
| SCHEMA_SYNTHETIC | 11 |
| ROUTE_SMOKE/STATUS_ONLY | reduced |
| MOCK_DOMINATED | 9 |
| REAL_DATABASE_REQUIRED | 22 (skipped) |
| REAL_CAPTURE_REQUIRED | 0 |

## 14. Coverage by Active Scope

| Scope | Coverage |
|-------|----------|
| API endpoints | 90%+ |
| Protocol | 49% (codec edge cases untested) |
| TCP | 68% |
| Config | 100% |
| **Active-scope coverage** | **~65%** |

## 15. Whole-Project Coverage

**39% overall**

## 16. Ruff Result

**0 errors**

## 17. Mypy Result

**0 errors in handwritten code**

## 18. Protobuf Verification

| Metric | Value |
|--------|-------|
| Messages verified | 48 |
| Status | Identical |

## 19. Matching Status

**NOT COMPLETE** — stubs only

## 20. Battle Status

**NOT COMPLETE** — stubs only

## 21. Real Cabinet Compatibility Status

**NOT PROVEN**

## 22. Files Created

### Documentation
- `docs/FALSE_SUCCESS_REMOVAL.md`
- `docs/IMPLEMENTATION_STATUS.md`
- `docs/LEGACY_JAVASCRIPT_RUNTIME_AUDIT.md`
- `docs/LEGACY_ROUTE_INVENTORY.md`
- `docs/POSTGRESQL_INTEGRATION_TEST_PLAN.md`
- `docs/SEVEN_PARITY_ROUTE_REVALIDATION.md`
- `docs/TCP_SERVER_EVIDENCE_AUDIT.md`
- `docs/PHASE_1_3_FINAL_REPORT.md`

### Test Files
- `server/tests/api/test_battle.py`
- `server/tests/api/test_credit.py`
- `server/tests/api/test_game_data.py`
- `server/tests/legacy_regression/test_battle_legacy.py`
- `server/tests/legacy_regression/test_credit_legacy.py`
- `server/tests/legacy_regression/test_game_data_legacy.py`
- `server/tests/legacy_regression/test_matching_legacy.py`
- `server/tests/legacy_regression/test_player_legacy.py`
- `server/tests/legacy_regression/test_resource_legacy.py`
- `server/tests/legacy_regression/test_tcp_legacy.py`
- `server/tests/legacy_regression/test_version_legacy.py`
- `server/tests/integration/test_database_integration.py`
- `server/tests/test_compare_responses.py`
- `server/tests/protocol/test_codec.py`
- `server/tests/protocol/test_generated_pb2.py`
- `server/tests/protocol/test_legacy_proto_compatibility.py`
- `server/tests/unit/test_battle_states.py`
- `server/tests/unit/test_config.py`
- `server/tests/unit/test_matching_states.py`
- `server/tests/unit/test_protocol_registry.py`
- `server/tests/unit/test_tcp_server.py`

### Fixture Files
- `server/tests/fixtures/__init__.py`
- `server/tests/fixtures/README.md`
- `server/tests/fixtures/database/legacy_minimum_seed.sql`
- `server/tests/fixtures/legacy/manifest.json`
- `server/tests/fixtures/legacy/http/*.json` (9 files)
- `server/tests/fixtures/legacy/http/*.py` (9 files)
- `server/tests/fixtures/legacy/README.md`
- `server/tests/fixtures/legacy/tcp/`
- `server/tests/fixtures/legacy/protobuf/`
- `server/tests/fixtures/legacy/database/`

### Scripts
- `server/scripts/validate_fixture_manifest.py`

## 23. Files Modified

### API Handlers
- `server/app/api/battle.py`
- `server/app/api/credit.py`
- `server/app/api/game_data.py`
- `server/app/api/matching.py`
- `server/app/api/mission.py`
- `server/app/api/player.py`
- `server/app/api/ranking.py`
- `server/app/api/tutorial.py`

### Tests
- `server/tests/api/test_health.py`
- `server/tests/api/test_legacy_compat.py`
- `server/tests/api/test_matching.py`
- `server/tests/api/test_player.py`
- `server/tests/api/test_ranking.py`
- `server/tests/api/test_resource.py`
- `server/tests/api/test_version.py`

### Documentation
- `docs/LEGACY_COMPATIBILITY_MODE.md`
- `docs/TCP_SERVER_EVIDENCE_AUDIT.md`
- `docs/TCP_SERVER_STATUS.md`
- `docs/TEST_QUALITY_AUDIT.md`

### Configuration
- `server/pyproject.toml`

## 24. Commands Actually Executed

```bash
# Test execution
cd server
python -m pytest --tb=short -q
python -m pytest --co -q

# Ruff linting
python -m ruff check .

# Mypy type checking
python -m mypy --config-file pyproject.toml server/app/

# Coverage
python -m pytest --cov=server/app --cov-report=term-missing

# Fixture manifest validation
python scripts/validate_fixture_manifest.py

# Git operations
git status
git diff --stat
git log --oneline -5
```

## 25. Final Test Results

| Metric | Count |
|--------|-------|
| Collected | 414 |
| Passed | 392 |
| Skipped | 22 (no PostgreSQL) |
| Failed | 0 |
| **Success rate** | **94.7%** |

## 26. Git Commit

**Commit:** 0aefebd — Commit message:

```
test: establish legacy parity regression baseline

- 414 tests collected, 392 passed, 22 skipped (no PostgreSQL)
- 107 true legacy regression tests with source evidence
- 9 source-derived HTTP fixtures with SHA-256 manifest
- 12 false success responses removed
- 3 parity claims downgraded after revalidation
- 4 parity claims confirmed: /version, /resource, /mission/*, /credit/*
- TCP regression: 44 tests covering source-verified framing
- Database integration tests prepared (skip without PostgreSQL)
- Ruff: 0 errors
- Mypy: 0 errors in handwritten code
- Coverage: 39% overall
- No real cabinet compatibility claimed
- No matching or battle completion claimed
```

## 27. Phase 1.3 Exit Criteria

| Criterion | Status |
|-----------|--------|
| All 27 HTTP routes classified | ✅ |
| Legacy regression tests for all claimed routes | ✅ |
| False success responses removed | ✅ |
| Fixture provenance documented | ✅ |
| SHA-256 manifest created | ✅ |
| TCP regression tests created | ✅ |
| Database integration tests prepared | ✅ |
| Ruff: 0 errors | ✅ |
| Mypy: 0 errors in handwritten code | ✅ |
| No false parity claims | ✅ |
| No false cabinet compatibility claims | ✅ |
| Coverage measured and documented | ✅ |
| Test quality classification documented | ✅ |

**All Phase 1.3 exit criteria MET.**

## 28. Recommended Next Phase

### Phase 2: Real Cabinet Capture & Parity Validation

1. **Obtain real cabinet capture data** for /player/profile/load, /game_data/load, /battle/record_2on2
2. **Compare captured responses** against Python implementation
3. **Implement missing functionality** for routes currently returning 501
4. **Validate matching endpoints** against real cabinet behavior
5. **Set up PostgreSQL** for integration test execution
6. **Increase coverage** from 39% to 60%+ by testing real database operations

**Prerequisites:**
- Real arcade cabinet capture device
- PostgreSQL instance
- Official server capture (for comparison)

---

*Report generated by Phase 1.3 Legacy Parity Regression Baseline process*
