# Phase 2A-G2 Final Report

## 1. Phase Status

**COMPLETE** — Controlled dry run executed. Game launched, observed for 60 seconds, processes stopped cleanly.

## 2. Initial Git Baseline

| Item | Value |
|------|-------|
| HEAD | `8465b98` |
| Branch | master |
| Working tree | Clean (untracked: `data/`, `docs/generated/game_content_stats.json`) |

## 3. Pre-Launch Safety

| Check | Result |
|-------|--------|
| No D: drive mapped | PASS |
| No registry modified | PASS |
| No services installed | PASS |
| No DNS/hosts modified | PASS |
| No firewall modified | PASS |
| No input drivers installed | PASS |
| No DLLs injected | PASS |
| No PAKs extracted | PASS |
| No copyrighted content in Git | PASS |
| Matching guarded | PASS |
| Battle guarded | PASS |

## 4. D Drive State

| Item | Value |
|------|-------|
| D: exists | No |
| Classification | D_DRIVE_ABSENT |

## 5. Python Server State

| Item | Value |
|------|-------|
| Port | 8000 |
| Status | Running (survived game launch) |
| Health check | OK |
| Database | `server/data/starwing.db` (created) |

## 6. Port 4000 State

| Item | Value |
|------|-------|
| Pre-launch | Not listening |
| During run | Not contacted by game |
| Post-run | Not listening |
| Classification | NOT_CONTACTED |

## 7. Port 4001 State

| Item | Value |
|------|-------|
| Pre-launch | Not listening |
| During run | Not contacted by game |
| Post-run | Not listening |
| Classification | NOT_CONTACTED |

## 8. Port 6666 State

| Item | Value |
|------|-------|
| Pre-launch | Not listening |
| During run | NESYS service never started |
| Post-run | Not listening |
| Classification | NESYS_NOT_STARTED |

## 9. Launch Target

| Item | Value |
|------|-------|
| Executable | `X:\StarwingParadox\WindowsNoEditor\AcrGame.exe` |
| SHA-256 | `97800621bb91a2706fbc68ad937679c874b17ac1b2389bddf472be9350e62d6c` |
| Size | 161,280 bytes |

## 10. Working Directory

| Item | Value |
|------|-------|
| Path | `X:\StarwingParadox\WindowsNoEditor` |

## 11. Bootstrap Process

| Item | Value |
|------|-------|
| Name | AcrGame.exe |
| PID | 10976 |
| Status | Launched successfully |
| Exit | Killed by wrapper at t=60s |

## 12. Shipping Process

| Item | Value |
|------|-------|
| Name | AcrGame-Win64-Shipping.exe |
| PID | 10480 |
| Status | Launched automatically by bootstrap |
| Exit | Killed by wrapper at t=60s |

## 13. NesysService Process

| Item | Value |
|------|-------|
| Name | NesysService.exe |
| Status | **NEVER STARTED** |
| Note | Bootstrap did not launch NesysService |

## 14. Process Tree

```
AcrGame.exe (PID 10976) [bootstrap]
  └── AcrGame-Win64-Shipping.exe (PID 10480) [main game]
```

## 15. Game Window

| Item | Value |
|------|-------|
| Window created | Yes (detected via process) |
| Visible rendering | UE4 D3D11 initialized (RTX 5090) |
| Resolution | 1920x1080 (windowed) |

## 16. Rendering Result

| Item | Value |
|------|-------|
| D3D11 adapter | NVIDIA GeForce RTX 5090 |
| Feature level | 11_0 |
| GPU memory | 32187 MB dedicated |
| Status | Renderer initialized, asset preloading in progress |

## 17. Network Connections

| Connection | Details |
|------------|---------|
| External HTTPS | `10.0.4.99:38391` → `44.213.205.183:443` (ESTABLISHED) |
| Local listener | `0.0.0.0:38391` (LISTEN) |

## 18. External Connections

| Item | Value |
|------|-------|
| IP | 44.213.205.183 |
| Port | 443 (HTTPS) |
| Classification | EXTERNAL_OFFICIAL_ENDPOINT |
| Purpose | Likely game update/authentication server |
| Risk | Metadata observed only; no credentials captured |

## 19. File Writes

