# CLEANROOM SESSION STATE MACHINE

**Date:** August 28, 2026  
**Phase:** 2A-G17  
**Classification:** Design Document

---

## Overview

The Session State Machine defines the deterministic lifecycle of transport sessions in the Starwing system, derived from G16 specification evidence.

---

## State Definitions

### Primary States

| State | Description | G16 Ref |
|---|---|---|
| IDLE | No active session, awaiting creation | §4.1.1 |
| CREATING | Session initialization in progress | §4.1.2 |
| ACTIVE | Session fully operational | §4.1.3 |
| SUSPENDED | Session temporarily inactive | §4.1.4 |
| DESTROYING | Session teardown in progress | §4.1.5 |
| DESTROYED | Session terminated | §4.1.6 |

---

## State Diagram

```
                    ┌─────────────┐
                    │    IDLE     │
                    └──────┬──────┘
                           │ SESSION_CREATE
                           ▼
                    ┌─────────────┐
                    │  CREATING   │
                    └──────┬──────┘
                           │ creation_complete
                           ▼
                    ┌─────────────┐
              ┌─────│   ACTIVE    │─────┐
              │     └──────┬──────┘     │
              │            │            │
              │ SUSPEND    │ DESTROY    │
              ▼            ▼            ▼
       ┌─────────────┐          ┌─────────────┐
       │  SUSPENDED  │          │ DESTROYING  │
       └──────┬──────┘          └──────┬──────┘
              │                        │
              │ RESUME                 │ destroy_complete
              ▼                        ▼
       ┌─────────────┐          ┌─────────────┐
       │   ACTIVE    │          │  DESTROYED  │
       └─────────────┘          └─────────────┘
```

---

## Transition Rules

### IDLE → CREATING
- **Trigger:** SESSION_CREATE command received
- **Guard:** Valid session parameters provided
- **Action:** Allocate session resources, assign session ID
- **G16 Ref:** §4.2.1

### CREATING → ACTIVE
- **Trigger:** Creation process completed successfully
- **Guard:** All required resources allocated
- **Action:** Notify session owner, enable command processing
- **G16 Ref:** §4.2.2

### ACTIVE → SUSPENDED
- **Trigger:** SESSION_DETACH command or timeout
- **Guard:** Session in good standing
- **Action:** Pause command processing, preserve state
- **G16 Ref:** §4.2.3

### SUSPENDED → ACTIVE
- **Trigger:** SESSION_ATTACH command
- **Guard:** Session not expired
- **Action:** Resume command processing
- **G16 Ref:** §4.2.4

### ACTIVE → DESTROYING
- **Trigger:** SESSION_DESTROY command or fatal error
- **Guard:** None
- **Action:** Initiate cleanup sequence
- **G16 Ref:** §4.2.5

### DESTROYING → DESTROYED
- **Trigger:** Cleanup completed
- **Guard:** All resources released
- **Action:** Finalize session, release session ID
- **G16 Ref:** §4.2.6

---

## State Data

### Session Record
```
Session {
    id: uint32
    state: SessionState
    owner: ConnectionId
    created_at: timestamp
    last_activity: timestamp
    timeout_ms: uint32
    data: Map<String, Any>
}
```

---

## Timeout Handling

| State | Timeout Action | G16 Ref |
|---|---|---|
| IDLE | N/A | - |
| CREATING | Return to IDLE after 30s | §4.3.1 |
| ACTIVE | Transition to SUSPENDED after configured timeout | §4.3.2 |
| SUSPENDED | Transition to DESTROYING after expiry | §4.3.3 |
| DESTROYING | Force destroy after 10s | §4.3.4 |
| DESTROYED | Immediate cleanup | §4.3.5 |

---

*Session state machine for Phase 2A-G17 cleanroom transport implementation.*
