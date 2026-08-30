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

## Phase 2A-G12: Original Cabinet Runtime Gap and NesysService Launcher Search (COMPLETE)

**Status**: COMPLETE

### G12 Objectives

- Determine whether operator-owned content contains original launcher
- Search for startup artifacts, process manager, service wrapper
- Audit all executable candidates
- Analyze shortcut and startup evidence
- Determine NesysService invocation evidence
- Analyze system-drive gap
- Determine NesysService standalone capability
- Make safe launch test decision

### G12 Results

| Finding | Detail |
|---------|--------|
| Executables found | 3 (AcrGame.exe, AcrGame-Win64-Shipping.exe, NesysService.exe) |
| Script files found | 0 (.bat, .cmd, .lnk, .reg, .vbs, .ps1) |
| Launcher candidates | NOT_FOUND |
| NesysService binary evidence | STRONG (Windows Service, named pipe, certificates, network) |
| External invocation evidence | NONE |
| System drive backup | D_DRIVE_ONLY_BACKUP |
| NesysService standalone | PARENT_CONTEXT_REQUIRED |
| Safe launch test | PARTIAL_INVOCATION_NOT_SAFE_TO_TEST |

### G12 Classification

**Primary**: `D_DRIVE_ONLY_BACKUP_CONFIRMED`

**Rationale**: Only D: drive content is present. No C: drive content found. No system drive components found. No startup configuration found. No registry found. No certificate store found. No Windows Service configuration found.

### G12 Environment

- Mypy: version 2.3.1, 0 errors on 64 source files
- Ruff: 0 errors
- Tests: 834 passed, 1 skipped, 0 failed

## Phase 2A-G13: IDA Static Runtime Reconstruction (COMPLETE)

**Status**: COMPLETE

### G13 Objectives

- Perform IDA static analysis of NesysService.exe, AcrGame.exe, AcrGame-Win64-Shipping.exe
- Reconstruct missing runtime contract between game, SCM, Registry, certificate store, named pipe
- Document service control, registry, pipe, certificate, and network contracts
- Determine process startup sequence
- Identify missing system-drive dependencies

### G13 Results

| Finding | Detail |
|---------|--------|
| Service name | NesysService (CONFIRMED) |
| Registry path | HKLM\SOFTWARE\taito\typex (CONFIRMED) |
| Certificate store | MY\.Default (CONFIRMED) |
| Named pipe | \\.\pipe\nesys_games (CONFIRMED) |
| Network endpoints | cert3.nesys.jp, data.nesys.jp, nesys.taito.co.jp, fjm170920zero.nesica.net (CONFIRMED) |
| Process launch | AcrGame.exe → AcrGame-Win64-Shipping.exe (CONFIRMED) |
| Runtime contract | PARTIAL_STATIC_RUNTIME_CONTRACT |
| Missing components | Service registration, certificate installation, registry configuration |

### G13 Classification

**Primary**: `PARTIAL_STATIC_RUNTIME_CONTRACT`

**Rationale**: Service identity, named pipe protocol, and network endpoints are confirmed. However, critical startup elements remain unresolved: the exact Windows Service registration, certificate installation, and Registry configuration.

### G13 Environment

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
| G12 system drive backup | D_DRIVE_ONLY_BACKUP_CONFIRMED |
| G12 launcher candidates | NOT_FOUND |
| G12 NesysService standalone | PARENT_CONTEXT_REQUIRED |
| G13 service name | NesysService (CONFIRMED) |
| G13 registry path | HKLM\SOFTWARE\taito\typex (CONFIRMED) |
| G13 certificate store | MY\.Default (CONFIRMED) |
| G13 named pipe | \\.\pipe\nesys_games (CONFIRMED) |
| G13 network endpoints | cert3.nesys.jp, data.nesys.jp, nesys.taito.co.jp, fjm170920zero.nesica.net (CONFIRMED) |
| G13 runtime contract | PARTIAL_STATIC_RUNTIME_CONTRACT |
| G12 safe launch test | PARTIAL_INVOCATION_NOT_SAFE_TO_TEST |
| G12 service registration | MISSING |
| G12 certificate installation | MISSING |

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

## Phase 2A-G14: Offline Service Registration Reconstruction (COMPLETE)

**Commit**: TBD
**Status**: COMPLETE
**Classification**: `EXTERNAL_REGISTRATION_REQUIRED`

### G14 Results

| Metric | Value |
|--------|-------|
| Service name | NesysService (CONFIRMED) |
| Binary path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe (CONFIRMED) |
| Self-installation | NOT_FOUND |
| Registration mechanism | EXTERNAL (installer, system image, or deployment package) |
| Certificate store | MY\.Default (CONFIRMED) |
| Certificate subject | nesys (CONFIRMED) |
| Private key | PROBABLY_REQUIRED (inference) |
| cert3.nesys.jp | UNRESOLVED |
| Registry values | 8 values (CONFIRMED) |
| Safe to register | FALSE |

### G14 Key Findings

1. **Service does NOT contain self-installation code** - Only service mode implemented
2. **Registration was performed externally** - Installer, system image, or deployment package
3. **Certificate private key acquisition NOT_SHOWN** - No direct evidence found
4. **cert3.nesys.jp purpose UNRESOLVED** - Hostname reference only
5. **Registry default values NOT_SHOWN** - Cannot determine defaults
6. **Service registration is NOT safe or complete** - Critical items unresolved

### G14 Documents Created

