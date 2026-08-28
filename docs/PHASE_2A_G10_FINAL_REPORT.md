# Phase 2A-G10 Final Report

**Date:** 2026-08-28
**Status:** COMPLETE

## Executive Summary

Phase 2A-G10 audited the provenance, lifecycle, and causality of OpenKey.json in the Starwing Paradox startup flow. The audit operated in DUMP-ONLY FILE-WRITING MODE — no OpenKey data was created, modified, or fabricated.

## Key Findings

### 1. OpenKey File Exists in Authorized Game Content

| File | Location | Size | SHA-256 |
|------|----------|------|---------|
| OpenKey.json | D DRIVE CONTENTS\Saved\ACRSaved\SaveData\ | 96 bytes | B166054F... |
| OpenKeyEvent_Galaxy.json | D DRIVE CONTENTS\system\DUA\event\ | 80 bytes | 65E45AF8... |

**Classification:** OPERATOR_OWNED_RUNTIME_SOURCE

### 2. OpenKey Producer is UNKNOWN

| Candidate | Evidence | Verdict |
|-----------|----------|---------|
| NesysService.exe | Binary contains file ops but no OpenKey-specific creation | NOT_PROVEN |
| AcrGame-Win64-Shipping.exe | Game reads OpenKey, doesn't create it | READ_ONLY |
| External provisioning | Unknown origin of D DRIVE CONTENTS | UNKNOWN |

**Classification:** PRODUCER_UNKNOWN

### 3. OpenKey is Read by Game, Not Written

| Component | Behavior | Evidence |
|-----------|----------|----------|
| AcrGame-Win64-Shipping.exe | EXPLICIT_READ | Game log LoadJsonFile |
| NesysService.exe | UNKNOWN | Exits before access |
| populate-starwing-test-vhd.ps1 | EXPLICIT_CREATE (copy) | Script evidence |

**Classification:** READ_BY_GAME_ONLY_WITH_UNKNOWN_PRODUCER

### 4. SystemDataCheck Has Multiple Requirements

| Requirement | G9-A Result | Classification |
|-------------|-------------|----------------|
| NESYS IsOnline | FAIL (IsOnline[0]) | REQUIRED |
| OpenKey.json | FAIL (LoadKeyFile error) | REQUIRED |
| NESYS Event | FAIL (IsEventCheck[0]) | REQUIRED |

**Classification:** MULTIPLE_SYSTEMDATA_REQUIREMENTS

### 5. NesysService Exits Before OpenKey Access

| Stage | Status |
|-------|--------|
| Process creation | COMPLETED |
| Binary initialization | COMPLETED |
| Registry check | NOT_REACHED |
| HTTP init | NOT_REACHED |
| Certificate check | NOT_REACHED |
| OpenKey read | NOT_REACHED |
| OpenKey create | NOT_REACHED |
| Named pipe create | NOT_REACHED |
| Ready state | NOT_REACHED |

**Classification:** NESYSSERVICE_EXITS_BEFORE_OPENKEY_ACCESS

### 6. Original Provisioning Context is Missing

| Component | Status | Impact |
|-----------|--------|--------|
| Launcher process | MISSING | NesysService cannot start |
| NESYS certificates | MISSING | Authentication fails |
| Registry keys | MISSING | Configuration missing |
| Network access | UNKNOWN | External services unreachable |
| OpenKey.json (runtime) | MISSING_AT_EXPECTED_PATH | SystemDataCheck fails |

**Classification:** ORIGINAL_PROVISIONING_CONTEXT_MISSING

## Corrected Claims

| Previous Claim | Corrected Classification |
|----------------|-------------------------|
| "NesysService generates OpenKey.json" | NOT_PROVEN |
| "Missing OpenKey is confirmed root cause" | OVERSTATED |
| "OpenKey is a certificate" | INCORRECT |
| "OpenKey alone makes NESYS online" | OVERSTATED |
| "OpenKey can be reconstructed" | UNSAFE |

## Documentation Created

| Document | Purpose |
|----------|---------|
| docs/PHASE_2A_G10_INITIAL_BASELINE.md | G9 baseline verification |
| docs/OPENKEY_CLAIM_CORRECTION.md | Corrected claims |
| docs/OPENKEY_REFERENCE_MAP.md | All OpenKey references |
| docs/generated/openkey_file_inventory.json | File inventory |
| docs/OPENKEY_LIFECYCLE_ANALYSIS.md | Read/write behavior |
| docs/OPENKEY_SYSTEMDATACHECK_CAUSALITY.md | Causality analysis |
| docs/ORIGINAL_CABINET_PROVISIONING_FLOW.md | Provisioning flow |
| docs/NESYS_OPENKEY_INITIALIZATION_ORDER.md | Exit relationship |

## Documents Updated

| Document | Change |
|----------|--------|
| PROGRESS.md | Added G10 section |
| docs/STARWING_BOOT_DEPENDENCY_GRAPH.md | Added correction note |
| docs/G9_POST_HTTP_GATING_ANALYSIS.md | Added correction note |

## Quality Gates

| Gate | Result |
|------|--------|
| Tests | 834 passed, 1 skipped, 0 failed ✓ |
| Ruff | 0 errors ✓ |
| Mypy | 0 errors ✓ |
| OpenKey leakage | None ✓ |
| Sensitive material committed | None ✓ |
| Game files modified | None ✓ |
| D: mapping | None ✓ |
| Matching guarded | Yes ✓ |
| Battle guarded | Yes ✓ |

## Final Status

**Classification:** `NESYS_OFFLINE_PRIMARY_GATE`

OpenKey.json exists in authorized game content but:
1. Producer is UNKNOWN (not proven to be NesysService)
2. SystemDataCheck has MULTIPLE requirements (not just OpenKey)
3. NesysService exits BEFORE OpenKey access
4. Original provisioning context is MISSING

The primary blocker remains NESYS offline (NesysService exit code -1). OpenKey is one of multiple SystemDataCheck requirements, not the sole gate.

## Recommendation

`INVESTIGATE_NESYSSERVICE_LAUNCH_CONTEXT`

To proceed, determine:
1. What launcher/context NesysService.exe expects
2. What command-line arguments it requires
3. What registry keys it reads
4. What certificates it needs

Do NOT generate, fabricate, or reconstruct OpenKey data.
