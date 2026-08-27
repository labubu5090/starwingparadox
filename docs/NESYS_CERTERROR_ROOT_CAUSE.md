# NESYS CertError Root Cause Analysis

## Log Evidence

| Timestamp | Frame | Event |
|-----------|-------|-------|
| 04.24.56.068 | 2 | `UCPP_NesysControl::Setup Completed` |
| 04.24.56.068 | 2 | `NetworkInitialize / InitNesys` |
| 04.24.56.069 | 2 | `NetworkInitialize / Setup Nesys complete` |
| 04.24.56.344 | 4 | `NesysControlErrorMessage / id[0] status[4] option[0]` |
| 04.24.56.344 | 4 | `UCPP_NesysControl::RequestNetworkInfo OK` |
| 04.24.56.344 | 4 | `UCPP_NesysControl::RequestNetworkInfo Error` |
| 04.24.56.344 | 4 | `ACPP_GameModeBoot::NesysRequest / RequestNetworkInfo` |
| 04.24.56.344 | 4 | `ACPP_GameModeBoot::NesysControlErrorMessage / ENesysNetworkServerMessage[CertError]` |

## Pattern

The loop repeats every ~16ms (60fps):
1. `NesysControlErrorMessage / id[0] status[4] option[0]`
2. `RequestNetworkInfo OK`
3. `RequestNetworkInfo Error`
4. `ENesysNetworkServerMessage[CertError]`

## NesysService Binary Analysis

| Property | Value |
|----------|-------|
| Architecture | x64 (not x86) |
| Subsystem | Windows Console (3) |
| Size | 548,352 bytes |
| Sibling DLLs | None required |
| External endpoint | `cert3.nesys.jp` |
| WINHTTP imports | WinHttpOpen, WinHttpConnect, WinHttpOpenRequest, etc. |
| CRYPT32 imports | CertOpenStore, CertFindCertificateInStore, etc. |
| WS2_32 imports | socket, recvfrom, sendto, gethostbyname, inet_addr |
| Port 6666 in binary | 1 occurrence (uint16) |
| Port 4000 in binary | 5 occurrences (uint16, in code sections) |
| Port 4001 in binary | 0 occurrences |

## Analysis

1. **NESYS plugin initialized** at t=2s (NesysClient UE4 plugin)
2. **NesysService was NOT started** by bootstrap
3. **Game attempted NESYS connection** at t=4s
4. **status[4]** = application-level error code from NESYS protocol
5. **CertError** = `ENesysNetworkServerMessage[CertError]` — an enum value in the game's NESYS protocol
6. **cert3.nesys.jp** = external NESYS certificate/authentication server
7. The game expects NesysService to be running locally, connecting to cert3.nesys.jp on behalf of the game

## Classification

**LOCAL_SERVICE_NOT_RUNNING**

The CertError occurs because:
- NesysService.exe was never started by the bootstrap
- The game's NESYS plugin tries to connect to a local NESYS service
- Without the service, the connection fails
- The error code `status[4]` maps to `CertError` in the game's enum
- This is NOT a TLS certificate validation failure
- This is NOT an external endpoint failure
- This is an application-level status code indicating the local NESYS service is unavailable

## Evidence

- NESYS setup completes (plugin loads)
- First error at t=4s (2s after setup)
- Error repeats at render framerate (~39/sec)
- No NesysService.exe process exists
- No port 6666 listener exists
- Game did not attempt connection to port 4001 or 4000
