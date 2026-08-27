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

## Phase 2A-G5R: NESYS Offline Block Investigation (IN PROGRESS)

**Status**: BLOCKED_BY_MISSING_NESYS_LAUNCHER

### NESYS Root Cause

The game requires NesysService.exe to be running via a named pipe connection.
NesysService.exe exits immediately (code -1) because:
1. D: drive is NOT MOUNTED (does not exist on this system)
2. No launcher/startup script starts NesysService
3. No Windows certificates for NESYS
4. No registry configuration for NESYS
5. No parent process context

### Current Runtime State

| Metric | Value |
|--------|-------|
| HTTP server discovery | VERIFIED_WORKING |
| Matching server response | VERIFIED_RECEIVED |
| NESYS status | OFFLINE |
| Card play | BLOCKED_BY_NESYS_OFFLINE |
| Normal game flow | NOT_REACHED |
| Coin/start validation | NOT_YET_VALID |
| Matching | NOT_IMPLEMENTED |
| Battle | NOT_IMPLEMENTED |
| Real playability | NOT_PROVEN |
| Primary blocker | NESYS_SERVICE_INITIALIZATION |

## Current State

| Metric | Value |
|--------|-------|
| Tests collected | 823 |
| Tests passed | 822 |
| Tests failed | 0 |
| Tests skipped | 1 |
| Ruff errors | 0 |
| Mypy errors | 0 |
| Database | SQLite-only |
| TCP flaky test | FIXED |
| Deployment status | SINGLE_CABINET_DEPLOYMENT_CANDIDATE |
| NESYS | OFFLINE (pipe does not exist) |
| D: drive | NOT MOUNTED |

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
