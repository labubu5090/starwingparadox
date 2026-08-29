# SystemDataCheck State Machine

**Phase:** 2A-G27  
**Date:** 2026-08-29

## State Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEMDATACHECK                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────────┐                   │
│  │ State 0:    │    │ State 2:         │                   │
│  │ EventRequest│───→│ CheckOpenKeyLoad │                   │
│  └─────────────┘    └──────────────────┘                   │
│         │                    │                              │
│         │ (IsOnline=0)      │ (File found)                 │
│         │ proceeds          │ proceeds                     │
│         │                    │                              │
│         │                    ▼                              │
│         │            ┌──────────────────┐                   │
│         │            │ State 3:         │                   │
│         │            │ CheckOpenKeyUpd  │                   │
│         │            └──────────────────┘                   │
│         │                    │                              │
│         │                    │ (NESYS Event error)          │
│         │                    │                              │
│         │                    ▼                              │
│         │            ┌──────────────────┐                   │
│         │            │ State 19:        │                   │
│         │            │ DispError        │                   │
│         │            └──────────────────┘                   │
│         │                    │                              │
│         │                    │ (wait ~10s)                  │
│         │                    │                              │
│         │                    ▼                              │
│         │            ┌──────────────────┐                   │
│         │            │ State 20:        │                   │
│         │            │ End              │                   │
│         │            └──────────────────┘                   │
│         │                    │                              │
│         │                    │                              │
│         │                    ▼                              │
│         │            ┌──────────────────┐                   │
│         └───────────→│ Title            │                   │
│                      └──────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## State Details

### State 0: EventRequest
- **Check:** `UCPP_NesysControl::Get(this)->IsOnline[0]`
- **Result:** IsOnline=0, proceeds to State 2
- **Trust Dependency:** NONE

### State 2: CheckOpenKeyLoad
- **Check:** `UFileManagerTickable::LoadJsonFile / path[D:/Saved/ACRSaved/SaveData/OpenKey.json]`
- **Result:** LoadKeyFile error (file not found)
- **Trust Dependency:** NONE
- **Private Server Fixable:** YES

### State 3: CheckOpenKeyUpdate
- **Check:** `NESYS Event error. IsEventCheck[0] IsEventError[0]`
- **Result:** NESYS Event error, proceeds to State 19
- **Trust Dependency:** NESYS_EVENT_STATUS
- **Private Server Fixable:** UNKNOWN

### State 19: DispError
- **Check:** None (display only)
- **Result:** Error message shown, waits ~10 seconds
- **Trust Dependency:** NONE

### State 20: End
- **Check:** None (terminal state)
- **Result:** SetNextMode(Title) / isError[1]
- **Trust Dependency:** NONE

## Execution Order

Sequential: 0 → 2 → 3 → 19 → 20

## Primary Blocker

**OpenKey.json not found** at State 2

## Secondary Blocker

**NESYS Event error** at State 3
