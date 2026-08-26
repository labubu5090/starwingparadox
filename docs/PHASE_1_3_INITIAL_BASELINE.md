# Phase 1.3 Initial Baseline

> **Captured:** 2026-08-26
> **Purpose:** Record verified baseline state before Phase 1.3 changes

---

## Environment

| Item | Value | Verification |
|------|-------|-------------|
| Git commit | `ce7d30d` | `git log --oneline -1` |
| Commit message | `chore: establish verified Phase 1.2 compatibility baseline` | |
| Working tree | **Dirty** — 15 modified, 16 untracked | `git status --porcelain` |
| Python version | 3.10.6 | `python --version` |
| uv version | 0.12.5 | `uv --version` |
| Ruff version | 0.16.4 | `ruff --version` |
| Mypy version | 2.3.1 | `mypy --version` |

---

## Baseline Test Results (at commit ce7d30d)

| Metric | Value | Command |
|--------|-------|---------|
| **Test collection** | 236 | `python -m pytest --collect-only -q` |
| **Test pass** | 236 | `python -m pytest --tb=short -q` |
| **Test fail** | 0 | |
| **Test skip** | 0 | |
| **Test xfail** | 0 | |
| **Test error** | 0 | |

### Test Files (at baseline)

| File | Tests |
|------|-------|
| `tests/api/test_health.py` | 3 |
| `tests/api/test_legacy_compat.py` | 24 |
| `tests/api/test_matching.py` | 20 |
| `tests/api/test_player.py` | 40 |
| `tests/api/test_ranking.py` | 24 |
| `tests/api/test_resource.py` | 3 |
| `tests/api/test_version.py` | 4 |
| `tests/protocol/test_codec.py` | 36 |
| `tests/protocol/test_generated_pb2.py` | 33 |
| `tests/protocol/test_legacy_proto_compatibility.py` | 13 |
| `tests/unit/test_battle_states.py` | 19 |
| `tests/unit/test_config.py` | 8 |
| `tests/unit/test_matching_states.py` | 21 |
| `tests/unit/test_protocol_registry.py` | 2 |
| `tests/unit/test_tcp_server.py` | 9 |
| `tests/test_compare_responses.py` | 22 |

---

## Baseline Coverage

| Metric | Value | Command |
|--------|-------|---------|
| **Overall coverage** | **36%** | `python -m pytest --cov=app --cov-report=term-missing` |
| Lines hit | 524 | |
| Lines missed | 936 | |

### Coverage by Package

| Package | Coverage | Lines |
|---------|----------|-------|
| app/api/ | 78% | 147/41 |
| app/config.py | 100% | 18/0 |
| app/dependencies.py | 77% | 24/7 |
| app/main.py | 84% | 38/7 |
| app/tcp_server.py | 68% | 70/33 |
| app/protocol/codec.py | 49% | 53/56 |
| app/protocol/registry.py | 100% | 2/0 |
| app/protocol/errors.py | 100% | 4/0 |
| app/middleware/ | 100% | 26/0 |
| app/logging_config.py | 41% | 16/23 |
| app/db/ | 0% | 0/333 |
| app/services/ | 0% | 0/102 |
| app/domain/ | 0% | 0/28 |
| app/protocol/generated/ | 11% | 12/97 |

---

## Baseline Lint Results

| Tool | Result | Command |
|------|--------|---------|
| **Ruff** | **Clean — 0 errors** | `ruff check .` |
| **Ruff format** | **89 files formatted** | `ruff format --check .` |
| **Mypy** | **Clean — 0 issues** | `mypy app/ --ignore-missing-imports` |
| **Mypy suppressions** | 2 (`# type: ignore[attr-defined]` in `codec.py`) | |

---

## Baseline Protobuf State

| Item | Value |
|------|-------|
| Proto file | `server/app/protocol/proto/starwingMessage.proto` |
| Generated file | `server/app/protocol/generated/starwingMessage_pb2.py` |
| Status | **Generated** |
| Messages | 48 (all field numbers identical to legacy) |
| Wire format | 100% compatible |
| Phantom registry entries | 5 (types 202, 205, 206, 214, 215) |

---

## Endpoint Classifications