| Document | Path |
|----------|------|
| G14 Initial Baseline | docs/PHASE_2A_G14_INITIAL_BASELINE.md |
| G14 Analysis Plan | docs/PHASE_2A_G14_ANALYSIS_PLAN.md |
| Service Registration Contract | docs/NESYSERVICE_REGISTRATION_CONTRACT.md |
| Command-Line Modes | docs/NESYSERVICE_COMMAND_LINE_MODES.md |
| Certificate Data Flow | docs/NESYSERVICE_CERTIFICATE_DATA_FLOW.md |
| cert3.nesys.jp Relationship | docs/CERT3_NESYS_JP_RELATIONSHIP.md |
| typex Registry Semantics | docs/TYPEX_REGISTRY_SEMANTICS.md |
| File-Path Dependencies | docs/NESYSERVICE_FILE_PATH_DEPENDENCIES.md |
| Safe Registration Assessment | docs/NESYSERVICE_SAFE_REGISTRATION_ASSESSMENT.md |
| G14 Final Report | docs/PHASE_2A_G14_FINAL_REPORT.md |

### G14 Artifacts Created

| Artifact | Path |
|----------|------|
| Registration Manifest | artifacts/phase_2a_g14/nesys_service_registration_manifest.json |
| Certificate Dependency | artifacts/phase_2a_g14/certificate_dependency.json |
| Registry Semantics | artifacts/phase_2a_g14/registry_semantics.json |

### G13 Corrections Applied

| Document | Correction | Reason |
|----------|------------|--------|
| PHASE_2A_G13_FINAL_REPORT.md | Removed "connects to cert3.nesys.jp" | Hostname reference ≠ connection |
| PHASE_2A_G13_FINAL_REPORT.md | Removed "retrieves certificate" | Store API ≠ retrieval |
| NESYSERVICE_CERTIFICATE_CONTRACT.md | Corrected "retrieve NESYS certificates" | Overstated evidence |
| NESYSERVICE_CERTIFICATE_CONTRACT.md | Corrected "Private key: (required)" | Inference, not confirmed |
| NESYSERVICE_NETWORK_CONTRACT.md | Corrected "connects to cert3.nesys.jp for certificate operations" | Overstated evidence |
| artifacts/phase_2a_g13/runtime_contract.json | Updated service, certificates, and network sections | Corrected overstated claims |

## Phase 2A-G15: External Registration Mechanism Investigation (COMPLETE)

**Commit**: TBD
**Status**: COMPLETE
**Classification**: `NO_NEW_REGISTRATION_EVIDENCE`

### G15 Results

| Metric | Value |
|--------|-------|
| Deployment artifacts found | 0 |
| Installer packages found | 0 |
| Recovery images found | 0 |
| Service registration evidence | NONE |
| Registry provisioning evidence | NONE |
| Startup orchestration evidence | NONE |
| Recovery sources available | 1 (D-drive backup, incomplete) |
| Recovery sources NOT_FOUND | 11 |
| Safe to register | FALSE |

### G15 Key Findings

1. **No deployment artifacts found** - No scripts, installers, or recovery images
2. **No service registration evidence** - No scripts or logs with service references
3. **No registry provisioning data** - No artifacts define typex values
4. **No startup orchestration evidence** - No startup scripts or shortcuts
5. **Most recovery sources NOT_AVAILABLE** - Only D-drive backup exists
6. **Service configuration partially recovered** - Name and path confirmed
7. **G14 classification maps to predefined** - EXTERNAL_REGISTRATION_REQUIRED → SYSTEM_IMAGE_OR_INSTALLER_REQUIRED

### G15 Documents Created

| Document | Path |
|----------|------|
| G15 Initial Baseline | docs/PHASE_2A_G15_INITIAL_BASELINE.md |
| G15 Analysis Plan | docs/PHASE_2A_G15_ANALYSIS_PLAN.md |
| Deployment Artifact Inventory | docs/DEPLOYMENT_ARTIFACT_INVENTORY.md |
| Installer and Image Candidates | docs/INSTALLER_AND_IMAGE_CANDIDATES.md |
| External Service Registration Evidence | docs/EXTERNAL_SERVICE_REGISTRATION_EVIDENCE.md |
| NesysService Deployment Residue | docs/NESYSERVICE_DEPLOYMENT_RESIDUE.md |
| NesysService Startup Orchestration | docs/NESYSERVICE_STARTUP_ORCHESTRATION.md |
| typex Provisioning Evidence | docs/TYPEX_PROVISIONING_EVIDENCE.md |
| Authorized Recovery Source Matrix | docs/AUTHORIZED_RECOVERY_SOURCE_MATRIX.md |
| G14 Classification Mapping | docs/G14_CLASSIFICATION_MAPPING.md |
| G15 Final Report | docs/PHASE_2A_G15_FINAL_REPORT.md |

### G15 Artifacts Created

| Artifact | Path |
|----------|------|
| Deployment Artifact Inventory | artifacts/phase_2a_g15/deployment_artifact_inventory.json |
| External Registration Evidence | artifacts/phase_2a_g15/external_registration_evidence.json |
| Startup Orchestration | artifacts/phase_2a_g15/startup_orchestration.json |
| Recovery Source Matrix | artifacts/phase_2a_g15/recovery_source_matrix.json |

## Phase 2A-G16: Original Runtime Recovery Closure and Clean-room Compatibility Boundary (COMPLETE)

**Commit**: TBD
**Status**: COMPLETE
**Classification**: CLEANROOM_COMPATIBILITY_SCOPE_DEFINED

