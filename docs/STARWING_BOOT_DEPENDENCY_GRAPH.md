# Starwing Boot Dependency Graph

## Boot Sequence

| Step | Dependency | Status | Evidence |
|------|------------|--------|----------|
| 1. Bootstrap launch | User action | COMPLETED | AcrGame.exe started |
| 2. Shipping process launch | Bootstrap creates | COMPLETED | AcrGame-Win64-Shipping.exe spawned |
| 3. D3D11 renderer init | Shipping process | COMPLETED | RTX 5090, 1920x1080 |
| 4. NESYS plugin init | Shipping process | COMPLETED | NesysClientPlugin loaded at frame 2 |
| 5. NESYS service detection | NesysService running | FAILED | NesysService not started |
| 6. Pipe creation | NesysService | NOT_STARTED | No pipe server created |
| 7. Pipe connection | Game client → pipe | NOT_STARTED | No pipe to connect to |
| 8. NESYS initialization | Pipe connected | COMPLETED (partial) | Setup Completed at frame 2 |
| 9. Certificate status | NESYS server | FAILED | CertError (status[4]) |
| 10. CertError retry loop | Certificate failure | COMPLETED | 7557 retries, frames 4-560 |
| 11. Asset preloading | Independent of NESYS | COMPLETED | Reached title screen |
| 12. Title screen load | Assets loaded | COMPLETED | SL_Title activated at frame 909 |
| 13. OpenKey load | D: drive | FAILED | LoadKeyFile error |
| 14. NESYS event check | OpenKey | FAILED | NESYS Event error |
| 15. Game-server init | NESYS + OpenKey | NOT_STARTED | Blocked by NESYS stage |
| 16. Port-4001 connection | Game-server init | NOT_STARTED | BLOCKED_BY_PREVIOUS_STAGE |
| 17. Rendering | Title screen | FAILED | EXCEPTION_ACCESS_VIOLATION |

## Key Findings

1. **CertError is NOT blocking** — Game progresses past CertError loop to title screen
2. **Asset preloading completes** — Given enough time (~3.5 min), all assets load
3. **D: drive failures are non-blocking** — Game boots without OpenKey.json
4. **Port 4001 is NOT reached** — Game never attempts HTTP connection to local server
5. **Crash is rendering-related** — Null pointer in post-process AA, not NESYS

## Status

**BOOT_PROGRESS_IMPROVED** — Game reached title screen despite NESYS failure.