| Classification | Count | Routes |
|---------------|-------|--------|
| VERIFIED_LEGACY_PARITY | 4 | /version, /resource, /mission/*, /credit/* |
| LEGACY_STATIC_REIMPLEMENTED | 9 | /matching/server, /matching/match_id/generate, /matching/*, all /ranking/* |
| LEGACY_DB_BEHAVIOR_PARTIAL | 7 | /player/profile/load, /player/login, /player/register, /game_data/load/mission, /game_data/load, /game_data/save, /battle/record_2on2 |
| SYNTHETIC_FOUNDATION_ONLY | 2 | /health, /ready |
| CONTROLLED_NOT_IMPLEMENTED | 2 | /mock/matching/server, /mock/* |
| VERIFIED_LEGACY_PARITY (mode=gated) | 5 | /player/login_bonus, /player/*, /game_data/*, /battle/*, /tutorial/* |
| **Total** | **27** (unique routes) + 5 (gated fallbacks) | |

**Note:** 7 routes were originally classified as VERIFIED_LEGACY_PARITY. The `SEVEN_PARITY_ROUTE_REVALIDATION.md` confirmed 4 and downgraded 3 (player/profile/load, game_data/load, battle/record_2on2).

---

## Legacy Source Integrity

| Item | Value |
|------|-------|
| SHA-256 manifest | `docs/LEGACY_SOURCE_SHA256.txt` |
| **Total files in manifest** | **145** |
| LEGACY_ORIGINAL | 34 |
| PYTHON_REWRITE | 60 |
| TEST | 21 |
| GENERATED | 2 |
| DOCUMENTATION | 15 |
| UNCLASSIFIED | 13 |
| Legacy source preserved | Yes (`legacy-js/` directory) |
| Legacy modification | None (verified read-only) |

---

## Current Working Tree Delta

The working tree at the time of Phase 1.3 baseline capture contains changes beyond ce7d30d:

### Modified Files (15)

| File | Change summary |
|------|---------------|
| `docs/LEGACY_COMPATIBILITY_MODE.md` | Updated behavior matrix |
| `docs/TCP_SERVER_EVIDENCE_AUDIT.md` | Extended evidence |
| `docs/TCP_SERVER_STATUS.md` | Status updates |
| `server/app/api/battle.py` | Compat mode changes |
| `server/app/api/credit.py` | Compat mode changes |
| `server/app/api/game_data.py` | Compat mode changes |
| `server/app/api/matching.py` | Compat mode changes |
| `server/app/api/mission.py` | Compat mode changes |
| `server/app/api/player.py` | Compat mode changes |
| `server/app/api/ranking.py` | Compat mode changes |
| `server/app/api/tutorial.py` | Compat mode changes |
| `server/pyproject.toml` | Dependency update |
| `server/tests/api/test_legacy_compat.py` | Expanded tests |
| `server/tests/api/test_matching.py` | Expanded tests |
| `server/tests/api/test_ranking.py` | Expanded tests |

### Untracked Files (16)

| File/Dir | Purpose |
|----------|---------|
| `docs/FALSE_SUCCESS_REMOVAL.md` | Audit: removed fake success responses |
| `docs/LEGACY_JAVASCRIPT_RUNTIME_AUDIT.md` | JS runtime behavior audit |
| `docs/LEGACY_ROUTE_INVENTORY.md` | Complete route inventory |
| `docs/PHASE_1_2_FINAL_REPORT.md` | Phase 1.2 final report |
| `docs/POSTGRESQL_INTEGRATION_TEST_PLAN.md` | DB integration test plan |
| `docs/SEVEN_PARITY_ROUTE_REVALIDATION.md` | 7-route revalidation |
| `server/scripts/validate_fixture_manifest.py` | Fixture validation script |
| `server/tests/api/test_battle.py` | Battle endpoint tests |
| `server/tests/api/test_credit.py` | Credit endpoint tests |
| `server/tests/api/test_game_data.py` | Game data endpoint tests |
| `server/tests/fixtures/database/` | Database fixtures |
| `server/tests/fixtures/legacy/` | Legacy HTTP fixtures |
| `server/tests/integration/` | Integration tests |
| `server/tests/legacy_regression/` | Legacy regression tests |

### Current Working Tree Test Count

After applying the working tree changes, test collection increases from 236 to **414** (178 new tests added across new test files).

---

## Exit Criteria for Phase 1.3

| Criterion | Status |
|-----------|--------|
| Baseline commit identified | `ce7d30d` |
| Test count recorded | 236 |
| Coverage recorded | 36% |
| Lint clean | Ruff 0, Mypy 0 |
| Protobuf generated | Yes |
| Endpoint classifications documented | 27 routes |
| Legacy manifest captured | 145 files SHA-256 |
| Working tree state documented | Dirty (15 modified, 16 untracked) |
