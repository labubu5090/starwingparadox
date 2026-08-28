# Phase 2A-G18 Final Report

## Classification: EVIDENCE_LOCKED_CODEC_AND_DETERMINISTIC_HARNESS

**Phase**: 2A-G18  
**Date**: 2026-08-29  
**Status**: COMPLETE  
**Commit**: [pending]

---

## Executive Summary

Phase 2A-G18 established an evidence-locked codec, deterministic timeout model, session scenario harness, and expanded safety guards for the clean-room protocol foundation. All G17 semantic overreach was identified and corrected.

---

## 1. Deliverables

### 1.1 New Source Modules (6)

| Module | Purpose | Lines |
|--------|---------|-------|
| `codec.py` | Evidence-locked codec with explicit evidence levels | ~200 |
| `timeout.py` | Deterministic clock and timeout model | ~220 |
| `harness.py` | Session scenario harness | ~265 |
| `scenarios.py` | Versioned synthetic scenarios | ~280 |
| `invariants.py` | State-machine invariant checker | ~260 |
| `safety.py` | Expanded safety guards | ~290 |

### 1.2 New Test Modules (6)

| Module | Tests |
|--------|-------|
| `test_codec.py` | 16 tests |
| `test_timeout.py` | 18 tests |
| `test_harness.py` | 12 tests |
| `test_scenarios.py` | 10 tests |
| `test_invariants.py` | 8 tests |
| `test_safety_expanded.py` | 8 tests |

### 1.3 Bug Fixes (3)

1. **`run_lifecycle` dispatch bug** (CRITICAL): Lifecycle commands with `numeric_id=None` were unreachable via `get_by_id()`. Fixed to dispatch by `message_name`.
2. **`receive_client_start` logic bug** (MEDIUM): `START_PENDING` appeared in both duplicate-check and valid-state conditions. Fixed to only accept `TRANSPORT_OPEN`.
3. **`close()` event recording** (LOW): Non-terminal close only recorded TRANSPORT_CLOSED. Now records both SESSION_FAILED and TRANSPORT_CLOSED.

### 1.4 Documentation (1)

- `G17_COMMAND_IMPLEMENTATION_AUDIT.md`: Complete audit of all 8 G17 commands

---

## 2. Test Results

```
222 tests passed, 0 failed
Mypy: 0 errors (16 source files)
Ruff: 0 errors
```

### 2.1 Test Breakdown

| Category | Count |
|----------|-------|
| G17 unit tests | 130 |
| G18 unit tests | 82 |
| Integration tests | 10 |
| **Total** | **222** |

---

## 3. Evidence Hierarchy

| Component | Evidence Level | Source |
|-----------|---------------|--------|
| Length prefix (4-byte LE) | CONFIRMED | G16 observed |
| Message type (first byte) | ELIGIBLE | G17 simplified model |
| Packet ID | UNKNOWN | Always 0 |
| Payload | CONFIRMED | Opaque bytes |
| Timeout values | SYNTHETIC | No G16 evidence |
| State transitions | CONFIRMED | G16 lifecycle states |

---

## 4. Safety Verification

All G18 modules:
- Do NOT import restricted modules
- Do NOT use production hostnames
- Do NOT reference certificate operations
- Do NOT create named pipes
- Do NOT access Windows registry
- Do NOT expose production entry points
- Do NOT contain deployment artifacts

---

## 5. Quality Gates

| Gate | Status |
|------|--------|
| All tests pass | PASS |
| Mypy 0 errors | PASS |
| Ruff 0 errors | PASS |
| No restricted imports | PASS |
| No production hostnames | PASS |
| No certificate references | PASS |
| No pipe paths | PASS |
| No registry paths | PASS |
| No deployment artifacts | PASS |

---

## 6. G18 Corrections Applied

### 6.1 Event Type Corrections
- `send_cert_error()`: Changed from `SYNTHETIC_TIMEOUT` to `SESSION_FAILED`
- `send_nw_error()`: Changed from `SYNTHETIC_TIMEOUT` to `SESSION_FAILED`

### 6.2 State Machine Corrections
- `receive_client_start()`: Fixed logic bug where `START_PENDING` was in both conditions
- `close()`: Now records both `SESSION_FAILED` and `TRANSPORT_CLOSED` for non-terminal states

### 6.3 Dispatch Corrections
- `run_lifecycle()`: Fixed to dispatch lifecycle commands by `message_name` instead of `get_by_id()`

---

## 7. What Was NOT Changed

- No original game files modified
- No production binary format assumptions
- No protobuf parsing added
- No real timeout values assumed
- No payload schemas invented
- No production entry points created

---

## 8. Recommendations for G19

1. Run full test suite against production-like traffic patterns
2. Verify no regression in existing TCP server integration
3. Consider adding fuzzing for frame validation
4. Document any new evidence discovered during runtime testing

---

## 9. Classification

**EVIDENCE_LOCKED_CODEC_AND_DETERMINISTIC_HARNESS**

This phase established:
- Evidence-locked codec with explicit evidence levels
- Deterministic timeout model for testing
- Session scenario harness with versioned scenarios
- State-machine invariant checker
- Expanded safety guards
- Complete audit trail for all G17 commands

All G17 semantic overreach was identified and corrected. The clean-room foundation is now evidence-locked and ready for runtime testing.
