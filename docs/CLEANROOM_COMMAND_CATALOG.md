# CLEANROOM COMMAND CATALOG

**Date:** August 28, 2026  
**Phase:** 2A-G17  
**Classification:** Reference Document

---

## Overview

The Command Catalog defines all commands supported by the Starwing transport system, derived exclusively from G16 specification evidence.

---

## Command Categories

### 1. System Commands

| Command ID | Name | Parameters | Response | G16 Ref |
|---|---|---|---|---|
| 0x0001 | PING | timestamp: uint64 | PONG + timestamp | §5.3.1 |
| 0x0002 | VERSION | - | version_info | §5.3.2 |
| 0x0003 | CAPABILITIES | - | capability_flags | §5.3.3 |
| 0x0004 | SHUTDOWN | reason: string | ACK | §5.3.4 |

### 2. Session Commands

| Command ID | Name | Parameters | Response | G16 Ref |
|---|---|---|---|---|
| 0x0100 | SESSION_CREATE | params: session_params | session_id | §5.4.1 |
| 0x0101 | SESSION_ATTACH | session_id: uint32 | status | §5.4.2 |
| 0x0102 | SESSION_DETACH | session_id: uint32 | status | §5.4.3 |
| 0x0103 | SESSION_DESTROY | session_id: uint32 | status | §5.4.4 |

### 3. Data Commands

| Command ID | Name | Parameters | Response | G16 Ref |
|---|---|---|---|---|
| 0x0200 | DATA_SEND | session_id, payload | send_receipt | §5.5.1 |
| 0x0201 | DATA_BROADCAST | payload | broadcast_receipt | §5.5.2 |
| 0x0202 | DATA_REQUEST | session_id, query | query_result | §5.5.3 |
| 0x0203 | DATA_CANCEL | request_id | cancel_ack | §5.5.4 |

### 4. State Commands

| Command ID | Name | Parameters | Response | G16 Ref |
|---|---|---|---|---|
| 0x0300 | STATE_QUERY | session_id | state_info | §5.6.1 |
| 0x0301 | STATE_SET | session_id, key, value | set_ack | §5.6.2 |
| 0x0302 | STATE_DELETE | session_id, key | delete_ack | §5.6.3 |
| 0x0303 | STATE_LIST | session_id | key_list | §5.6.4 |

---

## Command Structure

```
┌──────────────────────────────────────┐
│           Command Frame              │
├──────────────────────────────────────┤
│ Header (16 bytes)                    │
│   - Command ID (2 bytes)             │
│   - Flags (2 bytes)                  │
│   - Sequence Number (4 bytes)        │
│   - Session ID (4 bytes)             │
│   - Payload Length (4 bytes)         │
├──────────────────────────────────────┤
│ Payload (variable)                   │
│   - Command-specific data            │
├──────────────────────────────────────┤
│ Checksum (4 bytes)                   │
│   - CRC32 of header + payload        │
└──────────────────────────────────────┘
```

---

## Error Response Codes

| Code | Name | Description | G16 Ref |
|---|---|---|---|
| 0xE001 | INVALID_COMMAND | Unknown command ID | §6.1.1 |
| 0xE002 | INVALID_PARAMS | Malformed parameters | §6.1.2 |
| 0xE003 | SESSION_NOT_FOUND | Invalid session ID | §6.1.3 |
| 0xE004 | STATE_ERROR | State operation failed | §6.1.4 |
| 0xE005 | TIMEOUT | Command timeout | §6.1.5 |

---

*Command catalog for Phase 2A-G17 cleanroom transport implementation.*