### G16 Results

| Metric | Value |
|--------|-------|
| Recovery branch | CLOSED |
| Evidence consolidated | 55 confirmed, 56 unresolved |
| Interface facts eligible | 35 |
| Restricted behaviors | 12 |
| Protocol commands classified | 91 (8 confirmed, 20 protocol-identified, 63 unknown) |
| Implementation gaps | 41 not implemented, 3 partially implemented |
| Synthetic fixtures created | 4 files |
| Security boundary violations | 0 |

### G16 Key Findings

1. **Recovery branch closed** - No safe reconstruction from available backup
2. **Evidence consolidated** - 55 confirmed interface facts documented
3. **Startup model corrected** - Three models produced (confirmed, plausible, failure)
4. **Input eligibility defined** - 35 eligible interface facts identified
5. **Protocol confidence matrix** - 91 commands classified
6. **Compatibility specification** - Clean-room design established
7. **Implementation gaps identified** - 41 not implemented behaviors documented
8. **Security boundary established** - No violations found
9. **Decision record created** - Recovery branch closure justified
10. **Roadmap rebased** - G17 recommended as next phase

### G16 Documents Created

| Document | Path |
|----------|------|
| G16 Initial Baseline | docs/PHASE_2A_G16_INITIAL_BASELINE.md |
| G16 Analysis Plan | docs/PHASE_2A_G16_ANALYSIS_PLAN.md |
| Recovery Closure | docs/ORIGINAL_RUNTIME_RECOVERY_CLOSURE.md |
| Evidence Matrix | docs/G12_G15_CONSOLIDATED_EVIDENCE_MATRIX.md |
| Startup Model Correction | docs/ORIGINAL_STARTUP_MODEL_CORRECTION.md |
| Input Eligibility | docs/CLEANROOM_INPUT_ELIGIBILITY.md |
| Protocol Confidence | docs/NESYS_PROTOCOL_CONFIDENCE_MATRIX.md |
| Compatibility Spec | docs/CLEANROOM_COMPATIBILITY_SPECIFICATION.md |
| Gap Analysis | docs/CURRENT_IMPLEMENTATION_GAP_ANALYSIS.md |
| Security Boundary | docs/SECURITY_AND_AUTHORIZATION_BOUNDARY.md |
| Decision Record | docs/ADR_ORIGINAL_NESYSERVICE_RECOVERY_CLOSURE.md |
| G16 Final Report | docs/PHASE_2A_G16_FINAL_REPORT.md |

### G16 Artifacts Created

| Artifact | Path |
|----------|------|
| Recovery Closure | artifacts/phase_2a_g16/recovery_closure.json |
| Evidence Matrix | artifacts/phase_2a_g16/consolidated_evidence.json |
| Input Eligibility | artifacts/phase_2a_g16/cleanroom_input_eligibility.json |
| Protocol Confidence | artifacts/phase_2a_g16/protocol_confidence_matrix.json |
| Gap Analysis | artifacts/phase_2a_g16/implementation_gap_analysis.json |

### G16 Synthetic Fixtures Created

| Fixture | Path |
|---------|------|
| README | tests/fixtures/starwing_cleanroom/README.md |
| Command Catalog | tests/fixtures/starwing_cleanroom/command_catalog.json |
| Lifecycle Cases | tests/fixtures/starwing_cleanroom/lifecycle_cases.json |
| Invalid Cases | tests/fixtures/starwing_cleanroom/invalid_cases.json |

### G16 Audit Note

The previous G16 recommendation "Service Registration Feasibility Assessment" was replaced because G15 found no external registration or provisioning evidence. The current G16 is "Original Runtime Recovery Closure and Clean-room Compatibility Boundary".

## Phase 2A-G17: Synthetic Transport and Protocol State-Machine Foundation (COMPLETE)

**Commit**: TBD
**Status**: COMPLETE
**Classification**: SYNTHETIC_PROTOCOL_FOUNDATION_COMPLETE

### G17 Results

| Metric | Value |
|--------|-------|
| pytest | 974 passed |
| skipped | 1 |
| failed | 0 |
| Tests added | 140 |
| Ruff | 0 errors |
| Mypy | 0 errors on 74 source files |
| Typed source files | 74 |
| Source files created | 10 |
| Test files created | 11 |
| Documents created | 12 |
| Artifacts created | 4 |

### G17 Key Findings

1. **Transport abstraction implemented**: Abstract interface with synthetic implementation
2. **Command catalog loaded**: 28 commands from G16 evidence
3. **State machine implemented**: 7 states with 12 allowed transitions
4. **Frame validation implemented**: Minimum size, maximum size, catalog validation
5. **Dispatcher implemented**: Handler registration, direction validation, lifecycle constraints
6. **Lifecycle controller implemented**: Complete synthetic lifecycle
7. **Safety guards implemented**: No prohibited imports, no production endpoints
8. **Observability implemented**: 10 event types with structured logging
9. **Test suite comprehensive**: 140 new tests, all passing
10. **No regressions**: All existing tests still pass

### G17 Documents Created

