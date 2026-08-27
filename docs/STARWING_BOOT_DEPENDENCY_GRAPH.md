# Starwing Paradox Boot Dependency Graph (Corrected)

## Date: 2026-08-27

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
| Matching TCP | NOT_STARTED | NESYS offline |
| Battle | NOT_IMPLEMENTED | — |

## Root Cause
**NesysService.exe is not running.** The game's NESYS client plugin attempts to connect to a named pipe that does not exist. Without NESYS initialization, the game stays in offline mode permanently.

## What Would Fix This
1. Mount D: drive with correct directory structure
2. Start NesysService.exe with correct launcher/arguments
3. Configure valid NESYS certificates
4. Configure correct registry keys
5. Provide network access to TAITO NESYS servers

**This requires the original cabinet launcher or equivalent startup context.**
