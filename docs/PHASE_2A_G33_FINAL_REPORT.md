# Phase 2A-G33 Final Report

**Commit**: pending  
**Classification**: TCP_DECODER_BUG_FIXED  
**Timestamp**: 2026-08-29T21:10:00Z

## Summary

G33 corrected the server-side TCP decoder ambiguity and recovered the exact MatchingServer initialization condition. The game's MatchingServer object requires a server address to be resolved before it can connect. Two paths exist: NESYS (production trust) and Config (safe local).

## Key Findings

### 1. G32 Decode-Error Root Cause

**Classification**: SERVER_DECODER_BUG (PING_CONTROL_FRAME_NO_ONEOF_REQUIRED)

The game sends TWO frames per heartbeat cycle:
1. A Ping frame (messageType=0x66) — decoded successfully via raw fallback
2. A second frame with empty Message oneof — FAILED before fix, SUCCEEDS after fix

The generated decoder required `WhichOneof("Message")` to be non-None. The fix falls back to the `MESSAGE_TYPE_MAP` registry when the oneof is unset but messageType is known.

### 2. MatchingServer Initialization Gate

The gate expression is:
```
if (!MatchingServer address available) → "Error No MatchingServer so initialize Nesys before"
else → [UAcrProtocol::Connect] using NESYS or Config address
```

Two paths:
- **NESYS path**: Requires `UCPP_NesysControl::Setup Completed` + certificate success → PRODUCTION_TRUST (excluded)
- **Config path**: Uses `DefaultMatchingServerAddress` from command line → SAFE_LOCAL (permitted)

### 3. IsOnline Semantics

`IsOnline` represents production NESYS certificate-authenticated state. It is polled by `SystemDataCheck::Tick` before allowing the game to proceed. **Must not be fabricated.**

### 4. Config Command-Line Parameters

The binary contains:
- `UseConfigMatchingServer use commandLine value.(%d)` — reads flag from command line
- `HttpServerAddress use commandLine value.(%s)` — reads HTTP address from command line
- `MatchingServer : %s (UseConfigMatchingServer : %d)` — logs the config value

## Quality Gates

| Metric | G32 Baseline | G33 Result |
|--------|-------------|------------|
| pytest | 1058 passed, 1 skipped | 1078 passed, 1 skipped |
| G33 tests | N/A | 20/20 passed |
| Ruff | OK | OK |
| Protected hash | CE4C8905... | CE4C8905 (MATCH) |

## G34 Recommendation

Launch the game with command-line arguments:
```
UseConfigMatchingServer=1
DefaultMatchingServerAddress=127.0.0.1:4001
HttpServerAddress=127.0.0.1:4001
```

This bypasses the NESYS initialization gate using the game's own Config fallback path. No certificate trust, no identity fabrication required.
