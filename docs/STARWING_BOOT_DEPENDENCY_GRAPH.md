# Starwing Paradox Boot Dependency Graph (Corrected)

## Date: 2026-08-27

## Corrections

- **2026-08-28**: RENDERING_CRASH_STATUS: NOT_CONFIRMED_AS_SPONTANEOUS (operator-forced close)
- **2026-08-28**: messageType 103 (0x67): CAPTURE_SEQUENCE_CANDIDATE — not proven as PingResponse
- **2026-08-28**: G9-A analysis: Startup race DISPROVEN; post-HTTP gating classified as `BGAMECONNECT_GATES_TCP_CONNECTION`

## Boot Sequence (G9-A Validated)

```
1. AcrGame.exe (Bootstrap)
   Status: COMPLETED
   
2. Shipping executable (AcrGame-Win64-Shipping.exe)
   Status: COMPLETED
   
3. D3D11 initialization, GPU detection
   Status: COMPLETED (RTX 5090 detected)
   
4. Asset preloading (5132/7553 assets)
   Status: COMPLETED
   
5. NESYS Client Plugin (NesysClient) initializes
   Status: FAILED
   
6. NESYS Client attempts named pipe connection
   Pipe: \\.\pipe\nesys_games\...
   Status: FAILED (pipe does not exist)
   
7. NESYS status: offline (Nesys:0)
   Status: FAILED (offline)
   
8. CertError spam (12 cycles)
   Detail: NesysControlErrorMessage / ENesysNetworkServerMessage[CertError]
   Status: FAILED (NESYS offline)
   
9. Boot → Notice → SeatCheck → AdvertiseMovie
   Status: COMPLETED
   
10. HTTP matching-server discovery
    Request: dev.starwing.jp/mock/matching/server
    Response: {"ip_addr":"127.0.0.1:6666"}
    Status: VERIFIED_WORKING (server ready ~3min before request)
    
11. TCP connection setup
    TcpThread created, SetupConnect initiated
    Status: INITIATED
    
12. SystemDataCheck runs
    Checks NESYS IsOnline → FAIL (IsOnline[0])
    Checks OpenKey.json → FAIL (file missing)
    Checks NESYS Event → FAIL (IsEventCheck[0])
    Status: FAILED → DispError displayed
    
13. TCP address resolved
    ResolvedAddress: 127.0.0.1:6666 → ErrorCode[0]
    Status: RESOLVED (but connection aborted by error state)
    
14. SystemDataCheck ends with error
    SetNextMode[End](20), isError[1]
    Status: END_ERROR
    
15. PromotionMovie plays (InsertStart animation)
    Status: COMPLETED (operator-forced close at 02:37:33)
    
16. Card-based gameplay blocked
    Status: BLOCKED_BY_NESYS_OFFLINE
```

## Dependency Summary

| Stage | Status | Blocker |
|-------|--------|---------|
| Bootstrap | COMPLETED | — |
| D3D11 | COMPLETED | — |
| Assets | COMPLETED | — |
| NESYS pipe | FAILED | No pipe exists |
| NESYS status | FAILED | Offline (CertError) |
| HTTP discovery | WORKING | — |
| TCP setup | INITIATED | Aborted by error state |
| TCP resolution | RESOLVED | Never connected |
| SystemDataCheck | FAILED | OpenKey missing + NESYS offline |
| Card play | BLOCKED | NESYS offline |
| Normal flow | NOT_REACHED | NESYS offline |
| Battle | NOT_IMPLEMENTED | — |

## TCP Connection State (G9-A)

### Key Findings

1. **Server ready ~3 min before game request** — startup race DISPROVEN
2. **HTTP matching succeeds** — server returns `{"ip_addr":"127.0.0.1:6666"}` with 200
3. **TCP address resolved** — `127.0.0.1:6666` resolved successfully
4. **TCP connection NEVER established** — error state aborts callback
5. **Root cause chain**: NESYS offline → OpenKey missing → SystemDataCheck error → bGameConnect never set → TCP aborted

### Classification

**`BGAMECONNECT_GATES_TCP_CONNECTION`**: The game-level `bGameConnect` flag gates TCP connection establishment. NESYS offline → OpenKey missing → SystemDataCheck error → bGameConnect remains false → TCP connection callback is aborted before completion.

## Root Cause

**NesysService.exe is not running** (exits with -1). Without NESYS:
1. No named pipe connection → NESYS offline
2. No OpenKey.json generated → SystemDataCheck fails
3. SystemDataCheck error state → bGameConnect never set
4. TCP connection aborted → no game traffic

## What Would Fix This

1. **Start NesysService.exe** with correct launcher/arguments/certificates
2. **Provide NESYS authentication** so OpenKey.json is generated
3. **Fix SystemDataCheck** to not gate TCP on NESYS (game-level bug)
4. **Fix bGameConnect restoration** after reconnection (game-level bug)

**Items 3-4 are game-level bugs that require source code access to fix.**
**Items 1-2 require the original cabinet launcher or equivalent startup context.**
