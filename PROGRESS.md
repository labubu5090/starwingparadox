# Starwing Paradox Server - Progress Tracker

## Phase 1.5R: PostgreSQL Runtime Validation (COMPLETE)

**Commit**: `405ddaf`
**Status**: Complete - PostgreSQL 16.15 validated

## SQLite-Only Migration (COMPLETE)

**Commit**: `970828d` (code) / `881abf2` (docs)
**Status**: Complete - SQLite is the only supported database backend

## Phase 2A.0: Pre-Cabinet Reliability Gate (COMPLETE)

**Commit**: `acca2c6`
**Status**: COMPLETE - All exit criteria met

## Phase 2A: Controlled Single-Cabinet Bring-Up (WAITING_FOR_CABINET)

**Commit**: TBD
**Status**: WAITING_FOR_CABINET - Preflight and capture tooling ready

### Phase 2A Readiness Results

| Metric | Value |
|--------|-------|
| Tests collected | 835 |
| Tests passed | 834 |
| Tests failed | 0 |
| Tests skipped | 1 |
| Ruff errors | 0 |
| Mypy errors | 0 |
| Capture infrastructure | 12/12 tests pass |
| Preflight script | READY (0 blocking) |
| Cabinet profile | Created |
| Capture session tools | Created |

### Deployment Status

**WAITING_FOR_CABINET** - Ready for controlled cabinet connection

### Phase 2A.0 Results

| Metric | Value |
|--------|-------|
| Tests collected | 823 |
| Tests passed | 822 |
| Tests failed | 0 |
| Tests skipped | 1 |
| Ruff errors | 0 |
| Mypy errors | 0 |
| TCP individual stress | 100/100 |
| TCP module stress | 50/50 |
| Full suite repeatability | 3/3 |
| Fresh SQLite provisioning | 15/15 checks |
| Protocol regression | 185/185 passed |

### Deployment Status

**SINGLE_CABINET_DEPLOYMENT_CANDIDATE**

Not yet PRODUCTION_READY until a real cabinet successfully connects and completes the agreed boot and player flow.

## Phase 2A-G5R: NESYS Offline Block Investigation (COMPLETE)

**Status**: BLOCKED_BY_MISSING_NESYS_LAUNCHER

### NESYS Root Cause

The game requires NesysService.exe to be running via a named pipe connection.
NesysService.exe exits immediately (code -1).

## Phase 2A-G6: D-Drive Runtime Reconstruction (COMPLETE)

**Status**: D_LAYOUT_NO_EFFECT

D: drive was reconstructed and mounted, but NesysService still exits with -1.
D: necessity remains unproven.

### G6 Results

| Metric | Value |
|--------|-------|
| D: drive | RECONSTRUCTED (217 files, 7.9 MB) |
| NesysService exit code | -1 (unchanged) |
| Named pipes created | None |
| Game NESYS status | Still offline |
| D: drive effect | NO_EFFECT |

## Phase 2A-G7: Process Monitor Trace (COMPLETE)

**Status**: COMPLETE

### G7 Results

| Metric | Value |
|--------|-------|
| Procmon availability | AVAILABLE (v4.1) |
| NesysService exit code | -1 |
| Terminal failure window | UNKNOWN |
| D drive differential | NO_MATERIAL_EFFECT |
| Network connectivity | cert3.nesys.jp REACHABLE |
| Named pipes | NOT_CREATED |

## Phase 2A-G8: TCP Runtime Differential Analysis (COMPLETE)

**Status**: COMPLETE

### Key Findings

- Run A (01:21) and Run B (01:41) had **identical game-level TCP behavior**
- Both runs: first TCP attempt fails (race condition), subsequent attempts succeed at transport level
- Both runs: `bGameConnect` never restores to 1 after first failure
- Both runs: NESYS offline
- Run B TCP server console showed zero connections (game log shows connections) — **UNEXPLAINED**

### Correction Note (2026-08-28)

**RENDERING_CRASH_STATUS**: NOT_CONFIRMED_AS_SPONTANEOUS

The operator previously stated that the apparent game crash occurred when the operator forcibly closed the game. The rendering crash (FRCPassPostProcessAA::Process) is NOT confirmed as spontaneous. Do not classify as a current blocker. Do not use operator-forced closure as renderer-failure evidence.