| Document | Path |
|----------|------|
| G17 Initial Baseline | docs/PHASE_2A_G17_INITIAL_BASELINE.md |
| G17 Implementation Plan | docs/PHASE_2A_G17_IMPLEMENTATION_PLAN.md |
| Transport Architecture | docs/CLEANROOM_TRANSPORT_ARCHITECTURE.md |
| Command Catalog | docs/CLEANROOM_COMMAND_CATALOG.md |
| Session State Machine | docs/CLEANROOM_SESSION_STATE_MACHINE.md |
| Frame Validation | docs/CLEANROOM_FRAME_VALIDATION.md |
| Dispatch Foundation | docs/CLEANROOM_DISPATCH_FOUNDATION.md |
| Synthetic Test Strategy | docs/CLEANROOM_SYNTHETIC_TEST_STRATEGY.md |
| Safety Verification | docs/CLEANROOM_G17_SAFETY_VERIFICATION.md |
| G17 Final Report | docs/PHASE_2A_G17_FINAL_REPORT.md |

### G17 Artifacts Created

| Artifact | Path |
|----------|------|
| Implementation Status | artifacts/phase_2a_g17/implementation_status.json |
| Test Coverage Matrix | artifacts/phase_2a_g17/test_coverage_matrix.json |
| Safety Guard Results | artifacts/phase_2a_g17/safety_guard_results.json |
| State Transition Matrix | artifacts/phase_2a_g17/state_transition_matrix.json |

## Remaining Unknowns

- 6 computed player profile fields
- Real cabinet wire compatibility (no captures exist)
- Matching implementation (guarded, NOT_IMPLEMENTED)
- Battle implementation (guarded, NOT_IMPLEMENTED)
- External service registration mechanism (CONFIRMED: UNKNOWN)
- Certificate private key acquisition
- cert3.nesys.jp purpose
- Registry default values
- File path requirements
- Service display name, description, dependencies, failure actions
- Service SID type, preshutdown timeout
- Event log source
- Installation source, uninstall source

## Phase 2A-G18: Evidence-Locked Codec and Deterministic Session Harness (COMPLETE)

**Commit**: TBD
**Status**: COMPLETE - All exit criteria met
**Classification**: EVIDENCE_LOCKED_CODEC_AND_DETERMINISTIC_HARNESS

### G18 Summary

Phase 2A-G18 established an evidence-locked codec, deterministic timeout model, session scenario harness, and expanded safety guards for the clean-room protocol foundation. All G17 semantic overreach was identified and corrected.

### G18 Deliverables

| Deliverable | Count |
|-------------|-------|
| New source modules | 6 |
| New test modules | 6 |
| Bug fixes | 3 |
| Documentation | 1 |
| Total new tests | 82 |
| Total tests | 222 |

### G18 New Source Modules

| Module | Purpose |
|--------|---------|
| `codec.py` | Evidence-locked codec with explicit evidence levels |
| `timeout.py` | Deterministic clock and timeout model |
| `harness.py` | Session scenario harness |
| `scenarios.py` | Versioned synthetic scenarios |
| `invariants.py` | State-machine invariant checker |
| `safety.py` | Expanded safety guards |

### G18 Bug Fixes

1. **`run_lifecycle` dispatch bug** (CRITICAL): Lifecycle commands with `numeric_id=None` were unreachable via `get_by_id()`. Fixed to dispatch by `message_name`.
2. **`receive_client_start` logic bug** (MEDIUM): `START_PENDING` appeared in both duplicate-check and valid-state conditions. Fixed to only accept `TRANSPORT_OPEN`.
3. **`close()` event recording** (LOW): Non-terminal close only recorded TRANSPORT_CLOSED. Now records both SESSION_FAILED and TRANSPORT_CLOSED.

### G18 Test Results

```
222 tests passed, 0 failed
Mypy: 0 errors (16 source files)
Ruff: 0 errors
```

### G18 Quality Gates

| Gate | Status |
|------|--------|
| All tests pass | PASS |
| Mypy 0 errors | PASS |
| Ruff 0 errors | PASS |
| No restricted imports | PASS |
| No production hostnames | PASS |
| No certificate references | PASS |
| No pipe paths | PASS |
| No registry paths | PASS |
| No deployment artifacts | PASS |

### G18 Documents Created

| Document | Path |
|----------|------|
| G17 Command Implementation Audit | docs/G17_COMMAND_IMPLEMENTATION_AUDIT.md |
| G18 Final Report | docs/PHASE_2A_G18_FINAL_REPORT.md |

### Recommended Next Phase

Phase 2A-G19: Runtime Integration and Traffic Pattern Validation

## Phase 2A-G19: Game Client Contract Mapping for Private Server (COMPLETE)

**Commit**: TBD (single commit)
**Status**: COMPLETE - All exit criteria met
**Classification**: GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

### G19 Summary

Phase 2A-G19 mapped the game-client-visible contracts required for an operator-owned private
server, using the game's own executables and DLLs (Starwing Paradox Shipping build, launcher,
GALAXYIO, Lua524, QRreader) as the primary source of truth. Static PE analysis confirmed
multiple independent transports (HTTP via WININET, raw TCP via WS2_32, local NESYS named pipe),
the module structure, and the command families for matching, battle, result, and error handling,
while determining there is NO supported game-side endpoint override.

### G19 Deliverables

| Deliverable | Count |
|-------------|-------|
| Artifacts (JSON) | 11 |
| Documents | 15 |
| Analysis scripts | 11 |
| PE analysis outputs | 3 |

### G19 Key Findings