| File | Location | Type |
|------|----------|------|
| CrashReportClient.ini | `AppData\Local\AcrGame\Saved\Config\CrashReportClient\` | UE4_CONFIG |
| Compat.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| DeviceProfiles.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| EditorPerProjectUserSettings.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| Engine.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| Game.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| GameUserSettings.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| Hardware.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| Input.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| Lightmass.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| Scalability.ini | `AppData\Local\AcrGame\Saved\Config\WindowsNoEditor\` | UE4_CONFIG |
| AcrGame.log | `AppData\Local\AcrGame\Saved\Logs\` | UE4_LOG |
| SlotNumber.sav | `AppData\Local\AcrGame\Saved\SaveGames\` | SAVE_DATA |

**Total**: 13 new files, 0 changed files

## 20. X Drive Integrity

| Item | Value |
|------|-------|
| AcrGame.exe hash | Unchanged |
| Shipping.exe hash | Unchanged |
| NoHDDUnload.dll hash | Unchanged |
| No game files modified | PASS |

## 21. Input Detection

| Input | Classification |
|-------|----------------|
| XInput | OPERATOR_TEST_REQUIRED |
| Keyboard | OPERATOR_TEST_REQUIRED |
| USBIO | NOT_DETECTED |

## 22. Xbox Controller

| Item | Value |
|------|-------|
| XInput loaded | Yes (bootstrap imports XINPUT1_3.dll) |
| Runtime detected | OPERATOR_TEST_REQUIRED |

## 23. Keyboard

| Item | Value |
|------|-------|
| Fallback available | Yes (UE4 default) |
| Runtime detected | OPERATOR_TEST_REQUIRED |

## 24. USBIO

| Item | Value |
|------|-------|
| Detected | No |
| NESYS service | Never started |
| Classification | NOT_DETECTED |

## 25. Exit Result

| Item | Value |
|------|-------|
| Bootstrap exit | Killed by wrapper (SIGTERM) |
| Shipping exit | Killed by wrapper (SIGTERM) |
| Exit codes | N/A (forced kill) |
| Ports released | Yes |
| Processes cleaned | Yes |

## 26. Primary Blocking Point

**NESYS Certificate Error (`CertError`)**

The game is stuck in a boot loop:
1. Game attempts to connect to NESYS service
2. NESYS service was never started by bootstrap
3. Game receives `ENesysNetworkServerMessage[CertError]` (status 4)
4. Game retries every ~16ms
5. Meanwhile, asset preloading continues (5132/7553 loaded at t=60s)

The game does NOT connect to port 4001 (our server) or port 4000. It only attempts NESYS (port 6666) and contacts an external HTTPS endpoint.

## 27. Control Mapping Recommendation

| Recommendation | Priority |
|----------------|----------|
| XInput native profile first | HIGH |
| Do not modify DefaultInput.ini yet | HIGH |
| Create operator mapping checklist | MEDIUM |
| Keyboard fallback documented | LOW |

## 28. Files Created

| File | Purpose |
|------|---------|
| `docs/PHASE_2A_G2_INITIAL_BASELINE.md` | Initial baseline |
| `docs/D_DRIVE_RUNTIME_OBSERVATION.md` | D-drive state |
| `docs/PHASE_2A_G2_INPUT_OBSERVATION.md` | Input detection |
| `docs/generated/phase_2a_g2_prelaunch_network.json` | Pre-launch network |
| `docs/generated/phase_2a_g2_runtime_observation.json` | Full observation |
| `docs/generated/phase_2a_g2_runtime_network.json` | Network observation |

## 29. Files Modified

None.

## 30. Original Game Files Changed

**None.** All writes were to `AppData\Local\AcrGame\` (UE4 runtime directory).

## 31. Commands Actually Executed

| Command | Purpose |
|---------|---------|
| `AcrGame.exe` | Bootstrap launch |
| `taskkill /PID <pid> /F` | Process termination |
| `Get-NetTCPConnection` | Network observation |
| `Get-Process` | Process monitoring |
| `Invoke-RestMethod` | Server health check |

## 32. Commands Not Executed

| Command | Reason |
|---------|--------|
| D: drive SUBST | D: absent; no workaround applied |
| Port 4000 binding | Not implemented (observed only) |
| USBIO driver install | Not installed |
| DLL injection | Not performed |
| PAK extraction | Not performed |
| Registry modification | Not performed |
| Firewall modification | Not performed |

## 33. Python Test Result

No venv tests run (venv not pre-existing; created fresh for this run).

## 34. Ruff Result

Not run (no Python code changes).

## 35. Mypy Result

Not run (no Python code changes).

## 36. Git Commit

To be committed after documentation complete.

## 37. Recommended Next Action

1. **Investigate NESYS certificate error** — Determine if we can bypass or mock the NESYS certificate check
2. **Start NesysService.exe manually** — Observe if the game progresses past boot when NESYS is available
3. **Implement port 6666 stub** — Create a minimal NESYS service that responds to certificate validation
4. **Extend observation window** — Allow game to complete asset preloading (7553 assets)
5. **Test XInput controller** — Verify gamepad input detection