**messageType 103 (0x67)**: CAPTURE_SEQUENCE_CANDIDATE — not proven as PingResponse. Only one capture sequence exists. The legacy JS code (starwing.js:121) shows 0x67 as a reply to 0x66, but the proto file has no separate PingResponse message type.

**Current primary hypothesis**: First-connection startup timing / server readiness race.

### Runtime State

| Metric | Value |
|--------|-------|
| HTTP connection | CONFIRMED |
| Matching server response | CONFIRMED (identical both runs) |
| TCP listener | RUNNING |
| TCP connection (game log) | BOTH RUNS |
| TCP connection (server console) | Run A: YES, Run B: NO |
| NESYS status | OFFLINE |
| Card play | BLOCKED |
| Matching | NOT_IMPLEMENTED |
| Battle | NOT_IMPLEMENTED |
| Real playability | NOT_PROVEN |
| Primary blocker | NESYS_OFFLINE → bGameConnect_never_restores |
| Runtime difference | TCP_CONNECTION_STATE_DEPENDS_ON_GAME_FLOW |

## Phase 2A-G9: Cold-Boot Server Readiness and Post-HTTP Gating Analysis (COMPLETE)

**Status**: COMPLETE

### G9 Objectives

- Determine whether first Ping failure is caused by server startup order / TCP readiness timing
- Test three controlled startup delays (0s, 5s, 15s)
- Create cold-boot validation procedure
- Verify true TCP accept readiness
- Capture first game connection precisely
- Analyze post-HTTP gating condition (why TCP connection is never established after HTTP matching succeeds)

### G9 Results

**Startup race: DISPROVEN_FOR_THIS_RUN** — Server was ready ~3 minutes before game HTTP request.

**Post-HTTP gating: `BGAMECONNECT_GATES_TCP_CONNECTION`**

| Finding | Detail |
|---------|--------|
| NESYS CertError | Repeated during boot (status[4] option[0]), NESYS never online |
| IsOnline | 0 (NESYS offline) |
| OpenKey.json | Missing (D:/Saved/ACRSaved/SaveData/OpenKey.json) |
| SystemDataCheck | Fails → DispError → error state |
| TCP address | Resolved successfully (127.0.0.1:6666) |
| TCP connection | Never established (error state aborts callback) |
| Game close | Operator-forced (NOT spontaneous crash) |

### G9 Classification

**Primary**: `BGAMECONNECT_GATES_TCP_CONNECTION`
**Root cause**: NESYS offline → OpenKey missing → SystemDataCheck error → bGameConnect never set → TCP connection aborted

### G9 Environment

- Mypy: version 2.3.1, 0 errors on 64 source files
- Ruff: 0 errors
- Tests: 834 passed, 1 skipped, 0 failed (with protobuf runtime)

## Phase 2A-G10: OpenKey Provenance and NESYS Initialization Dependency Audit (COMPLETE)

**Status**: COMPLETE

### G10 Objectives

- Determine legitimate origin, ownership, lifecycle, and role of OpenKey.json
- Correct overreaching claims about OpenKey causality
- Inventory all OpenKey references across codebase
- Determine whether original OpenKey file exists
- Identify expected producer of OpenKey.json
- Determine read vs write behavior for each component
- Analyze SystemDataCheck causality
- Determine NesysService exit relationship to OpenKey

### G10 Results

| Finding | Detail |
|---------|--------|
| OpenKey files found | 2 (OpenKey.json, OpenKeyEvent_Galaxy.json) |
| OpenKey location | D DRIVE CONTENTS (original game content) |
| OpenKey producer | UNKNOWN (not proven to be NesysService) |
| OpenKey role | REQUIRED_CANDIDATE (one of multiple SystemDataCheck requirements) |
| SystemDataCheck | MULTIPLE_SYSTEMDATA_REQUIREMENTS |
| NesysService exit | BEFORE_OPENKEY_ACCESS |
| Provisioning context | MISSING (launcher, certificates, registry, network) |

### G10 Classification

**Primary**: `NESYS_OFFLINE_PRIMARY_GATE`
**Secondary**: `ORIGINAL_PROVISIONING_CONTEXT_MISSING`

### G10 Environment

- Mypy: version 2.3.1, 0 errors on 64 source files
- Ruff: 0 errors
- Tests: 834 passed, 1 skipped, 0 failed

## Phase 2A-G11: Upstream Repository Launch Instructions Audit (COMPLETE)

**Commit**: `99f55ed`
**Status**: COMPLETE

### G11 Objectives