1. **Role of AcrGame.exe**: thin launcher/wrapper (CreateProcessW/ShellExecuteExW); no network protocol of its own.
2. **Startup path**: launcher -> Shipping build; Shipping reads OpenKey + master data locally before contacting any server.
3. **Contracts**: HTTP (matching/game-data/fest-result/error), TCP (matching/battle commands), NESYS pipe (card ops).
4. **Direct network protocols**: HTTP (WININET), TCP (WS2_32), local pipe. Framing = 4-byte LE length prefix + protobuf.
5. **Endpoint override**: NO_SUPPORTED_ENDPOINT_OVERRIDE_FOUND. Hardcoded `http://dev.starwing.jp/mock` (port 80); only operator hosts-file/DNS redirect works.
6. **Python-server gaps**: no endpoint confirmed against game-side contract; matching/battle/result need confirmed client request + response + state advancement.
7. **Architecture**: Option A (two-tier transport boundary + Python HTTP/TCP server), SQLite-only.
8. **91-command registry preserved**: 8 confirmed/high + 20 protocol-identified/medium + 63 unknown = 91.

### G19 Quality Gates (actual)

| Gate | Result |
|------|--------|
| Full test suite | 1056 passed, 1 skipped, 0 failed |
| Clean-room subset | 222 passed, 0 failed |
| Ruff | All checks passed (2 unused imports removed from G18 test files) |
| Mypy | 0 errors, 80 source files |
| SHA-256 integrity (6 artifacts) | All MATCH |
| No live pipe created | PASS |
| No service/registry/cert change | PASS |
| legacy-js unchanged | PASS |

### G19 Documents Created

| Document | Path |
|----------|------|
| G19 Initial Baseline | docs/PHASE_2A_G19_INITIAL_BASELINE.md |
| G19 IDA Analysis Plan | docs/PHASE_2A_G19_IDA_ANALYSIS_PLAN.md |
| G19 Final Report | docs/PHASE_2A_G19_FINAL_REPORT.md |
| Executable Module Map | docs/GAME_CLIENT_EXECUTABLE_MODULE_MAP.md |
| Startup Dependency Graph | docs/GAME_CLIENT_STARTUP_DEPENDENCY_GRAPH.md |
| Pipe Protocol | docs/GAME_SIDE_PIPE_PROTOCOL.md |
| Command Dispatch | docs/GAME_SIDE_COMMAND_DISPATCH.md |
| NESYS Min-Necessity | docs/NESYSERVICE_MINIMUM_NECESSITY_ASSESSMENT.md |
| Feature Protocol Map | docs/PRIVATE_SERVER_FEATURE_PROTOCOL_MAP.md |
| Endpoint Classification | docs/GAME_NETWORK_ENDPOINT_CLASSIFICATION.md |
| Endpoint Configuration | docs/GAME_SUPPORTED_ENDPOINT_CONFIGURATION.md |
| Python Server Gap Map | docs/PYTHON_PRIVATE_SERVER_CLIENT_GAP_MAP.md |
| Minimum Architecture | docs/PRIVATE_SERVER_MINIMUM_ARCHITECTURE.md |
| Service Requirement Matrix | docs/SERVICE_REQUIREMENT_MATRIX.md |
| Implementation Eligibility | docs/PRIVATE_SERVER_IMPLEMENTATION_ELIGIBILITY.md |

### Recommended Next Phase

Phase 2A-G20: Runtime Integration, Traffic Pattern Validation, and Private-Server Contract Enforcement

---

## Phase 2A-G20 (Private-Server HTTP Startup Contract Vertical Slice)

**Classification:** HTTP_STARTUP_PAYLOAD_EVIDENCE_INSUFFICIENT

### G20 Outcome Summary

1. **HTTP startup uses JSON, not protobuf (CONFIRMED).** Evidence: `CPP_HttpJsonSerialize.cpp`,
   `CPP_HttpJsonDifference.cpp`, `HttpGameDataLoadData`/`HttpGameDataLoadMissionData` JSON symbols,
   `http:ResponseGameDataLoad:OptionData/PlayerData/mechas success`. Protobuf field-number recovery
   does NOT apply to HTTP startup; the TCP `message.pb.cpp` is separate.
2. **Startup route payloads NOT recovered.** Only two literal URL paths exist in the binary:
   `/matching/match_id/generate` and `/option/save`. `BindHttpBoot/Version/Resource/...` encode route
   intent only, not path/method/JSON contract.
3. **Boot gating:** `ACPP_SystemDataCheck::HttpRequestWait` (`Request complete.` / `WaitTimer over.`).
4. **All 9 startup routes documented BLOCKED_EVIDENCE** (0 implementable) — no fabrication.
5. **Compatibility mode added, disabled by default:** `private_server_compatibility_mode: bool = False`.
6. **NESYS pipe decision:** PIPE_NOT_REQUIRED_FOR_HTTP_STARTUP (card-session pipe deferred).

### G20 Quality Gates (actual)

| Gate | Result |
|------|--------|
| Full test suite | 1058 passed, 1 skipped, 0 failed (baseline 1056 + 2 new config tests) |
| Clean-room subset | 222 passed, 0 failed |
| Ruff | All checks passed |
| Mypy | 0 errors |
| SHA-256 integrity (6 artifacts) | All MATCH |
| No original exe modified/launched | PASS |
| No live pipe / service / registry / cert / DNS / proxy change | PASS |
| legacy-js unchanged | PASS |

### G20 Documents Created

