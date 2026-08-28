# CLEANROOM SYNTHETIC TEST STRATEGY

**Date:** August 28, 2026  
**Phase:** 2A-G17  
**Classification:** Test Strategy

---

## Overview

The Synthetic Test Strategy defines the approach for testing the Starwing cleanroom transport implementation using synthetically generated commands and scenarios, validated against G16 evidence.

---

## Test Philosophy

1. **Synthetic Generation** - Commands generated from specifications, not captured traffic
2. **Coverage-Driven** - All G16-defined commands and states covered
3. **Fault Injection** - Systematic error condition testing
4. **Regression Prevention** - Automated test suite for continuous validation

---

## Test Categories

### 1. Unit Tests

| Test Type | Description | Coverage Target |
|---|---|---|
| Frame Validation | Individual validation rule testing | 100% rules |
| Command Parsing | Command deserialization testing | 100% commands |
| State Machine | State transition testing | 100% transitions |
| Parameter Validation | Schema validation testing | 100% schemas |

### 2. Integration Tests

| Test Type | Description | Coverage Target |
|---|---|---|
| End-to-End Commands | Full command lifecycle | 100% commands |
| Session Workflows | Complete session scenarios | 100% states |
| Error Recovery | Error handling paths | 100% error codes |
| Concurrency | Multi-session testing | Key scenarios |

### 3. System Tests

| Test Type | Description | Coverage Target |
|---|---|---|
| Load Testing | Throughput and latency | Performance targets |
| Stress Testing | Resource limits | Failure modes |
| Soak Testing | Extended operation | Stability |

---

## Synthetic Command Generation

### Generation Process

```
┌─────────────────────────────────────┐
│  G16 Command Specification          │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│  Parameter Space Definition         │
│  - Valid ranges                     │
│  - Boundary values                  │
│  - Invalid variants                 │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│  Command Generator                  │
│  - Random sampling                  │
│  - Edge case focus                  │
│  - Coverage tracking                │
└───────────────────┬─────────────────┘
                    │
                    ▼
┌─────────────────────────────────────┐
│  Synthetic Command Stream           │
└─────────────────────────────────────┘
```

### Generator Implementation

```typescript
class SyntheticCommandGenerator {
    generateValidCommand(commandId: number): Command;
    generateInvalidCommand(commandId: number, errorType: ErrorType): Command;
    generateBoundaryCommand(commandId: number): Command[];
    generateMalformedCommand(variant: MalformVariant): Command;
}
```

**G16 Ref:** §7.1.1

---

## Test Scenarios

### Scenario 1: Session Lifecycle
```
1. Create session → ACTIVE
2. Attach session → Verify ACTIVE
3. Suspend session → SUSPENDED
4. Resume session → ACTIVE
5. Destroy session → DESTROYING → DESTROYED
```
**G16 Ref:** §7.2.1

### Scenario 2: Command Dispatch
```
1. Register handler
2. Send valid command → Success response
3. Send unknown command → UNKNOWN_COMMAND error
4. Send invalid params → INVALID_PARAMS error
```
**G16 Ref:** §7.2.2

### Scenario 3: Frame Validation
```
1. Send valid frame → Accepted
2. Send invalid magic → Rejected
3. Send wrong checksum → Rejected
4. Send oversized frame → Rejected
```
**G16 Ref:** §7.2.3

### Scenario 4: Error Recovery
```
1. Trigger timeout → Session suspended
2. Trigger checksum error → Frame rejected
3. Trigger handler error → Error response
4. Verify system stability
```
**G16 Ref:** §7.2.4

---

## Fault Injection Matrix

| Fault Type | Injection Point | Expected Behavior |
|---|---|---|
| Network Timeout | Transport layer | Session suspend |
| Checksum Corruption | Frame validation | Frame rejection |
| Invalid Command | Dispatch layer | Error response |
| Resource Exhaustion | Session management | Graceful degradation |
| State Violation | State machine | Error handling |

**G16 Ref:** §7.3.1

---

## Coverage Metrics

| Metric | Target | Measurement |
|---|---|---|
| Code Coverage | > 90% | Line/branch coverage |
| Command Coverage | 100% | All G16 commands tested |
| State Coverage | 100% | All states and transitions |
| Error Coverage | 100% | All error codes tested |
| Path Coverage | > 80% | Critical paths |

---

## Test Execution

### Local Execution
```bash
npm run test:unit
npm run test:integration
npm run test:synthetic
```

### CI Integration
```yaml
test:
  stage: test
  script:
    - npm run test:unit -- --coverage
    - npm run test:integration
    - npm run test:synthetic
  coverage: '/Lines\s*:\s*(\d+\.?\d*)%/'
```

**G16 Ref:** §7.4.1

---

*Synthetic test strategy for Phase 2A-G17 cleanroom transport implementation.*
