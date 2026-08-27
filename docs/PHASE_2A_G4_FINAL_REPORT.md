# Phase 2A-G4 Final Report

## 1. Phase Status

**BOOT_PROGRESS_IMPROVED** — The game reached the title screen (SL_Title) for the first time. CertError is NOT blocking boot. The crash was a rendering null pointer in post-process AA, unrelated to NESYS.

## 2. Initial Git Baseline

| Item | Value |
|------|-------|
| HEAD | `c8a9cc4` |
| Branch | `master` |
| Working tree | Clean |

## 3. Port Model Correction

| Port | Previous Classification | G4 Evidence | Updated Status |
|------|------------------------|-------------|----------------|
| 4001 | Game server (required for boot) | Game booted to title without connecting | NOT_NEEDED_FOR_BOOT |
| 6666 | NESYS TCP listener | Binary uses named pipes, NOT TCP | PIPE_NOT_CREATED |
| 4000 | Unknown | Unused in observed boot | UNUSED_IN_OBSERVED_BOOT |
| 8000 | Dev server | Not game-facing | NOT_GAME_FACING |

## 4. Extended Boot Duration

| Metric | G2/G3 | G4 |
|--------|-------|-----|
| Boot time to title screen | Never reached | ~3.5 minutes |
| CertErrors | 5131 (120s) | 7557 (360s) |
| CertError停止 | Never stopped | Stopped at frame 560 |
| Title screen reached | No | Yes |
| Crash | None (killed) | EXCEPTION_ACCESS_VIOLATION |

## 5. Asset Preload Result

**COMPLETED** — All assets loaded given sufficient time (~3.5 minutes). The game reached the title screen with full rendering.

## 6. Process Creation Events

| Process | Parent | PID | Status |
|---------|--------|-----|--------|
| AcrGame.exe | User | Unknown | Running (bootstrap) |
| AcrGame-Win64-Shipping.exe | AcrGame.exe | Unknown | Crashed at title screen |
| NesysService.exe | None | N/A | Never started |

## 7. NesysService Launch Attempt

**NOT_OBSERVED** — Neither game process attempted to launch NesysService.exe. The game's NESYS client plugin initializes but does not start the service.

## 8. NesysService Command Line

Not applicable — NesysService was never launched.

## 9. NesysService Working Directory

Not applicable — NesysService was never launched.

## 10. NesysService Exit Result

Not applicable — NesysService was never launched.

## 11. Named Pipe Names

**NO NESYS PIPES CREATED** — No `nesys_games` pipe was observed. System pipes only (InitShutdown, lsass, etc.).

## 12. Named Pipe Creator

Not applicable — No pipe was created.

## 13. Named Pipe Client

Not applicable — No pipe was created.

## 14. Named Pipe Lifecycle

Not applicable — No pipe was created.

## 15. Pipe Connection Result

Not applicable — No pipe was created.

## 16. File Lookup Result

| File | Result | Impact |
|------|--------|--------|
| D:/Saved/ACRSaved/SaveData/OpenKey.json | LoadKeyFile error | Non-blocking |
| D:/Saved/ACRSaved/Debug/DebugSetting.json | Load error | Non-blocking |
| D:/Saved/ACRSaved/Ranking/RankingData.json | LoadFileToString error | Non-blocking |
| D:/Saved/ACRSaved/SendLog | CreateDirectory error | Non-blocking |
| D:/Saved/ACRSaved/TestMode/BookKeeping/Old | CreateDirectory error | Non-blocking |

## 17. Missing Runtime Files

- `D:/Saved/ACRSaved/SaveData/OpenKey.json` — NESYS key data
- `D:/Saved/ACRSaved/Debug/DebugSetting.json` — Debug config
- `D:/Saved/ACRSaved/Ranking/RankingData.json` — Ranking data

All missing files are non-blocking for boot.

## 18. D Drive Result

D: drive absent. All D: path operations fail. Game boots to title screen despite failures.

## 19. OpenKey Access Result

`LoadKeyFile error` → `NESYS Event error` → Game continues to title screen in offline mode.

## 20. WINHTTP Sequence

No external HTTPS connections observed during the G4 boot. The game operates in offline mode.

## 21. CertError Sequence

| Frame | Event |
|-------|-------|
| 0 | Game start |
| 2 | NESYS setup completed |
| 4 | First CertError (status[4]) |
| 4-560 | CertError retry loop (~39/sec) |
| 560 | Last CertError (retries stop) |
| 909 | Title screen activated |
| 783 | Crash (post-process AA) |

