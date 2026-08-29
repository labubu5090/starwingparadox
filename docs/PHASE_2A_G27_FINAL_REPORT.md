# Phase 2A-G27 Final Report

**Date:** 2026-08-29  
**Classification:** OPENKEY_CONFIGURATION_HARD_GATE_CONFIRMED  
**Commit:** PENDING

## Executive Summary

G27 recovered the complete SystemDataCheck dependency graph. The primary blocker is a missing OpenKey.json file at `D:/Saved/ACRSaved/SaveData/OpenKey.json`. The file exists in the operator's backup at `X:\StarwingParadox\D DRIVE CONTENTS\Saved\ACRSaved\SaveData\OpenKey.json` and contains simple public configuration fields with no trust dependency.

## Key Findings

### 1. SystemDataCheck State Machine

```
State 0: EventRequest → checks IsOnline[0] → proceeds
State 2: CheckOpenKeyLoad → loads OpenKey.json → LoadKeyFile error
State 3: CheckOpenKeyUpdate → NESYS Event error → DispError
State 19: DispError → displays error, waits ~10 seconds
State 20: End → returns to Title
```

### 2. Primary Blocker

**OpenKey.json not found** at `D:/Saved/ACRSaved/SaveData/OpenKey.json`

### 3. OpenKey.json Content

```json
{
  "IsOpen": 1,
  "OpenVersion": 56299,
  "OpenDate": "2018/11/21",
  "OpenTime": "08:00:00"
}
```

### 4. OpenKey Security Classification

- `IsOpen`: PUBLIC_CONFIGURATION (safe)
- `OpenVersion`: SOFTWARE_VERSION (safe)
- `OpenDate`: LOCAL_CONFIGURATION (safe)
- `OpenTime`: LOCAL_CONFIGURATION (safe)

### 5. Blocking Chain (Updated)

```
Title → Z (2 credits) → Enter → SystemDataCheck
  → EventRequest (IsOnline=0, proceeds)
  → CheckOpenKeyLoad (file not found)
  → CheckOpenKeyUpdate (NESYS Event error)
  → DispError
  → End → Title
```

### 6. Private Server Credit Decision

**NO_SERVER_CREDIT_COMPONENT_REQUIRED** (confirmed from G26)

### 7. Implementation Eligibility

| Component | Eligible | Reason |
|-----------|----------|--------|
| OpenKey.json | YES | Simple local configuration |
| NESYS Event Check | NO | Requires investigation |
| HTTP Matching Server | NO | Contract incomplete |

## G28 Recommendation

**PRIVATE_OPENKEY_CONFIGURATION_FOUNDATION**

Create OpenKey.json at the expected path and test if SystemDataCheck advances.

## Protected Hashes

All protected files verified:
- AcrGame-Win64-Shipping.exe: `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4`
- GALAXYIO.dll: `47B4E1EDD13A7F94C74FF512C2CA705B0D9EEAF9C0355673452091BD882B9C92`

## Quality Gates

- Pytest: 1058 passed, 1 skipped
- Ruff: All checks passed

## Artifacts

- 15 JSON artifacts in `artifacts/phase_2a_g27/`
- 5+ documents in `docs/`

## Conclusion

The SystemDataCheck blocker is a simple missing configuration file. No trust dependency for OpenKey.json. A private server can provide this file independently.

---

**Next:** G28 - Private OpenKey Configuration Foundation
