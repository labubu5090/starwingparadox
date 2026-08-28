# G17 Command Implementation Audit

## Classification: EVIDENCE_LOCKED_CODEC_AND_DETERMINISTIC_HARNESS

**Phase**: 2A-G18  
**Date**: 2026-08-29  
**Status**: COMPLETE

---

## Audit Summary

This audit reviews all 8 G17-implemented commands for semantic overreach and documents what is confirmed vs inferred.

---

## 1. Confirmed Commands (HIGH Confidence)

### 1.1 LCOMMAND_CLIENT_START (Client → Service)
- **G16 Evidence**: Identity confirmed (symbolic name)
- **G17 Implementation**: `handle_client_start()` transitions TRANSPORT_OPEN → START_PENDING → ACTIVE
- **Semantic Overreach**: NONE. State transitions are documented as synthetic.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE

### 1.2 LCOMMAND_CLIENT_END (Client → Service)
- **G16 Evidence**: Identity confirmed (symbolic name)
- **G17 Implementation**: `handle_client_end()` transitions ACTIVE → END_PENDING → CLOSED
- **Semantic Overreach**: NONE. State transitions are documented as synthetic.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE

### 1.3 LCOMMAND_PING (Client → Service)
- **G16 Evidence**: Identity confirmed, numeric ID 0x66 confirmed
- **G17 Implementation**: Registered handler for 0x66
- **Semantic Overreach**: NONE. Ping behavior is documented as synthetic.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE

### 1.4 SCOMMAND_CLIENT_START_REPLY (Service → Client)
- **G16 Evidence**: Identity confirmed (symbolic name)
- **G17 Implementation**: Synthetic reply after CLIENT_START
- **Semantic Overreach**: NONE. Reply behavior is documented as synthetic.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE

### 1.5 SCOMMAND_PING_RESPONSE (Service → Client)
- **G16 Evidence**: Identity confirmed, numeric ID 0x67 confirmed
- **G17 Implementation**: Synthetic response to PING
- **Semantic Overreach**: NONE. Response behavior is documented as synthetic.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE

### 1.6 SCOMMAND_CERT_ERROR (Service → Client)
- **G16 Evidence**: Identity confirmed (symbolic name)
- **G17 Implementation**: `send_cert_error()` transitions to FAILED
- **Semantic Overreach**: **CORRECTED in G18**. Previously used SYNTHETIC_TIMEOUT event type. Now uses SESSION_FAILED.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE (after G18 correction)

### 1.7 SCOMMAND_NW_ERROR (Service → Client)
- **G16 Evidence**: Identity confirmed (symbolic name)
- **G17 Implementation**: `send_nw_error()` transitions to FAILED
- **Semantic Overreach**: **CORRECTED in G18**. Previously used SYNTHETIC_TIMEOUT event type. Now uses SESSION_FAILED.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE (after G18 correction)

### 1.8 SCOMMAND_NWRECOVER_NOTICE (Service → Client)
- **G16 Evidence**: Identity confirmed (symbolic name)
- **G17 Implementation**: `send_nwrecover_notice()` records SYNTHETIC_DISCONNECT event
- **Semantic Overreach**: NONE. Recovery notice behavior is documented as synthetic.
- **Payload Semantics**: NOT confirmed. No payload parsing.
- **Status**: SAFE

---

## 2. Bug Fixes (G18)

### 2.1 `run_lifecycle` Dispatch Bug (CRITICAL)
- **Issue**: Lifecycle commands with `numeric_id=None` could never be matched by `get_by_id()` lookup
- **Fix**: Changed dispatch to use `message_name` instead of `get_by_id()` for lifecycle commands
- **Impact**: `run_lifecycle` now correctly dispatches LCOMMAND_CLIENT_START and LCOMMAND_CLIENT_END

### 2.2 `receive_client_start` Logic Bug (MEDIUM)
- **Issue**: `START_PENDING` appeared in both duplicate-check and valid-state conditions
- **Fix**: Changed valid-state check to only accept `TRANSPORT_OPEN`
- **Impact**: Duplicate start now correctly rejected when already in START_PENDING

### 2.3 `close()` Event Recording (LOW)
- **Issue**: `close()` from non-terminal state only recorded TRANSPORT_CLOSED, not SESSION_FAILED
- **Fix**: Now records both SESSION_FAILED and TRANSPORT_CLOSED for non-terminal states
- **Impact**: Event log now correctly reflects both state change and transport closure

---

## 3. Evidence Levels

| Component | Evidence Level | Source |
|-----------|---------------|--------|
| Length prefix (4-byte LE) | CONFIRMED | G16 observed |
| Message type (first byte) | ELIGIBLE | G17 simplified model |
| Packet ID | UNKNOWN | Always 0 |
| Payload | CONFIRMED | Opaque bytes |

---

## 4. Safety Verification

All 8 implemented commands:
- Do NOT import restricted modules (socket, requests, httpx, winreg, subprocess)
- Do NOT use production hostnames
- Do NOT reference certificate operations
- Do NOT create named pipes
- Do NOT access Windows registry
- Do NOT expose production entry points

---

## 5. Test Coverage

- **Unit tests**: 212 (130 G17 + 82 G18)
- **Integration tests**: 10
- **Total**: 222 tests, all passing
- **Mypy**: 0 errors (16 source files)
- **Ruff**: 0 errors

---

## 6. Conclusion

All 8 G17-implemented commands are SAFE. No semantic overreach detected. G18 corrections were applied to:
1. Fix `run_lifecycle` dispatch bug
2. Fix `receive_client_start` logic bug
3. Fix `close()` event recording
4. Update CERT_ERROR and NW_ERROR event types

**Classification**: EVIDENCE_LOCKED_CODEC_AND_DETERMINISTIC_HARNESS
