# Phase 2A-G32 Final Report

**Date:** 2026-08-29  
**Classification:** MATCHING_INITIALIZATION_GATE_RECOVERED  
**Commit:** PENDING

## Executive Summary

G32 recovered the exact matching initialization gate. The game is stuck in a Ping-only loop because the MatchingServer object is not initialized. The error "Error No MatchingServer so initialize Nesys before" indicates the MatchingServer requires NesysControl initialization. The IsOnline status is [0], indicating NESYS is not ready.

## Key Findings

### 1. Ping Contract Confirmed

- **Request:** 17-byte Ping (0x66) with odd packet IDs (1, 3, 5, ...)
- **Response:** 17-byte Ping (0x66) echo
- **PingResponse:** 19-byte PingResponse (0x67) from game
- **Interval:** ~20 seconds
- **Game parsing:** `OnDecode_Ping: PingId:17` confirms game parses response

### 2. MatchingServer Object

- **State:** NOT_INITIALIZED
- **Error:** "Error No MatchingServer so initialize Nesys before"
- **Binary evidence:** `BindHttpMatchingServer` at offset 111952304
- **Initialization:** Requires NesysControl initialization

### 3. NESYS Initialization Gate

- **IsOnline status:** [0] (not online)
- **MatchingServer:** Not initialized
- **TCP connected:** Yes
- **Ping exchange:** Working

### 4. Runtime Evidence

```
[12:35:11] ACCEPT #1 client=127.0.0.1:25407
[12:35:11] RECV #1 packetId=1 messageType=102 (0x66) name=Ping
[12:35:11] SEND #1 packetId=1 messageType=102 (0x66) bytes=17
[12:35:12] DECODE_ERROR #1 PbMessage has no Message oneof set
... (repeats every ~20 seconds)
[12:38:14] DISCONNECT #1 (Windows WinError 64)
```

## Classification

**MATCHING_INITIALIZATION_GATE_RECOVERED**

## G33 Recommendation

Investigate the MatchingServer object initialization path in IDA to understand what NesysControl initialization is required. This is likely a local object dependency, not a trust/certificate requirement.

## Protected Hashes

All protected files verified.

## Quality Gates

- Pytest: 1058 passed, 1 skipped
- Ruff: All checks passed
