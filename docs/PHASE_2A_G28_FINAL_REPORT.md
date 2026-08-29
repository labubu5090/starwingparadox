# Phase 2A-G28 Final Report

**Date:** 2026-08-29  
**Classification:** OPENKEY_GATE_PASSED_CHECKVERSION_PASSED  
**Commit:** PENDING

## Executive Summary

G28 deployed the operator-owned OpenKey.json to the exact path expected by the game (`D:/Saved/ACRSaved/SaveData/OpenKey.json`). The game loaded and accepted the file. SystemDataCheck advanced past State 2 (CheckOpenKeyLoad) to State 4 (CheckVersion), which also passed. SystemDataCheck completed successfully with `isError[0]`.

## Key Findings

### 1. OpenKey.json Deployment

- **Original state:** FILE_ABSENT (D: drive did not exist)
- **Solution:** Created D: drive via `subst D: X:\StarwingParadox\D DRIVE CONTENTS`
- **File already present** at the correct path after subst
- **Content:** `{IsOpen: 1, OpenVersion: 56299, OpenDate: "2018/11/21", OpenTime: "08:00:00"}`

### 2. Runtime Evidence

```
UFileManagerTickable::LoadJsonFile / path[D:/Saved/ACRSaved/SaveData/OpenKey.json]
ACPP_SystemDataCheck::SetNextMode[CheckOpenKeyLoad](2)
ACPP_SystemDataCheck::Tick / CheckOpenKeyLoad / IsOpen[1].
ACPP_SystemDataCheck::SetNextMode[CheckVersion](4)
ACPP_SystemDataCheck::Tick / CheckVersion / IsOnlineStatus[0] CheckPackage[1] CheckMasterData[1]
ACPP_SystemDataCheck::SetNextMode[End](20)
ACPP_SystemDataCheck::SetNextMode(PromotionMovie) / isError[0]
```

### 3. State Machine Progress

| State | G27 (no OpenKey) | G28 (with OpenKey) |
|-------|------------------|---------------------|
| 0: EventRequest | IsOnline=0, proceeds | IsOnline=0, proceeds |
| 2: CheckOpenKeyLoad | LoadKeyFile error | IsOpen[1] accepted |
| 3: CheckOpenKeyUpdate | NESYS Event error | SKIPPED (went to 4) |
| 4: CheckVersion | NOT REACHED | IsOnlineStatus[0] CheckPackage[1] CheckMasterData[1] |
| 19: DispError | Error shown | NOT REACHED |
| 20: End | isError[1] → Title | isError[0] → PromotionMovie |

### 4. SystemDataCheck Completed Successfully

- **isError[0]** - No error
- **Next sequence:** PromotionMovie (not Title with error)
- **OpenKey gate:** PASSED
- **CheckVersion gate:** PASSED

### 5. Z Input Limitation

Z input could not be tested because the game window could not be brought to foreground from OpenCode's PowerShell process. This is an automation limitation, not a game contract issue.

## Classification

**OPENKEY_GATE_PASSED_CHECKVERSION_PASSED**

## G29 Recommendation

The next phase should:
1. Test Z, Z, Enter sequence with operator manually pressing keys
2. Or investigate the POST-boot loop behavior
3. Or implement the matching server mock (http://dev.starwing.jp/mock/matching/server)

## Protected Hashes

All protected files verified.

## Quality Gates

- Pytest: 1058 passed, 1 skipped
- Ruff: All checks passed
