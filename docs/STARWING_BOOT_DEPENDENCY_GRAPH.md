# Starwing Paradox Boot Dependency Graph (Corrected)

## Date: 2026-08-27

## Correction Note (2026-08-28)

**RENDERING_CRASH_STATUS**: NOT_CONFIRMED_AS_SPONTANEOUS

The operator previously stated that the apparent game crash occurred when the operator forcibly closed the game. The rendering crash (FRCPassPostProcessAA::Process) is NOT confirmed as spontaneous. Do not classify as a current blocker.

**messageType 103 (0x67)**: CAPTURE_SEQUENCE_CANDIDATE — not proven as PingResponse.

**Current primary hypothesis**: First-connection startup timing / server readiness race.

## Boot Sequence

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
   
8. CertError reported
   Status: FAILED (NESYS offline)
   
9. Game continues in offline/testmode
   Status: COMPLETED (fallback to offline)
   
10. SystemDataCheck runs
    Detects NESYS offline
    Status: COMPLETED (error displayed)
    
11. "offline, cannot check" message displayed
    Status: COMPLETED (operator observes this)
    
12. Card-based gameplay blocked
    Status: BLOCKED_BY_NESYS_OFFLINE
    
13. PromotionMovie plays
    Status: COMPLETED
    
14. InsertStart widget visible
    Status: COMPLETED (but overlaid by NESYS error)
    
15. HTTP matching-server discovery
    Request: dev.starwing.jp/mock/matching/server
    Response: {"ip_addr":"127.0.0.1:6666"}
    Status: VERIFIED_WORKING
    
16. "Error No MatchingServer so initialize Nesys before."
    Status: COMPLETED (game requires NESYS first)
    
17. Normal title flow (menu, card, gameplay)
    Status: NOT_REACHED (blocked by NESYS offline)
```

## Dependency Summary

| Stage | Status | Blocker |
|-------|--------|---------|
| Bootstrap | COMPLETED | — |
| D3D11 | COMPLETED | — |
| Assets | COMPLETED | — |
| NESYS pipe | FAILED | No pipe exists |
| NESYS status | FAILED | Offline |
| SystemDataCheck | COMPLETED | Error shown |
| Card play | BLOCKED | NESYS offline |
| Normal flow | NOT_REACHED | NESYS offline |
| HTTP discovery | WORKING | — |
| Matching TCP | PARTIAL | First attempt fails (race condition), bGameConnect never restores |
| TCP ping/pong | WORKING | Transport level works after first failure |
| Battle | NOT_IMPLEMENTED | — |

## TCP Connection State (2026-08-28)

### Observed in Both Runs (Run A and Run B)

1. GameConnect:1 initially
2. HTTP POST matching/server → 200 → {"ip_addr":"127.0.0.1:6666"}
3. TCP #1: SetupConnect → Failed to post Ping (race condition)
4. GameConnect drops to 0, never restores
5. TCP #2+: Successful ping/pong at transport level
6. bGameConnect stays 0 despite WebServer Revived
7. SystemDataCheck detects offline → error
8. Crash on SL_Title (rendering bug)

### Key Finding

The first TCP attempt fails because the game sends a Ping before the TCP handshake completes. This sets GameConnect:0 permanently. Subsequent successful TCP connections never restore it.

### Discrepancy

Run B TCP server console showed zero connections, but game log shows TCP connections. Status: UNEXPLAINED.

## Root Cause
**NesysService.exe is not running.** The game's NESYS client plugin attempts to connect to a named pipe that does not exist. Without NESYS initialization, the game stays in offline mode permanently. Additionally, the game's TCP client has a race condition where the first connection attempt fails, and bGameConnect never restores even after successful reconnection.

## What Would Fix This
1. Mount D: drive with correct directory structure
2. Start NesysService.exe with correct launcher/arguments
3. Configure valid NESYS certificates
4. Configure correct registry keys
5. Provide network access to TAITO NESYS servers
6. Fix the TCP race condition (game-level bug)
7. Fix bGameConnect restoration after reconnection (game-level bug)

**Items 6-7 are game-level bugs that require source code access to fix.**
**Items 1-5 require the original cabinet launcher or equivalent startup context.**
