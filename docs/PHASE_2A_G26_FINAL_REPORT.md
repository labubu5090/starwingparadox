# Phase 2A-G26 Final Report

**Date:** 2026-08-29  
**Classification:** LOCAL_COIN_INPUT_CONFIRMED  
**Commit:** PENDING

## Executive Summary

G26 proved that the keyboard Z key inserts local arcade credits. Each Z press adds exactly one debug credit. After 2 Z presses, the game accepts Start and advances to SystemDataCheck. The SystemDataCheck fails because NESYS is offline and OpenKey.json is missing.

## Key Findings

### 1. Z Key Works

- **ZPressed**: `ACPP_DebugActor::ZPressed`
- **Credit type**: Debug (not production)
- **NesysService involvement**: NONE
- **GALAXYIO involvement**: NONE
- **Classification**: LOCAL_DEBUG_CREDIT_INPUT

### 2. Credit Threshold Met

- **Required**: 2 credits (StartCredit=2)
- **After 2 Z presses**: OnChangeCreditCount:2,0,0,2
- **Start accepted**: Yes

### 3. SystemDataCheck Blocked

- **OpenKey.json**: Not found
- **NESYS**: Offline (IsOnline[0])
- **Error message**: "System is offline, cannot check"
- **Return to**: Title screen

## Corrected G25 Interpretation

**Original G25 classification**: `CREDIT_SYSTEM_BLOCKED`  
**Corrected**: `TITLE_START_BLOCKED_BY_ZERO_CREDITS_IN_G25`

G25 did not press Z, so credits were zero. Z is the normal cabinet input.

## Blocking Chain (Updated)

```
Title Screen
  → Z key (2 credits)
    → Enter
      → SystemDataCheck
        → OpenKey.json (missing)
        → NESYS (offline)
          → ERROR → Title
```

## Private Server Credit Decision

**NO_SERVER_CREDIT_COMPONENT_REQUIRED**

Z supplies local credits entirely in local game state.

## Downstream Feature Reassessment

| Feature | G25 Classification | G26 Classification |
|---------|-------------------|-------------------|
| Player Session | BLOCKED | SYSTEMDATACHECK_BLOCKED |
| Matching | BLOCKED | SYSTEMDATACHECK_BLOCKED |
| Battle | BLOCKED | SYSTEMDATACHECK_BLOCKED |
| Result | BLOCKED | SYSTEMDATACHECK_BLOCKED |

## G27 Recommendation

**SYSTEMDATACHECK_BYPASS_ANALYSIS**

Analyze SystemDataCheck code to understand:
1. OpenKey.json format and content
2. NESYS IsOnline check bypass
3. SystemDataCheck → next sequence path

## Protected Hashes

All protected files verified:
- AcrGame-Win64-Shipping.exe: `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4`
- GALAXYIO.dll: `47B4E1EDD13A7F94C74FF512C2CA705B0D9EEAF9C0355673452091BD882B9C92`

## Quality Gates

- Pytest: 1058 passed, 1 skipped
- Ruff: All checks passed
- Mypy: 1 pre-existing error

## Artifacts

- 18 JSON artifacts in `artifacts/phase_2a_g26/`
- 3+ documents in `docs/`
- Audit correction for G25 zero-credit interpretation

## Conclusion

The credit system is NOT a production trust dependency. Z works locally. The new blocking boundary is SystemDataCheck (NESYS offline + OpenKey.json missing).

---

**Next:** G27 - SystemDataCheck Bypass Analysis
