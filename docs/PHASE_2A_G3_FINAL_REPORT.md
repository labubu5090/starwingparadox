# Phase 2A-G3 Final Report

## 1. Phase Status

**NO_CHANGE_FROM_G2** — Game behavior identical to G2. NesysService never started. CertError loop continues. Port alignment corrected but game did not connect to local ports.

## 2. Initial Git Baseline

| Item | Value |
|------|-------|
| HEAD | `9dabca9` |
| Branch | master |
| Working tree | Clean |

## 3. G2 Runtime Evidence

| Item | Value |
|------|-------|
| Bootstrap launched | Yes |
| Shipping launched | Yes |
| NesysService started | No |
| CertErrors | 5131 in ~130s |
| External connection | 44.213.205.183:443 |
| Asset preload | 5132/7553 |

## 4. AppData Runtime Files

13 files created by G2 run. All under `AppData\Local\AcrGame\Saved\`. No sensitive content. No CertError references in config files. AcrGame.log contains 5131 CertError lines.

## 5. CertError Source

| Property | Value |
|----------|-------|
| First occurrence | t=4s after launch (frame 4) |
| NESYS setup | Completed at t=2s (frame 2) |
| Frequency | ~39 per second (60fps render loop) |
| Pattern | `RequestNetworkInfo OK` → `RequestNetworkInfo Error` → `CertError` |
| Process | AcrGame-Win64-Shipping.exe |
| External endpoint | cert3.nesys.jp |

## 6. CertError Classification

**LOCAL_SERVICE_NOT_RUNNING**

The CertError is an application-level status code (`ENesysNetworkServerMessage[CertError]`, status[4]) indicating the local NESYS service is unavailable. It is NOT a TLS certificate validation failure.

## 7. Game Runtime Port Profile

| Port | Protocol | Owner | Status |
|------|----------|-------|--------|
| 4001 | HTTP | Python server | CORRECTED — now aligned |
| 6666 | Named pipe | NesysService.exe | CORRECTED — pipe IPC, not TCP |
| 4000 | HTTP | Unknown/WebAPI | NOT IMPLEMENTED — not needed for boot |
| 8000 | HTTP | Dev server | Not game-facing |

## 8. Port 4000 Ownership

**UNUSED_IN_OBSERVED_BOOT**

Game did not connect to port 4000 during either G2 or G3 runs. NesysService binary has 5 uint16 refs to 4000 in code sections. May be needed for web API in later boot stages.

## 9. Port 4001 Ownership

**PYTHON_HTTP_SERVER**

| Property | Value |
|----------|-------|
| Expected listener | Python FastAPI server |
| Expected client | AcrGame-Win64-Shipping.exe |
| Protocol | HTTP |
| Evidence | Game config `GameServerPort=4001` |
| Confidence | HIGH |
| Implementation | Running on 127.0.0.1:4001 |

## 10. Port 6666 Ownership

**NESYS_SERVICE (Named Pipe, not TCP)**

| Property | Value |
|----------|-------|
| Expected listener | NesysService.exe |
| IPC method | Named pipe `\\.\pipe\nesys_games\...` |
| Protocol | Custom NESYS protocol |
| Evidence | Binary analysis (CreateNamedPipeA, ConnectNamedPipe) |
| Confidence | HIGH |
| Implementation | NesysService exits immediately when standalone |

## 11. NesysService Preflight

**SAFE_FOR_SHORT_PROCESS_OBSERVATION** — But exits immediately with code -1 when run standalone.

## 12. NesysService Launch

| Property | Value |
|----------|-------|
| PID | 7204 |
| Exit code | 0xFFFFFFFF (-1) |
| Runtime | < 1 second |
| Listeners | None |
| Connections | None |
| Files written | None |

## 13. NesysService Process State

**EXITED** — Process terminated immediately after launch.

## 14. NesysService Listeners

None created.

## 15. NesysService Connections

None established.

## 16. NesysService File Writes

None detected.

## 17. Python HTTP Server

| Property | Value |
|----------|-------|
| Port | 4001 |
| Host | 127.0.0.1 |
| Status | Running |
| /health | OK |
| /ready | OK |

## 18. Python TCP Server

Not started (NesysService uses named pipes, not TCP).

## 19. Full Launch Order

1. Python HTTP server started on 127.0.0.1:4001
2. AcrGame.exe launched (bootstrap)
3. AcrGame-Win64-Shipping.exe spawned by bootstrap
4. D3D11 renderer initialized
5. NESYS plugin initialized (t=2s)
6. CertError loop began (t=4s)
7. Asset preloading continued
8. External HTTPS connection to cert3.nesys.jp
9. Process killed at t=120s

## 20. AcrGame Result

Launched successfully. PID 27960.

## 21. Shipping Game Result

Launched automatically. PID 38472. D3D11 rendering active.

## 22. Asset Preload Result

Progressing but blocked by NESYS retry loop consuming CPU cycles.

## 23. Local Connections

**None** — Game did not connect to port 4001, 6666, or 4000.

## 24. External Connections

| Destination | Port | Process |
|-------------|------|---------|
| 100.25.160.95 | 443 | AcrGame-Win64-Shipping.exe |

## 25. CertError After NesysService

NesysService was not running. CertError continued.

## 26. Boot Progress Comparison

| Metric | G2 | G3 |
|--------|-----|-----|
| NesysService started | No | No |
| CertErrors | 5131 | ~1200 (120s) |
| Server connections | 0 | 0 |
| Boot state | CertError loop | CertError loop |
| Progress | NONE | NONE |

## 27. D Drive Result

D: drive absent. No workaround applied.

## 28. Input Result

**BLOCKED_BY_BOOT_STATE** — Game stuck in CertError loop, not accepting input.

## 29. Security Boundaries Preserved

| Boundary | Status |
|----------|--------|
| No certificate bypass | PASS |
| No key extraction | PASS |
| No binary patching | PASS |
| No D: mapping | PASS |
| No registry modification | PASS |
| No service installation | PASS |
| No DNS/hosts modification | PASS |
| No firewall modification | PASS |
| No port-4000 fake service | PASS |
| Matching guarded | PASS |
| Battle guarded | PASS |

## 30. Tests

No Python code changes. Existing tests not re-run (no modifications).

## 31. Ruff

Not run (no Python changes).

## 32. Mypy

Not run (no Python changes).

## 33. Files Created

| File | Purpose |
|------|---------|
| `docs/PHASE_2A_G3_INITIAL_BASELINE.md` | Baseline |
| `docs/G2_APPDATA_RUNTIME_AUDIT.md` | AppData audit |
| `docs/NESYS_CERTERROR_ROOT_CAUSE.md` | CertError analysis |
| `docs/STARWING_PORT_OWNERSHIP.md` | Port ownership |
| `docs/NESYS_SERVICE_RUNTIME_PREFLIGHT.md` | NesysService preflight |
| `docs/NESYS_SERVICE_RUNTIME_RESULT.md` | NesysService result |
| `docs/GAME_EXTERNAL_CONNECTION_AUDIT.md` | External connections |
| `docs/PHASE_2A_G3_FINAL_REPORT.md` | This report |
| `config/game-runtime.local.example.env` | Port-aligned config |
| `tools/game/start-game-server.ps1` | Server start |
| `tools/game/stop-game-server.ps1` | Server stop |
| `tools/game/verify-game-server.ps1` | Server verify |
| `docs/generated/nesys_service_runtime_observation.json` | Nesys observation |
| `docs/generated/phase_2a_g3_full_launch_observation.json` | Full launch |

## 34. Files Modified

| File | Change |
|------|--------|
| `docs/CURRENT_CONTROL_MAPPING.md` | Added G2 runtime observation section |

## 35. Original Game Files Changed

**None.**

## 36. Commands Actually Executed

| Command | Purpose |
|---------|--------|
| `AcrGame.exe` | Bootstrap launch |
| `NesysService.exe` | Isolated observation |
| `taskkill /PID` | Process termination |
| `uvicorn app.main:app --port 4001` | Game runtime HTTP server |
| `Invoke-RestMethod` | Health checks |
| `Get-NetTCPConnection` | Port monitoring |
| `Get-Process` | Process monitoring |

## 37. Commands Not Executed

| Command | Reason |
|---------|--------|
| Certificate bypass | Security boundary |
| Key extraction | Security boundary |
| Binary patching | Security boundary |
| D: drive mapping | D: absent |
| Port 4000 implementation | Not needed for boot |
| NesysService with arguments | No evidence of required args |

## 38. Remaining Unknowns

1. **NesysService command-line arguments** — Unknown what args the game passes
2. **NesysService startup requirements** — Exits immediately when standalone
3. **Port 4000 purpose** — May be web API for later boot stages
4. **Named pipe protocol** — Exact message format unknown
5. **Game connection to port 4001** — Game never connected even with server running
6. **Asset preload completion** — Never reached 7553/7553

## 39. Git Commit

To be committed after documentation complete.

## 40. Recommended Next Action

1. **Investigate why game doesn't connect to port 4001** — The game config says GameServerPort=4001 but never connects
2. **Try launching NesysService with the game** — Start both simultaneously and observe pipe connection
3. **Capture named pipe traffic** — Use Process Monitor to trace pipe communication
4. **Extend observation to completion** — Allow asset preloading to finish (may take >5 minutes)
5. **Implement minimal NESYS stub** — Create a named pipe server that responds to basic NESYS protocol
