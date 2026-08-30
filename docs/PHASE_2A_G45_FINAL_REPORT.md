# G45 Final Report: Onboarding State Reconciliation

**Date**: 2026-08-30  
**Classification**: ONBOARDING_NOT_PERSISTED  
**Commit**: Pending (G45)  
**Predecessor**: G44 (326c685)

---

## Executive Summary

G45 resolved the onboarding state question and the LiveBits contradiction through IDA binary analysis, filesystem inventory, and database inspection. **Onboarding state is NOT persisted anywhere** - not in save files, not in the database, not in local config. The game determines onboarding flow at runtime based on the IsOnline flag and NESYS card events.

## Primary Objectives Completed

### 1. LiveBits Contradiction Resolution

**Previous claim**: SetLiveFromGame at sub_142C71F30 writes both a1[101] (bNesicaReception) and a1[103] (bLiveFromGame) with the same parameter.

**Actual finding**: 
- `sub_142C71F30` does not exist in the binary
- `SetLiveFromGame` is a **string literal** at `0x1479d6af8`, not a function name
- The function `sub_142D102C0` (the OnlineGateCheck function itself) contains this string as a log label
- Five getter functions read from separate global RPC singletons:
  - `sub_142D554B0` → "Get" (qword_14924BCD8)
  - `sub_142D557E0` → "IsOnline" (qword_14924BCE0)
  - `sub_142D55A50` → "OnReceiveMatchingServer" (qword_14924BCE8)
  - `sub_142D55DC0` → "OnReceivePong" (qword_14924BCF0)
  - `sub_142D55FF0` → "SetLiveFromGame" (qword_14924BCF8)

**Root cause**: IDA decompiler's `a1[N]` notation uses element indexing based on recovered pointer type, not byte offsets. `a1[101]` does not mean byte offset 101.

### 2. Corrected Seven-Flag Mapping

OnlineGateCheck at `sub_142C71510` reads 7 **byte** flags at offsets:
```
+0x63 (99)  → checked 1st → bWebServerLive (runtime=1)
+0x64 (100) → checked 2nd → bNesysServerLive (runtime=0)
+0x66 (102) → checked 3rd → bLiveFromTestmode (runtime=1)
+0x65 (101) → checked 4th → bNesicaReception (runtime=0)
+0x67 (103) → checked 5th → bLiveFromGame (runtime=1)
+0x68 (104) → checked 6th → bGameConnect (runtime=1)
+0x69 (105) → checked 7th → bHttpSuccess (runtime=1)
```

Gate check order is **non-sequential**: 63, 64, 66, 65, 67, 68, 69 (compiler reordered branches).

### 3. Onboarding State Conclusion

**Classification**: ONBOARDING_NOT_PERSISTED

Evidence chain:
1. No player-specific save file exists anywhere on the filesystem
2. `player_progress` table has zero rows
3. `SaveData.json` contains only master data metadata
4. Local Profile 413 has `tutorial_completed=0`
5. `$IsTutorialProgress` is server-authoritative (defaults to 0)
6. TutorialProgress string has 0 code xrefs in binary

### 4. bNesicaReception Meaning

bNesicaReception is a log-category label for the "OnReceiveMatchingServer" RPC event. It indicates whether the matching server response was successfully received and parsed. It is **NOT** directly related to NESICA card insertion.

**Certificate dependency**: bNesicaReception is COUPLED to certificate trust - it cannot be set without valid NESYS authentication.

### 5. /player/profile/load Trigger Status

**Trigger chain**: NESYS card inserted → NESYS pipe authenticates → bNesicaReception=1 → ReadCard flow → game calls /player/profile/load

**Current blocker**: Without NESYS cert trust, bNesicaReception cannot be set, so ReadCard never initiates.

### 6. Local Card Event Eligibility

**Eligible**: NO  
**Reason**: Requires NESYS card reader hardware or NESYS pipe emulation. Neither available within safety constraints.

### 7. Reversible Test Design Status

**Status**: NO_SAFE_ONBOARDING_STATE_TEST_AVAILABLE  
**Reason**: Onboarding state is runtime-only (not persisted). The only way to test is via NESYS card event, which requires certificate trust.

## Test Changes

7 test assertions modified in 2 files:
- `tests/api/test_player.py`: 2 assertions updated (result → player_id/nesys_id)
- `tests/legacy_regression/test_player_profile_fields.py`: 5 assertions updated (absent → present field checks)

All changes justified by G43 handler implementation. No coverage weakened.

## Quality Gates

- **Tests**: 1115 passed, 1 skipped, 0 failed
- **Mypy**: Clean (85 files)
- **Ruff**: Clean
- **IDA analysis**: Read-only, no modifications

## Artifacts

1. `artifacts/phase_2a_g45/livebits_corrected_map.json`
2. `artifacts/phase_2a_g45/save_state_manifest.json`
3. `artifacts/phase_2a_g45/onboarding_branch.json`
4. `artifacts/phase_2a_g45/nesica_reception_dataflow.json`
5. `artifacts/phase_2a_g45/profile_request_trigger.json`
6. `artifacts/phase_2a_g45/reversible_test_design.json`
7. `artifacts/phase_2a_g45/implementation_eligibility.json`
8. `artifacts/phase_2a_g45/test_reconciliation.json`
9. `artifacts/phase_2a_g45/safety_results.json`