| Document/Artifact | Path |
|----------|------|
| G20 Final Report | docs/PHASE_2A_G20_FINAL_REPORT.md |
| HTTP Startup Contract | docs/PRIVATE_SERVER_HTTP_STARTUP_CONTRACT.md |
| Python Server Gap Map (updated) | docs/PYTHON_PRIVATE_SERVER_CLIENT_GAP_MAP.md |
| Route Confirmation Matrix | artifacts/phase_2a_g20/http_route_confirmation_matrix.json |
| HTTP Startup Contract Evidence | artifacts/phase_2a_g20/http_startup_contract_evidence.json |
| NESYS Pipe Decision | artifacts/phase_2a_g20/nesys_pipe_decision.json |

### Recommended Next Phase

Phase 2A-G21: resolve startup route URL-path/method/JSON payload via control-flow or runtime-capture
evidence (currently BLOCKED_EVIDENCE), then implement confirmed boot/version/resource routes.

---

## Phase 2A-G35 (First-Time Onboarding Blocking Matching)

**Classification:** PLAYABLE_FLOW_BLOCKED_AFTER_START

**Commit:** (TBD)

### G35 Outcome Summary

1. **INI config path reproduced (CONFIRMED).** Same evidence chain as G34:
   `FAcrNetworkConfig::Init / port[7777]`, `MatchingServer : 127.0.0.1:6666 (UseConfigMatchingServer : 1)`,
   `Decide connect type INI file address`.

2. **TCP connection attempted but never established.** DNS resolved successfully
   (`ResolvedAddr complete! / ResolvedAddr[127.0.0.1:6666]`) but TCP handshake stalled.
   No `TryToConnect` or `Success to connect` messages after DNS resolution.
   0 established TCP connections on port 6666.

3. **First-time onboarding is the blocker.** Game detected first-time launch and entered
   local-only onboarding flow: BuyCredit → WarningDisp → UserDataCheck → HowToPlay →
   UserDataInput → Immersion → Introduction → Tutorial Battle. This flow requires no network.

4. **Credit consumption:** 1 credit consumed for BuyCredit. Total debug credits: 3.
   UserId: -1 (no player identity set during onboarding).

5. **Tutorial battle runs locally.** `CurrentBattleSequence:Battle`,
   `BattleSequencePlayer:E_BattlePlayer`, `BattlePlayerId:0`, `UserId:-1`.

6. **No non-Ping frames captured.** TCP was never connected, so no game protocol frames exchanged.

### G35 Quality Gates

| Gate | Result |
|------|--------|
| Full test suite | 19 G34 tests pass |
| Ruff | OK |
| No fabricated network responses | PASS |
| No fake player identities | PASS |
| No NESYS pipe mock | PASS |

### G35 Documents Created

| Document/Artifact | Path |
|----------|------|
| G35 Final Report | docs/PHASE_2A_G35_FINAL_REPORT.md |
| Runtime Timeline | artifacts/phase_2a_g35/runtime_timeline.json |
| TCP Frames | artifacts/phase_2a_g35/tcp_frames.json |
| First Non-Ping Message | artifacts/phase_2a_g35/first_non_ping_message.json |
| Response Eligibility | artifacts/phase_2a_g35/response_eligibility.json |
| Next Blocker | artifacts/phase_2a_g35/next_blocker.json |
| Test Reconciliation | artifacts/phase_2a_g35/test_reconciliation.json |
| Safety Results | artifacts/phase_2a_g35/safety_results.json |

### Recommended Next Phase

Phase 2A-G36: Complete tutorial naturally via controller mapper, monitor TCP/save-data/relaunch state.

---

## Phase 2A-G36 (Tutorial Completed, Onboarding Passed)

**Classification:** TUTORIAL_COMPLETED_ONBOARDING_PASSED

**Commit:** TBD

### G36 Outcome Summary

1. **Full onboarding flow completed (CONFIRMED).** Game executed all 22 sequences: Boot → Notice → SeatCheck → AdvertiseMovie → SystemDataCheck → PromotionMovie → Title → SystemDataCheck → PromotionMovie → Title → SystemDataCheck → ReadCard → BuyCredit → WarningDisp → UserDataCheck → HowToPlay → UserDataInput → Immersion → Introduction → FirstTimeTutorial → Battle → LeavedBattle → TerminatedBattle → Title.

2. **TCP connection stable (CONFIRMED).** 43 pings sent, all received Pong responses. Connection maintained throughout session. `bWebServerLive[1]` confirmed.

3. **Tutorial battle completed (CONFIRMED).** Battle ended with `Result_Timeover_Lose`. 51 respawns. Game returned to Title via `TerminatedBattle`.

4. **NESYS errors non-blocking (CONFIRMED).** 46 occurrences of `Error No MatchingServer so initialize Nesys before.` Every 20 seconds on Ping cycle. Tutorial completed despite errors.

5. **No player save data (CONFIRMED).** Only master data metadata (SaveData.json, 3771 bytes). No player-specific files created.

6. **Controller mapper functional (CONFIRMED).** XInput detected, keyboard output working. Tutorial playable via keyboard inputs.

### G36 Quality Gates

| Gate | Result |
|------|--------|
| Game launch | PASS |
| INI config path | PASS (Decide connect type INI file address) |
| TCP connection | PASS (Success to connect) |
| Ping/Pong | PASS (43 pings, all Pong) |
| Onboarding flow | PASS (all 22 sequences) |
| Tutorial battle | PASS (completes with Timeover_Lose) |
| Return to Title | PASS (TerminatedBattle → Title) |
| NESYS errors | NON-BLOCKING (46 errors, tutorial completes) |
| No fabricated data | PASS |
| No NESYS pipe mock | PASS |
| No fake player identities | PASS |

