# Phase 2A-G22 Final Report: Cold-Start Runtime Capture

**Classification:** `RUNTIME_PATH_OBSERVED_COLD_START_CAPTURED`  
**Date:** 2026-08-29  
**Commit:** Pending (single commit after all gates pass)

## Executive Summary

G22 completed a full cold-start capture of Starwing Paradox, observing the complete boot sequence from before launcher execution through asset preloading. Two critical corrections to G21 findings were identified:

1. **Port 5233 is OpenCode, not the Python server** — The health checks observed in G21 were hitting the OpenCode desktop application's health endpoint, not a Starwing game service.

2. **Port 1042 is NesysService** — The game launcher connects to `localhost:1042` (NesysService) for certificate validation. Without NesysService running, the game cannot authenticate and enters a retry loop.

## Key Findings

### Cold-Start Timeline
| Time | Event |
|------|-------|
| T+0.0s | Capture started (pre-launch) |
| T+0.4s | Launcher begins port 1042 connection attempts |
| T+1.0s | Shipping process launched (PID 45844) |
| T+0.4-23.6s | Port 1042 retries (all RST, NesysService not running) |
| T+16.3s | HTTP OPTIONS+GET /api/health → 204 + 200 `{"healthy":true}` |
| T+55s | External TCP connection to 100.30.30.137:443 (AWS EC2) |
| T+76.3s | Second HTTP health check (same pattern) |
| T+78s | SSDP M-SEARCH from all interfaces |

### Port Analysis
| Port | Owner | Purpose | Status |
|------|-------|---------|--------|
| 1042 | NesysService | Cabinet service controller | NOT RUNNING (all RST) |
| 5233 | OpenCode (PID 40956) | Health check endpoint | RUNNING (not game server) |
| 7777 | Game (UE4 IpNetDriver) | Multiplayer networking | LISTENING |
| 4001 | Python server | app_port | NOT RUNNING |
| 6666 | Python server | pb_port | NOT RUNNING |

### NesysService Certificate Validation
The game log reveals a repeating pattern:
```
NesysControlErrorMessage / id[0] status[4] option[0]
UCPP_NesysControl::RequestNetworkInfo OK.
UCPP_NesysControl::RequestNetworkInfo Error.
NesysRequest / RequestNetworkInfo
NesysControlErrorMessage / ENesysNetworkServerMessage[CertError]
```
This pattern occurs **4,575 times** over 77 seconds before the game gives up.

### External Server
- **IP:** 100.30.30.137
- **Reverse DNS:** ec2-100-30-30-137.compute-1.amazonaws.com
- **Protocol:** TLS/HTTPS (port 443)
- **First seen:** T+55s after launch

### Local Cache
- **AppData:** `C:\Users\KAHO\AppData\Local\AcrGame`
- **Config files:** Engine.ini, GameUserSettings.ini
- **Save games:** SlotNumber.sav (717 bytes), PlayerData1.sav (MISSING)
- **Crash reports:** 8 crash reports from Aug 27-29, 2026
- **Game log:** 74,693 lines, 10.5MB

## G21 Corrections

### Pipe Interpretation
- **Previous:** `PIPE_NOT_REQUIRED_FOR_HTTP_STARTUP` confirmed
- **Corrected:** `PIPE_REQUIREMENT_UNRESOLVED`
- **Reason:** Wireshark cannot observe Windows named-pipe traffic

### Health Check Origin
- **Previous:** Health check hits Python server on port 5233
- **Corrected:** Health check hits OpenCode server on port 5233
- **Reason:** Port 5233 is owned by OpenCode, not the Python server

## Evidence Files

| File | Description |
|------|-------------|
| `tools/wireshark_g22/captures/g22_coldstart.pcapng` | 13.9MB capture file |
| `artifacts/phase_2a_g22/runtime_events.json` | Complete runtime event timeline |
| `artifacts/phase_2a_g22/port_function_correlation.json` | Port-to-function mapping |
| `artifacts/phase_2a_g22/http_health_check_origin.json` | Health check origin analysis |
| `artifacts/phase_2a_g22/local_cache_assessment.json` | Local cache and config analysis |
| `artifacts/phase_2a_g22/safety_report.json` | Binary integrity verification |
| `artifacts/phase_2a_g22/final_classification.json` | Final classification and corrections |

## Remaining Uncertainties

1. **Named pipe traffic** not observable via Wireshark (requires internal monitoring)
2. **NesysService protocol** not captured (service not running)
3. **External HTTPS traffic** not captured on loopback (requires physical interface capture)
4. **Full HTTP API contract** not captured (NesysService required for authentication)

## Recommendations for G23

1. Start NesysService to capture full authentication flow
2. Capture on physical interface to observe external HTTPS traffic
3. Use API hooking or ETW to capture named pipe traffic
4. Analyze NesysService binary for protocol details
