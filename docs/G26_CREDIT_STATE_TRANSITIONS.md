# G26 Credit State Transitions

**Phase:** 2A-G26  
**Date:** 2026-08-29

## Timeline

| Time | Credits | Action |
|------|---------|--------|
| 09:45:51.804 | all[0] | ResetCredit |
| 09:47:54.213 | 0,0,0,0 | OnChangeCreditCount |
| 09:50:23.525 | 1,0,0,1 | ZPressed #1 |
| 09:50:24.140 | 2,0,0,2 | ZPressed #2 |

## Format

`OnChangeCreditCount:all,credit,service,debug`

- **all**: Total credits
- **credit**: Production credits (NesysService)
- **service**: Service credits
- **debug**: Debug credits (Z key)

## Credit Source

**LOCAL_DEBUG_INPUT**

- Z key → ACPP_DebugActor → UTestModeWork → UMachineDataWork
- No NesysService involvement
- No GALAXYIO involvement
- No named pipe involvement
- No localhost:1042 involvement

## Key Evidence

```
UMachineDataWork::AddDebugCredit / success / _credit[1] tmpCredit[1] kind[AddCreditKindMaxGame] checkLockout:[0] / all[2](1) credit:[0] service:[0] debug:[2](1)
```

## Conclusion

Credits are entirely local game state. No server interaction required.
