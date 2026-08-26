# TCP Server Status

**Date:** 2026-08-26
**Status:** TRANSPORT_ONLY
**Legacy Regression:** TCP framing tests added (test_tcp_legacy.py)

---

## Implementation

| Feature | Detail | Legacy Parity |
|---------|--------|---------------|
| Framework | `asyncio` TCP server | ✅ SOURCE_VERIFIED (net.createServer) |
| Port | 6666 | ✅ SOURCE_VERIFIED (starwing.js:29) |
| Bind address | 0.0.0.0 | ✅ SOURCE_VERIFIED (starwing.js:342) |
| Framing | 4-byte uint32 LE length prefix | ✅ SOURCE_VERIFIED (E6-E13) |
| Buffering | Incremental buffering for partial reads | ✅ FUNCTIONAL_PARITY |
| Handler dispatch | Registry pattern with `Ping` handler | ✅ SOURCE_VERIFIED (E32-E36) |
| Timeout | 30 seconds (configurable) | ⚠️ EXPERIMENTAL (legacy unset) |
| Max frame size | 1 MiB safety limit | ⚠️ EXPERIMENTAL (legacy unlimited) |
| Shutdown | Graceful (drains connections) | ✅ FUNCTIONAL_PARITY |
| IP authorization | Not implemented | ❌ NOT_IMPLEMENTED (legacy E19-E21) |

---

## Architecture

```
Client → [4-byte LE length][payload] → TCP Server (port 6666)
                                          ↓
                                   Handler Dispatch Registry
                                          ↓
                                   Ping Handler (registered)
```

---

## Legacy Regression Coverage

| Test Class | Source Evidence | Status |
|------------|----------------|--------|
| TestLengthPrefixEncode | E6 (starwing.js:71-73) | ✅ |
| TestLengthPrefixDecode | E7-E8 (starwing.js:101,104) | ✅ |
| TestOneFrameRequestHandling | tcp_server.py:103-157 | ✅ |
| TestResponseFraming | E6 (starwing.js:62-78) | ✅ |
| TestConnectionCloseBehavior | E23-E27 (starwing.js:303-341) | ✅ |
| TestMultipleFramesPerConnection | tcp_server.py:103-131 | ✅ |
| TestProposedProtections | §4.2-4.5 of audit | ✅ |
| TestPortAndBindAddress | E14-E18 | ✅ |
| TestHandlerDispatch | E32-E36 | ✅ |

---

## Integration Status

- **NOT integrated with cabinet capture**
- Transport layer only — no protocol handlers beyond `Ping`
- No battle or matching logic connected

---

## Summary

The TCP transport is fully functional for raw message send/receive. Application-level protocol handlers (matching, battle, cabinet) are **not yet wired** to the transport layer. Legacy regression tests verify framing protocol parity with the original JavaScript implementation.
