# G26 Post-Start UI State

**Phase:** 2A-G26  
**Date:** 2026-08-29  
**Status:** BLOCKED

## Summary

After pressing Enter with 2 credits, the game advanced from Title to SystemDataCheck. The SystemDataCheck failed because NESYS is offline and OpenKey.json is missing. The game returned to Title.

## Sequence

```
Title (with 2 credits)
  → Enter pressed
    → SystemDataCheck
      → CheckOpenKeyLoad
        → OpenKey.json not found
      → CheckOpenKeyUpdate
        → NESYS Event error (IsOnline[0])
        → Error message displayed
      → Return to Title
```

## Blocking Errors

1. **OpenKey.json not found**
   - Path: `D:/Saved/ACRSaved/SaveData/OpenKey.json`
   - Error: `LoadKeyFile error`

2. **NESYS offline**
   - `UCPP_NesysControl::Get(this)->IsOnline[0]`
   - Error: `NESYS Event error. IsEventCheck[0] IsEventError[0]`

3. **Error message**
   - Japanese: `システムオフラインのためチェックが出来ません。オフラインになるまでお待ちください。`
   - Translation: "System is offline, cannot check. Please wait until offline."

## Classification

**SYSTEMDATACHECK_NESYS_OFFLINE_BLOCKED**

## Implication

The SystemDataCheck is the new blocking boundary after valid credit insertion. A private server must either:
1. Provide a valid OpenKey.json
2. Bypass the NESYS online check
3. Implement the SystemDataCheck protocol

---

**See also:** `G26_DOWNSTREAM_FEATURE_REASSESSMENT.md`
