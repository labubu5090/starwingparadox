# TCP Server Status

**Date:** 2026-08-26
**Status:** TRANSPORT_ONLY

---

## Implementation

| Feature | Detail |
|---------|--------|
| Framework | `asyncio` TCP server |
| Port | 6666 |
| Framing | 4-byte little-endian length prefix |
| Buffering | Incremental buffering for partial reads |
| Handler dispatch | Registry pattern with `Ping` handler |
| Timeout | 30 seconds (configurable) |
| Shutdown | Graceful (drains connections) |

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

## Integration Status

- **NOT integrated with cabinet capture**
- Transport layer only — no protocol handlers beyond `Ping`
- No battle or matching logic connected

---

## Summary

The TCP transport is fully functional for raw message send/receive. Application-level protocol handlers (matching, battle, cabinet) are **not yet wired** to the transport layer.