### G36 Documents Created

| Document/Artifact | Path |
|----------|------|
| G36 Final Report | docs/PHASE_2A_G36_FINAL_REPORT.md |
| G36 Decision | artifacts/phase_2a_g36/g36_decision.json |
| G36 Classification | artifacts/phase_2a_g36/g36_classification.md |
| Runtime Timeline | artifacts/phase_2a_g36/runtime_timeline.json |

### Recommended Next Phase

Phase 2A-G37: Implement NESYS protocol in TCP server to handle initialization handshake, then test post-tutorial matching flow.

## Phase 2A-G38: bNesysServerLive Writer/Reader/Semantic Classification (COMPLETE)

**Status**: COMPLETE - Full IDA decompilation of LiveBits data flow
**AUDIT NOTE (G45)**: The LiveBits offset mapping in G38 used IDA decompiler's a1[N] notation which does NOT represent byte offsets. G45 corrected this via direct disassembly of OnlineGateCheck at sub_142C71510. The actual byte offsets are 0x63-0x69 (not a1[99]-a1[105]). See artifacts/phase_2a_g45/livebits_corrected_map.json.

### Key Findings

| Property | Value |
|----------|-------|
| Format function | `sub_142C71A30` (UOnlineObserverWork::Report) |
| bNesysServerLive writer | `sub_142C72730` (UOnlineObserverWork::Tick) |
| bNesysServerLive reader | `sub_142C71500`: `*(byte*)(NESYS_state + 1600) == 1` |
| Classification | `NESYS_CERTIFICATE_AUTHENTICATED_STATE` |
| Certificate dependency | YES - HTTP certificate validation required |
| Pipe dependency | NO |
| Gate expression | `a1[99] && a1[100] && a1[102] && a1[101] && a1[103] && a1[104] && a1[105]` |

### LiveBits Flags

| Flag | Offset | Writer | Trigger |
|------|--------|--------|---------|
| bWebServerLive | [99] | OnReceivePong | TCP pong received |
| bNesysServerLive | [100] | Tick | NESYS certificate authenticated |
| bNesicaReception | [101] | SetLiveFromGame | Game live state change |
| bLiveFromTestmode | [102] | Unknown | Test mode state |
| bLiveFromGame | [103] | SetLiveFromGame | Game live state change |
| bGameConnect | [104] | Unknown | TCP connection established |
| bHttpSuccess | [105] | SetHttpSuccess | HTTP request completion |

### Artifacts

| Artifact | Path |
|----------|------|
| LiveBits xrefs | artifacts/phase_2a_g38/livebits_xrefs.json |
| Data flow | artifacts/phase_2a_g38/nesys_live_dataflow.json |
| Write map | artifacts/phase_2a_g38/livebits_write_map.json |
| Gate expression | artifacts/phase_2a_g38/playable_gate_expression.json |
| Final report | docs/PHASE_2A_G38_FINAL_REPORT.md |

## Phase 2A G39: Local Profile and Offline Session (COMPLETE)

**Commit**: TBD
**Classification**: `LOCAL_PROFILE_IMPLEMENTED`
**Status**: COMPLETE - All deliverables implemented

### Summary
Local profile system implemented with SQLite persistence, CRUD API endpoints, card-style PyQt5 GUI, server status dashboard, and tutorial progress tracking.

### Tutorial Persistence Root Cause
- Game queries `POST /tutorial/*` and `POST /game_data/save` for tutorial completion state
- Server returned HTTP 501 (not implemented)
- `$IsTutorialProgress` stays 0 on every relaunch
- UserId = -1 (no authenticated player, free play mode)
- Tutorial battle times out by design (~590s, Result_Timeover_Lose)

### Deliverables

