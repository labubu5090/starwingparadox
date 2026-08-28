# OpenKey Reference Map

**Date:** 2026-08-28

## Summary

| Category | Count |
|----------|-------|
| EXPLICIT_READ | 1 |
| PATH_STRING_ONLY | 3 |
| LOG_REFERENCE | 6 |
| CONFIG_REFERENCE | 2 |
| DOCUMENTATION_REFERENCE | 14 |
| UNKNOWN | 0 |
| **Total** | **26** |

## Reference Inventory

### 1. Game Binary (EXPLICIT_READ)

| Source | Path | Component | Intent | Stage | Error |
|--------|------|-----------|--------|-------|-------|
| AcrGame-Win64-Shipping.exe | D:/Saved/ACRSaved/SaveData/OpenKey.json | Game runtime | LoadJsonFile (read) | Boot/SystemDataCheck | LoadKeyFile error |

**Evidence:** Game log line 8448, 108153. Game calls `UFileManagerTickable::LoadJsonFile` with this path. Result: file not found.

### 2. D DRIVE CONTENTS (PATH_STRING_ONLY)

| Source | Path | Component | Intent | Stage |
|--------|------|-----------|--------|-------|
| D DRIVE CONTENTS\Saved\ACRSaved\SaveData\OpenKey.json | D:\Saved\ACRSaved\SaveData\OpenKey.json | Game data | File exists (96 bytes) | Runtime provision |

**Evidence:** File exists in authorized game content. SHA-256: `B166054FD8CFAC828A9BF72F97663A311F7C5B9A4A23AEE3189B959241D64AE2`

### 3. D Drive Populate Script (PATH_STRING_ONLY)

| Source | Path | Component | Intent | Stage |
|--------|------|-----------|--------|-------|
| tools/game/d-drive/populate-starwing-test-vhd.ps1 | D:\Saved\ACRSaved\SaveData\OpenKey.json | Deployment | Copy to VHD | D: drive setup |

**Evidence:** Script copies OpenKey.json to D: drive during VHD population.

### 4. D Drive Verify Script (PATH_STRING_ONLY)

| Source | Path | Component | Intent | Stage |
|--------|------|-----------|--------|-------|
| tools/game/d-drive/verify-starwing-test-vhd.ps1 | D:\Saved\ACRSaved\SaveData\OpenKey.json | Verification | Check exists | D: drive validation |

**Evidence:** Script verifies OpenKey.json exists on D: drive.

### 5. Game Log Events (LOG_REFERENCE)

| Line | Timestamp | Event | Result |
|------|-----------|-------|--------|
| 8448 | 02:34.32 | LoadJsonFile (boot) | File not found |
| 108145 | 02:36.41 | SetNextMode[CheckOpenKeyLoad] | Entry |
| 108153 | 02:36.41 | LoadJsonFile (SystemDataCheck) | File not found |
| 108154 | 02:36.41 | SetNextMode[CheckOpenKeyUpdate] | Entry |
| 108155 | 02:36.41 | CheckOpenKey / LoadKeyFile error | FAIL |
| 108156 | 02:36.41 | CheckOpenKeyUpdate / NESYS Event error | FAIL |

### 6. Configuration References (CONFIG_REFERENCE)

| Source | Path | Content |
|--------|------|---------|
| GAME_CONFIGURATION_MAP.md | OpenKey.json | `{"IsOpen":1,"OpenVersion":56299,"OpenDate":"2018/11/21","OpenTime":"08:00:00"}` |
| NESYS_SERVICE_STARTUP_REQUIREMENTS.md | D:\Saved\ACRSaved\SaveData\OpenKey.json | Hardcoded path in binary |

### 7. Documentation References (DOCUMENTATION_REFERENCE)

| Document | Lines | Claim |
|----------|-------|-------|
| D_DRIVE_EXACT_LAYOUT_MAP.md | 9,30,47,58 | File exists, game writes it |
| D_DRIVE_SENSITIVE_FILE_POLICY.md | 7,8,49,54 | Content never committed |
| G9_POST_HTTP_GATING_ANALYSIS.md | 12,28,48,50,56,74,79,95 | Missing causes error |
| GAME_CONFIGURATION_MAP.md | 17,18,74,82 | File structure |
| GAME_CONTENT_FILE_INVENTORY.md | 51,52 | File listed |
| NESYS_RUNTIME_FILE_REQUIREMENTS.md | 7,16,23,25,27,32,46 | Required for auth |
| NESYS_SERVICE_STARTUP_REQUIREMENTS.md | 77 | Hardcoded path |
| PHASE_2A_G4_FINAL_REPORT.md | 86,94,104,139,246,258 | Load failed |
| PHASE_2A_G5R_FINAL_REPORT.md | 145,160 | File listed |
| PHASE_2A_G6_FINAL_REPORT.md | 23 | File present |
| STARWING_BOOT_DEPENDENCY_GRAPH.md | 54,85,98,102,108,115 | Missing causes error |
| TCP_RUNTIME_DIFFERENTIAL_ANALYSIS.md | 19,89,252,260,273 | Missing gates TCP |

## Read vs Write Classification

| Component | Read | Write | Create | Unknown |
|-----------|------|-------|--------|---------|
| AcrGame-Win64-Shipping.exe | ✓ | — | — | — |
| NesysService.exe | — | — | — | ✓ |
| D DRIVE CONTENTS | ✓ (static) | — | — | — |
| populate-starwing-test-vhd.ps1 | — | — | ✓ (copy) | — |
| verify-starwing-test-vhd.ps1 | ✓ (check) | — | — | — |

## Evidence Strength

| Classification | Strength |
|----------------|----------|
| EXPLICIT_READ (game binary) | STRONG — confirmed by game log |
| PATH_STRING_ONLY (D DRIVE) | STRONG — file exists |
| LOG_REFERENCE (game log) | STRONG — direct runtime evidence |
| CONFIG_REFERENCE | MODERATE — from documentation |
| DOCUMENTATION_REFERENCE | MODERATE — from prior analysis |