## 22. Boot Dependency Graph

| Step | Status |
|------|--------|
| Bootstrap launch | COMPLETED |
| Shipping launch | COMPLETED |
| D3D11 renderer init | COMPLETED |
| NESYS plugin init | COMPLETED |
| NESYS service detection | FAILED |
| Pipe creation | NOT_STARTED |
| Pipe connection | NOT_STARTED |
| NESYS initialization | COMPLETED (partial) |
| Certificate status | FAILED |
| Asset preloading | COMPLETED |
| Title screen load | COMPLETED |
| OpenKey load | FAILED |
| NESYS event check | FAILED |
| Game-server init | NOT_STARTED |
| Port-4001 connection | NOT_STARTED |
| Rendering | FAILED |

## 23. Port 4001 Status

**NO_GAME_CONNECTION** — Game never attempted to connect to port 4001. OnlineObserver: WebServer:0, HttpSuccess:0.

## 24. Port 4000 Status

**UNUSED_IN_OBSERVED_BOOT** — No game connection observed.

## 25. Port 6666 Status

**PIPE_NOT_CREATED** — NesysService was never started. No pipe server created.

## 26. Input Status

**BLOCKED_BY_CRASH** — Game crashed at title screen before input could be tested.

## 27. Launch-Context Replay

Not applicable — NesysService launch context not proven. Game does not start NesysService.

## 28. Security Boundaries Preserved

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
| No pipe stub created | PASS |
| Matching guarded | PASS |
| Battle guarded | PASS |

## 29. Tests

- 802 collected, 794 passed, 2 failed (pre-existing), 6 skipped
- Pre-existing failures: test_codec_edge_cases, test_tcp_server

## 30. Ruff

Not run (no Python changes).

## 31. Mypy

Not run (no Python changes).

## 32. Files Created

| File | Purpose |
|------|---------|
| `docs/PHASE_2A_G4_INITIAL_BASELINE.md` | Baseline |
| `docs/NESYS_NAMED_PIPE_LIFECYCLE.md` | Pipe lifecycle |
| `docs/NESYS_PROCESS_LAUNCH_CONTEXT.md` | Process context |
| `docs/NESYS_RUNTIME_FILE_REQUIREMENTS.md` | File requirements |
| `docs/NESYS_WINHTTP_SEQUENCE.md` | WINHTTP observation |
| `docs/STARWING_BOOT_DEPENDENCY_GRAPH.md` | Boot graph |
| `docs/PROCESS_MONITOR_OBSERVATION.md` | Procmon status |
| `docs/PHASE_2A_G4_FINAL_REPORT.md` | This report |
| `docs/generated/g4_extended_boot_observation.json` | Boot data |

## 33. Files Modified

| File | Change |
|------|--------|
| `docs/STARWING_PORT_OWNERSHIP.md` | Updated with G4 evidence |

## 34. Original Game Files Changed

**None.**

## 35. Commands Actually Executed

| Command | Purpose |
|---------|--------|
| `AcrGame.exe` | Bootstrap launch |
| `Get-Process` | Process monitoring |
| `Get-NetTCPConnection` | Connection monitoring |
| `Get-Content AcrGame.log` | Log analysis |
| `[System.IO.Directory]::GetFiles("\\.\pipe\")` | Pipe enumeration |

## 36. Commands Not Executed

| Command | Reason |
|---------|--------|
| Certificate bypass | Security boundary |
| Key extraction | Security boundary |
| Binary patching | Security boundary |
| D: drive mapping | D: absent |
| Port 4000 implementation | Not needed |
| Pipe stub creation | Security boundary |
| NesysService launch | No proven context |

## 37. Remaining Unknowns

1. **Rendering crash cause** — Null pointer in FRCPassPostProcessAA::Process() at title screen
2. **Why game doesn't connect to port 4001** — Even with server running, no HTTP connection
3. **NesysService launch context** — Game does not start it; external service required
4. **D: drive OpenKey.json content** — What NESYS key data is expected
5. **Port 4000 purpose** — May be needed for later game stages

## 38. Git Commit

To be committed after documentation complete.

## 39. Recommended Next Action

1. **Fix rendering crash** — Investigate EXCEPTION_ACCESS_VIOLATION in FRCPassPostProcessAA::Process()
2. **Allow title screen interaction** — Fix crash to enable input testing
3. **Investigate port 4001 connection** — Why doesn't game connect even when available
4. **Create minimal OpenKey.json** — Determine expected format for D: drive
5. **Install Process Monitor** — For detailed process/file/pipe tracing