| Component | Status |
|-----------|--------|
| Database schema | 13-field `local_profile` table |
| Migration | `002_local_profile` |
| API endpoints | 7 routes under `/profile/local/` |
| Profile GUI | Card-style PyQt5 (`tools/profile_manager/app.py`) |
| Status dashboard | Real-time monitoring (`tools/profile_manager/dashboard.py`) |
| Tests | 11 passing tests |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profile/local/create` | POST | Create a new local profile |
| `/profile/local/list` | POST | List all local profiles |
| `/profile/local/select` | POST | Select a profile and start session |
| `/profile/local/end` | POST | End the current session |
| `/profile/local/update` | POST | Update profile fields |
| `/profile/local/delete` | POST | Delete a profile |
| `/profile/local/tutorial/record` | POST | Record a tutorial attempt |

### Security Boundaries
- No NESYS/NESICA identity fabrication
- No game binary modification
- No forced `bNesysServerLive` or `IsOnline`
- Profile labeled as "Local Profile" / "Private Profile"
- No external interfaces exposed
- All tools bind to loopback only

### Artifacts

| Artifact | Path |
|----------|------|
| Decision JSON | artifacts/phase_2a_g39/g39_decision.json |
| Classification | artifacts/phase_2a_g39/g39_classification.md |
| Profile schema | artifacts/phase_2a_g39/profile_schema.json |
| Tutorial result | artifacts/phase_2a_g39/tutorial_persistence_result.json |
| Security boundary | artifacts/phase_2a_g39/security_boundary.json |
| Test reconciliation | artifacts/phase_2a_g39/test_reconciliation.json |
| Final report | docs/PHASE_2A_G39_FINAL_REPORT.md |
| Boundary doc | docs/G39_LOCAL_PROFILE_BOUNDARY.md |

## Phase 2A-G40: NESYS Offline Block Investigation (COMPLETE)

**Status**: COMPLETE
**Classification**: NESYS_CARD_EVENT_REQUIRED

## Phase 2A-G41: Controller Mapper and Tutorial Flow (COMPLETE)

**Status**: COMPLETE
**Classification**: CONTROLLER_MAPPER_FUNCTIONAL

## Phase 2A-G42: Public Implementation Correlation (COMPLETE)

**Status**: COMPLETE
**Classification**: PUBLIC_REFERENCE_CORRELATED

## Phase 2A-G43: Local Player Profile Handler (COMPLETE)

**Commit**: f3a6d46
**Status**: COMPLETE
**Classification**: LOCAL_PLAYER_PROFILE_IMPLEMENTED

## Phase 2A-G44: Live Card-Profile Validation (COMPLETE)

**Commit**: 326c685
**Status**: COMPLETE
**Classification**: NESYS_CARD_EVENT_REQUIRED

### G44 Key Findings

| Metric | Value |
|--------|-------|
| /matching/server | WORKING (game accepted response) |
| TCP ping/pong | WORKING (127.0.0.1:6666) |
| /player/profile/load | IMPLEMENTED but NEVER CALLED |
| Game stuck at | Title → InsertStart animation loop |
| Seven-flag gate | 5/7 true, bNesysServerLive[0] and bNesicaReception[0] block |

## Phase 2A-G45: Onboarding State Reconciliation (COMPLETE)

**Status**: COMPLETE
**Classification**: ONBOARDING_NOT_PERSISTED

### G45 Key Findings

| Finding | Detail |
|---------|--------|
| LiveBits contradiction | RESOLVED - SetLiveFromGame is a string literal, not a function name |
| Seven-flag offsets | CONFIRMED as byte offsets 0x63-0x69 in struct |
| Gate check order | NON-SEQUENTIAL: 63, 64, 66, 65, 67, 68, 69 |
| Onboarding persistence | NOT_PERSISTED - no save file, no DB record, no local config |
| $IsTutorialProgress | Server-authoritative (defaults to 0) |
| bNesicaReception | COUPLED to certificate trust |
| /player/profile/load trigger | REQUIRES NESYS card event (ReadCard flow) |
| Local Card event eligibility | NOT_ELIGIBLE (requires NESYS cert trust) |
| Reversible test design | NO_SAFE_ONBOARDING_STATE_TEST_AVAILABLE |
| Test assertions | 7 modified (all strengthened, evidence-based) |

### G45 Quality Gates

| Gate | Result |
|------|--------|
| Full test suite | 1115 passed, 1 skipped, 0 failed |
| Mypy | 0 errors (85 source files) |
| Ruff | 0 errors |
| IDA analysis | Read-only, no modifications |
| Safety constraints | ALL SATISFIED |

### G45 Documents

| Document | Path |
|----------|------|
| G45 Final Report | docs/PHASE_2A_G45_FINAL_REPORT.md |
| LiveBits Corrected Map | artifacts/phase_2a_g45/livebits_corrected_map.json |
| Save State Manifest | artifacts/phase_2a_g45/save_state_manifest.json |
| Onboarding Branch | artifacts/phase_2a_g45/onboarding_branch.json |
| NESICA Reception Dataflow | artifacts/phase_2a_g45/nesica_reception_dataflow.json |
| Profile Request Trigger | artifacts/phase_2a_g45/profile_request_trigger.json |
| Reversible Test Design | artifacts/phase_2a_g45/reversible_test_design.json |
| Implementation Eligibility | artifacts/phase_2a_g45/implementation_eligibility.json |
| Test Reconciliation | artifacts/phase_2a_g45/test_reconciliation.json |
| Safety Results | artifacts/phase_2a_g45/safety_results.json |

## Phase 2A-G46: Local Offline Launcher (COMPLETE)

**Status**: COMPLETE
**Classification**: OFFLINE_LAUNCHER

### G46 Key Findings

| Finding | Detail |
|---------|--------|
| Launcher type | PyQt5 GUI application |
| Environment checks | 12 checks (D drive, OpenKey, config, ports, Python, etc.) |
| Process management | OwnedProcess tracking with emergency stop |
| Session logging | JSONL event logging with summary export |
| Startup order | Strict 8-step sequence |
| Security boundaries | No NESiCA terminology, no vendor card claims, no online mode claims |
| Test coverage | 33 launcher tests, 125 server tests |
| Quality gates | Mypy clean, Ruff clean |

### G46 Quality Gates

| Gate | Result |
|------|--------|
| Launcher tests | 33 passed, 0 failed |
| Server tests | 125 passed, 0 failed |
| Mypy | 0 errors (6 source files) |
| Ruff | 0 errors |
| Safety constraints | ALL SATISFIED |

### G46 Documents

| Document | Path |
|----------|------|
| G46 Final Report | docs/PHASE_2A_G46_FINAL_REPORT.md |
| Local Launcher Guide | docs/G46_LOCAL_LAUNCHER_GUIDE.md |
| Environment Checks | artifacts/phase_2a_g46/g46_environment_checks.json |
| Process Manager | artifacts/phase_2a_g46/g46_process_manager.json |
| Status Tracking | artifacts/phase_2a_g46/g46_status_tracking.json |
| Session Logging | artifacts/phase_2a_g46/g46_session_logging.json |
| Test Results | artifacts/phase_2a_g46/g46_test_results.json |