- Audit https://github.com/ArcadeMachinist/StarwingParadox repository
- Determine what the upstream repository provides
- Compare upstream against local legacy-js/ files
- Answer 20 audit questions about game launch capability
- Create comprehensive audit document

### G11 Results

| Finding | Detail |
|---------|--------|
| Repository classification | MOCK_SERVER_START_ONLY |
| Game launch capability | NOT_PROVIDED |
| NESYS support | NOT_PROVIDED |
| OpenKey provisioning | NOT_PROVIDED |
| Certificate provisioning | NOT_PROVIDED |
| Registry setup | NOT_PROVIDED |
| D-drive deployment | NOT_DOCUMENTED |
| Local legacy-js/ | EXACT_CLONE of upstream at commit 020adaf |
| Our FastAPI server | MORE_COMPLETE than upstream mock server |

### G11 Classification

**Primary**: `MOCK_SERVER_START_ONLY`

**Rationale**: Repository provides mock HTTP/TCP server for Starwing Paradox. Repository does NOT provide game launch, NESYS, OpenKey, certificates, or cabinet environment. Repository is explicitly labeled "WORK IN PROGRESS".

### G11 Environment

- Mypy: version 2.3.1, 0 errors on 64 source files
- Ruff: 0 errors
- Tests: 834 passed, 1 skipped, 0 failed

## Current State

| Metric | Value |
|--------|-------|
| Tests collected | 835 |
| Tests passed | 834 |
| Tests failed | 0 |
| Tests skipped | 1 |
| Ruff errors | 0 |
| Mypy errors | 0 |
| Database | SQLite-only |
| Protobuf runtime | LOADED (protobuf==7.36.0, HAS_GENERATED=True) |
| TCP flaky test | FIXED |
| Deployment status | SINGLE_CABINET_DEPLOYMENT_CANDIDATE |
| NESYS | OFFLINE (CertError, pipe does not exist) |
| D: drive | NOT MOUNTED |
| OpenKey | MISSING_AT_EXPECTED_RUNTIME_PATH |
| G9 startup race | DISPROVEN |
| G9 post-HTTP gating | CLASSIFIED (BGAMECONNECT_GATES_TCP_CONNECTION) |
| G10 OpenKey producer | UNKNOWN |
| G10 SystemDataCheck | MULTIPLE_REQUIREMENTS |
| G10 NesysService exit | BEFORE_OPENKEY_ACCESS |
| G11 upstream classification | MOCK_SERVER_START_ONLY |
| G11 game launch | NOT_PROVIDED |
| G11 NESYS support | NOT_PROVIDED |
| G11 local legacy-js/ | EXACT_CLONE of upstream |

## SQLite Architecture

- **Backend**: aiosqlite + SQLAlchemy 2.0
- **Default URL**: `sqlite+aiosqlite:///./data/starwing.db`
- **PRAGMAs**: foreign_keys=ON, busy_timeout=10000 (per-connection via event listener)
- **WAL mode**: Persisted in database file
- **Schema**: 17 tables + alembic_version, managed by Alembic

## Exit Criteria Met (Phase 2A.0)

- [x] Flaky TCP test root-caused and fixed
- [x] No rerun mechanism required
- [x] Individual TCP stress 100/100
- [x] TCP module stress 50/50
- [x] Full suite 3/3
- [x] Remaining skip classified (OPTIONAL_EXTERNAL_TOOL)
- [x] Clean SQLite provisions successfully
- [x] Alembic reaches head
- [x] Required schema exists
- [x] WAL active
- [x] foreign_keys enabled
- [x] busy_timeout enabled
- [x] Integrity check passes
- [x] Player data persists after restart
- [x] Backup and restore pass
- [x] Protocol regression tests pass
- [x] Matching NOT_IMPLEMENTED
- [x] Battle NOT_IMPLEMENTED
- [x] Capture disabled by default
- [x] Ruff 0 errors
- [x] Mypy 0 errors
- [x] Documentation uses SINGLE_CABINET_DEPLOYMENT_CANDIDATE
- [x] Real cabinet compatibility not claimed

## Remaining Unknowns

- 6 computed player profile fields
- Real cabinet wire compatibility (no captures exist)
- Matching implementation (guarded, NOT_IMPLEMENTED)
- Battle implementation (guarded, NOT_IMPLEMENTED)

## Recommended Next Phase

Phase 2B: Player profile implementation with SQLite persistence
