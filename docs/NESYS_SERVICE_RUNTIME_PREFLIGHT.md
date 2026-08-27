# NesysService Runtime Preflight

## Binary Properties

| Property | Value |
|----------|-------|
| Path | `X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe` |
| Size | 548,352 bytes |
| SHA-256 | `3a968f29b12050dd1b3ae7a8acfe48bf98f1e6e11b0e090d3eb4b5a05b51d76f` |
| Architecture | x64 |
| Subsystem | Windows Console (3) |
| Linker | MSVC |

## Imports

| DLL | Key Functions |
|-----|---------------|
| ADVAPI32.dll | CryptAcquireContextA, CryptCreateHash, CryptEnumProvidersA, CryptDeriveKey |
| WINHTTP.dll | WinHttpOpen, WinHttpConnect, WinHttpOpenRequest, WinHttpSendRequest, WinHttpReceiveResponse |
| CRYPT32.dll | CertOpenStore, CertFindCertificateInStore, CertGetNameStringA |
| WS2_32.dll | socket, gethostbyname, inet_addr, recvfrom, sendto |
| IPHLPAPI.DLL | GetAdaptersInfo, GetNetworkParams, GetIfTable |
| PSAPI.DLL | EnumProcesses, GetProcessMemoryInfo |
| KERNEL32.dll | HeapCreate, GetStartupInfoA, GetEnvironmentStringsW |
| USER32.dll | GetProcessWindowStation, ExitWindowsEx, MonitorFromPoint |
| GDI32.dll | CreateDCA, BitBlt, CreateCompatibleDC |

## Analysis

### What NesysService Does
1. **Console application** — runs in a command window
2. **WINHTTP client** — connects to `cert3.nesys.jp` (external NESYS server)
3. **Cryptographic operations** — uses ADVAPI32/CRYPT32 for certificate handling
4. **Socket operations** — uses WS2_32 for local network communication
5. **Network enumeration** — uses IPHLPAPI to query network adapters

### What NesysService Needs
- **No sibling DLLs** — all imports are system DLLs
- **No D: drive access** — no D: references found in binary
- **No command-line arguments** — no evidence of argument parsing
- **No service registration** — no SCM APIs imported
- **Working directory** — likely `X:\StarwingParadox\D DRIVE CONTENTS\system\Service\`

### Port Behavior
- Port 6666: 1 occurrence (likely local listener)
- Port 4000: 5 occurrences (possibly client connection)
- Port 4001: 0 occurrences

## Safe Preflight Status

**SAFE_FOR_SHORT_PROCESS_OBSERVATION**

Rationale:
- Console application (no GUI, no service registration)
- No admin elevation required
- No D: drive dependency
- No sibling DLLs needed
- Can be observed for 30 seconds without risk
- Can be stopped with taskkill

## Required Working Directory

```
X:\StarwingParadox\D DRIVE CONTENTS\system\Service
```

## Command Line

No arguments — launch bare:
```
X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe
```
