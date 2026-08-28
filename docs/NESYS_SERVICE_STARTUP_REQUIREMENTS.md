# NesysService Startup Requirements

## Date: 2026-08-28

## Binary Analysis Results

### Identity
- **Name**: NesysService
- **Version**: 2.97
- **Company**: TAITO Corporation
- **Built**: (x64) 2017/11/07
- **PDB**: `C:\alienbrainWork\all_development_solution\NESYS_support\NESiCAxLive\NesysService\bin\Release(NESYS_Game_cert3)\NesysServiceCert_x64.pdb`
- **Size**: 548,352 bytes
- **SHA-256**: `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F`

### Named Pipe Interface
- **Pipe prefix**: `\\.\pipe\`
- **Pipe name format**: `\\.\pipe\nesys_games\%s%s` (two variable components, likely company ID + game ID)
- **Server side**: NesysService creates the pipe via `CreateNamedPipeA`
- **Client side**: AcrGame connects via `ConnectNamedPipe` (NesysClient plugin)

### API Commands (LCOMMAND / SCOMMAND protocol)
The pipe protocol uses command pairs (LCOMMAND = game-to-service request, SCOMMAND = service-to-game reply):

- `LCOMMAND_CLIENT_START` / `SCOMMAND_CLIENT_END` — Client lifecycle
- `LCOMMAND_GAME_START_REQUEST` — Game start request
- `LCOMMAND_GAME_FREE_START_REQUEST` — Free play start
- `LCOMMAND_GAMESTATUS_RESET_REQUEST` / `SCOMMAND_GAMESTATUS_RESET_REPLY`
- `LCOMMAND_ROW_EVENTDATA_LIST_REQUEST` / `SCOMMAND_ROW_EVENTDATA_LIST_REPLY`
- `SCOMMAND_SHOPPING` — Shopping data

### External Service Endpoints
| Host | Protocol | Purpose |
|------|----------|---------|
| `cert3.nesys.jp` | HTTPS | Certificate/authentication |
| `data.nesys.jp` | HTTP | Data downloads |
| `nesys.taito.co.jp` | HTTP | Alive check (`/alive/%d/%s`) |
| `proxy.nesys.jp` | HTTPS | Proxy (`proxy.php?url=...`) |
| `fjm170920zero.nesica.net` | HTTPS | NESICA card service |
| Various | HTTPS | Service endpoints (`/service/card/`, `/service/incom/`, `/service/respone/`, `/service/upload/`) |

### HTTP Endpoints
- `certify.php` — Certificate verification
- `incom.php`, `incomALL.php` — Incoming data
- `shop.php` — Shop data
- `respone.php` — Response handling
- `Alive.txt` — Liveness check

### Windows APIs Used
| Category | Functions |
|----------|-----------|
| Named pipes | `CreateNamedPipeA`, `ConnectNamedPipe`, `DisconnectNamedPipe`, `PeekNamedPipe`, `SetNamedPipeHandleState`, `WaitNamedPipeA` |
| Certificate store | `CertOpenStore`, `CertFindCertificateInStore`, `CertCloseStore`, `CertFreeCertificateContext`, `CertGetNameStringA` |
| HTTP | `WinHttpOpen`, `WinHttpConnect`, `WinHttpOpenRequest`, `WinHttpSendRequest`, `WinHttpReceiveResponse`, `WinHttpReadData`, `WinHttpSetCredentials`, `WinHttpSetTimeouts` |
| Registry | `RegOpenKeyExA`, `RegQueryValueExA` |
| Files | `FindFirstFileA`, `GetModuleFileNameA` |
| Threads | `_beginthreadex` |

### Exit Behavior
- **Exit code**: -1 (0xFFFFFFFF)
- **Exit timing**: Immediate (within <1 second of launch)
- **Cause**: Missing required context — no named pipe server expected, no D: drive paths accessible, no parent process context

### Why NesysService Exits Immediately
NesysService.exe expects to be launched as part of a cabinet environment where:
1. A launcher/startup script starts it with specific command-line arguments
2. The D: drive exists with required directory structure
3. Windows certificate store contains valid NESYS certificates
4. Registry keys contain machine-specific configuration
5. A parent process manages its lifecycle

Without these, the service cannot initialize and exits immediately with code -1.

## Required D: Drive Structure
The game binary hardcodes paths to D: drive:

```
D:\Saved\ACRSaved\SaveData\OpenKey.json
D:\Saved\ACRSaved\SaveData\SaveData.json
D:\Saved\ACRSaved\Ranking\RankingData.json
D:\Saved\ACRSaved\Debug\DebugSetting.json
D:\Saved\ACRSaved\TestMode\NesicaTime\NesicaTime.json
D:\Saved\ACRSaved\TestMode\System\System.json
D:\Saved\ACRSaved\TestMode\Game\Game.json
D:\system\DUA\event\system_management_*.json
```

**D: drive does not exist on this system.** No D: drive is mounted, no junction point exists.

## Current System State
- **D: drive**: NOT MOUNTED (does not exist)
- **NesysService**: NOT RUNNING (exits immediately)
- **Named pipe**: DOES NOT EXIST (`\\.\pipe\nesys_games\...`)
- **Certificate store**: No NESYS certificates
- **Registry**: No NESYS configuration
- **Result**: Game stays in offline mode permanently

## Boot Dependency Chain (Corrected)
```
AcrGame.exe starts
  → NESYS client plugin initializes
  → Attempts to connect to named pipe: \\.\pipe\nesys_games\...
  → Pipe does not exist (NesysService not running)
  → NESYS status: offline (Nesys:0)
  → CertError reported
  → Game continues in offline mode
  → SystemDataCheck runs, detects NESYS offline
  → Displays "offline, cannot check" message
  → Card-based gameplay unavailable
  → Game remains at offline screen
