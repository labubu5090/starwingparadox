# G26 Local Coin Input Observation

**Phase:** 2A-G26  
**Date:** 2026-08-29  
**Status:** CONFIRMED

## Summary

The keyboard Z key inserts local arcade credits. Each Z press adds exactly one debug credit. The game requires 2 credits to start.

## Evidence

### First Z Press (09:50:23.525)

```
ACPP_DebugActor::ZPressed
UAdvertiseSequenceWork::OnChangeCreditCount:1,0,0,1
UTestModeWork::OnAddDebugCredit / all[1] debug[1]
UMachineDataWork::AddDebugCredit / success / _credit[1] kind[AddCreditKindMaxGame]
```

### Second Z Press (09:50:24.140)

```
ACPP_DebugActor::ZPressed
UAdvertiseSequenceWork::OnChangeCreditCount:2,0,0,2
UTestModeWork::OnAddDebugCredit / all[1] debug[1]
UMachineDataWork::AddDebugCredit / success / _credit[1] kind[AddCreditKindMaxGame]
```

## Credit Format

`OnChangeCreditCount:all,credit,service,debug`

- `all`: Total credits across all sources
- `credit`: Production credits (from NesysService)
- `service`: Service credits
- `debug`: Debug/test credits (from Z key)

## Key Findings

1. **Z is the local coin input** - Confirmed by operator
2. **Each Z adds 1 debug credit** - Verified by log
3. **Credit type is "debug"** - Not production credits
4. **No NesysService involvement** - Z works without NesysService
5. **No GALAXYIO involvement** - Z is local game state only
6. **Threshold met at 2 credits** - Start accepted after 2 Z presses

## Classification

**LOCAL_DEBUG_CREDIT_INPUT**

---

**See also:** `G26_CREDIT_STATE_TRANSITIONS.md`
