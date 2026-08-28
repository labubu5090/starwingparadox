# G9 Post-HTTP Gating Analysis

**Date:** 2026-08-28
**Run:** G9-A cold boot validation
**Classification:** `BGAMECONNECT_GATES_TCP_CONNECTION`

## Executive Summary

After HTTP matching succeeds (game receives `{"ip_addr":"127.0.0.1:6666"}`), the game **does not establish a TCP connection** because:

1. **NESYS is offline** (CertError spam during boot) → `bNesysServerLive = false`, `IsOnline = 0`
2. **OpenKey.json is missing** → SystemDataCheck cannot verify game state
3. **SystemDataCheck enters error state** (DispError) → TCP connection callback is aborted

The TCP address was resolved successfully (line 108161-108163) but the connection was never initiated. The server was ready 3+ minutes before the game's HTTP request, ruling out server startup race.

## Timeline

| # | Time | Phase | Event | Status |
|---|------|-------|-------|--------|
| 1 | 02:36.34 | BOOT | NESYS CertError spam (12 cycles) | FAIL |
| 2 | 02:36.35 | BOOT | Boot → Notice | OK |
| 3 | 02:36.40 | SEAT_CHECK | Notice → SeatCheck → AdvertiseMovie | OK |
| 4 | 02:36.40 | MATCHING | HTTP POST matching/server sent | SENT |
| 5 | 02:36.41 | MATCHING | HTTP 200 received, address=127.0.0.1:6666 | SUCCESS |
| 6 | 02:36.41 | TCP_SETUP | TcpThread created, SetupConnect initiated | INITIATED |
| 7 | 02:36.41 | SYSTEM_CHECK | IsOnline[0] — NESYS offline | FAIL |
| 8 | 02:36.41 | SYSTEM_CHECK | OpenKey.json load error | FAIL |
| 9 | 02:36.41 | SYSTEM_CHECK | NESYS Event error | FAIL |
| 10 | 02:36.41 | SYSTEM_CHECK | DispError displayed | ERROR |
| 11 | 02:36.41 | TCP_SETUP | TCP address resolved (127.0.0.1:6666) | RESOLVED |
| 12 | 02:36.51 | SYSTEM_CHECK | SystemDataCheck ends with error | END |
| 13 | 02:36.51 | PROMOTION | InsertStart animation looping | ACTIVE |
| 14 | 02:37.33 | EXIT | Operator closes game | CLOSED |
| 15 | 02:38.27 | CRASH | Render thread 30s timeout (aftermath) | CRASH |

## Key Findings

### 1. NESYS CertError Blocks NESYS Authentication

During boot (02:36.34-02:36.35), the game logs repeated `NesysControlErrorMessage / ENesysNetworkServerMessage[CertError]` with `RequestNetworkInfo OK → RequestNetworkInfo Error` cycles. This indicates:

- The game is trying to authenticate with NESYS
- NESYS service crashes with exit code -1 before authentication completes
- `bNesysServerLive` remains false
- `IsOnline` remains 0

### 2. OpenKey.json Missing

The game expects `D:/Saved/ACRSaved/SaveData/OpenKey.json` to exist. This file is normally created by NESYS after successful authentication. Since NESYS never came online, the file never existed, and `LoadKeyFile error` is logged.

### 3. SystemDataCheck Error State

The SystemDataCheck phase checks:
1. NESYS IsOnline → **FAIL** (IsOnline[0])
2. OpenKey.json → **FAIL** (LoadKeyFile error)
3. NESYS Event → **FAIL** (IsEventCheck[0] IsEventError[0])

This triggers DispError, setting the game into an error state.

### 4. TCP Connection Aborted

Despite TCP address being resolved successfully at 02:36.41:804, the game never establishes the connection. The only event between resolution and game close is the SystemDataCheck error. The error state appears to abort the TCP connection callback.

### 5. Operator-Forced Close

The game closes at 02:37:33 with `Closing by request` (operator-forced), NOT a spontaneous crash. The render thread crash at 02:38:27 is a 30s timeout aftermath of the forced close.

## Classification

**Primary: `BGAMECONNECT_GATES_TCP_CONNECTION`**

The game-level `bGameConnect` flag gates TCP connection establishment. The flag is never set because:
- NESYS offline → OpenKey missing → SystemDataCheck error → bGameConnect remains false
- TCP connection callback is aborted before completion

**Secondary factors:**
- NESYS CertError blocks NESYS authentication (root cause of offline state)
- OpenKey.json missing (consequence of NESYS offline)
- SystemDataCheck error state prevents TCP completion

## Server Evidence

| Metric | Value |
|--------|-------|
| Total TCP connections | 0 |
| Readiness probe connections | 2 (ACCEPT #1, #2) |
| Probable game connections | 0 |
| Decoded game frames | 0 |
| HTTP requests | 1 (POST /mock/matching/server → 200) |
| Server ready before game request | ~180 seconds |

## Conclusion

The post-HTTP gating condition is caused by **NESYS offline state** → **missing OpenKey.json** → **SystemDataCheck error** → **TCP connection aborted**. The server was fully ready and responded correctly to the HTTP matching request, but the game-level NESYS dependency prevents TCP connection establishment.

To resolve this, the NESYS service (NesysService.exe) must be operational and able to authenticate before the game can proceed past SystemDataCheck and establish TCP connections.