```

## What Would Be Needed for NesysService to Work
1. D: drive mounted with correct directory structure
2. NesysService.exe launched with correct arguments by a launcher process
3. Valid NESYS certificates in Windows certificate store
4. Correct registry keys for machine configuration
5. Network access to cert3.nesys.jp (external TAITO servers)
6. Parent process managing service lifecycle

## G12 Findings (2026-08-28)

### Operator-Owned Content Analysis

| Finding | Detail |
|---------|--------|
| Executables found | 3 (AcrGame.exe, AcrGame-Win64-Shipping.exe, NesysService.exe) |
| Script files found | 0 (.bat, .cmd, .lnk, .reg, .vbs, .ps1) |
| Launcher candidates | NOT_FOUND |
| System drive backup | D_DRIVE_ONLY_BACKUP |
| NesysService standalone | PARENT_CONTEXT_REQUIRED |
| Safe launch test | PARTIAL_INVOCATION_NOT_SAFE_TO_TEST |

### NesysService Binary Evidence

| Component | Evidence | Strength |
|-----------|----------|----------|
| Service Control | StartServiceCtrlDispatcherA, RegisterServiceCtrlHandlerA, SetServiceStatus | CONFIRMED |
| Named Pipe | `\\.\pipe\nesys_games`, CreateNamedPipeA, ConnectNamedPipe | CONFIRMED |
| Certificate | CertOpenStore, CertFindCertificateInStore, cert3.nesys.jp | CONFIRMED |
| Network | WSACreateEvent, WSAEventSelect, URL patterns | CONFIRMED |
| Mutex | CreateMutexA, ReleaseMutex | CONFIRMED |
| Registry | RegOpenKeyExA | CONFIRMED |
| Process Creation | CreateProcessA, GenerateConsoleCtrlEvent | CONFIRMED |

### Missing Components

| Component | Status | Impact |
|-----------|--------|--------|
| Launcher executable | MISSING | Cannot determine startup sequence |
| Service registration | MISSING | NesysService not registered |
| Certificate store | MISSING | Cannot authenticate with NESYS |
| Registry | MISSING | Cannot read configuration |
| Startup shortcuts | MISSING | No startup folder placement |
| Scheduled tasks | MISSING | No task scheduler entries |
| Watchdog | MISSING | No crash recovery |
| Environment variables | MISSING | Cannot configure NESYS |

### Conclusion

The operator-owned content is a D-drive only backup. The original Windows system drive, launcher, startup configuration, certificate store, registry, and Windows Service configuration are missing.

**Classification**: `D_DRIVE_ONLY_BACKUP_CONFIRMED`

**The NESYS offline block cannot be resolved with the available content.**

**None of these are present on this system.**
