# Phase 2A-G19 Initial Baseline

## Status

**Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

## Baseline Verification

### Test Suite

- **Full suite:** 1056 passed, 1 skipped, 0 failed
- **Clean-room subset:** 222 passed, 0 failed
- **G17 contribution:** 974 tests
- **G18 contribution:** 82 tests (222 − 140 G17)
- **Non-cleanroom tests:** 835 (1057 − 222)

### Git State

- **HEAD:** ca5515b (Phase 2A-G18: Evidence-Locked Codec and Deterministic Session Harness)
- **Working tree:** Clean
- **Branch:** master

### Quality Gates

- **Ruff:** All checks passed
- **Mypy:** 0 errors, 80 source files (note: generated protobuf file has expected import-untyped warning)

### Recovery Audit Note (G19 completion)

During G19 completion (interruption recovery) the quality gates were re-run and recorded as
ACTUAL values:

- **Full suite:** 1056 passed, 1 skipped, 0 failed
- **Clean-room subset:** 222 passed, 0 failed
- **Ruff:** On re-run, `ruff check .` initially reported 2 `F401` unused-import errors in G18
  test files (`tests/unit/cleanroom/test_codec.py`, `tests/unit/cleanroom/test_invariants.py`).
  Both were removed via a narrow G18 correction (unused imports only; no behavior change).
  After the fix, Ruff reports **All checks passed**. The 2 files still pass (25 tests).
- **Mypy:** 0 errors, 80 source files
- **SHA-256 integrity:** all 6 artifacts verified MATCH (see § SHA-256)

### SHA-256 Integrity

| Executable | SHA-256 | Status |
|------------|---------|--------|
| NesysService.exe | 3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F | CONFIRMED UNCHANGED |
| AcrGame.exe | 97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C | CONFIRMED UNCHANGED |
| AcrGame-Win64-Shipping.exe | CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4 | CONFIRMED UNCHANGED |

### Newly Analyzed DLLs

| DLL | SHA-256 |
|-----|---------|
| GALAXYIO.dll | 47B4E1EDD13A7F94C74FF512C2CA705B0D9EEAF9C0355673452091BD882B9C92 |
| Lua524.dll | 5B8F9941F91C1C9683CF248A57C698496629524E5B2D031F05670C1DC23389C9 |
| QRreader.dll | C6DDFDF673919CE5C5B4D1393CB44B311A26D22ADDC695CFA49B44693FF99383 |

## IDA Analysis Summary

### Analysis Method

PE analysis using pefile library (IDA batch mode unavailable). Static analysis of:
- Import tables
- Export tables
- String extraction (ASCII and Unicode)
- Source code path extraction
- Pattern matching for game-specific protocols

### AcrGame-Win64-Shipping.exe Analysis

- **File size:** 163MB
- **Machine:** x86_64 (0x8664)
- **Sections:** 9 (.text, .rdata, .data, .pdata, .gfids, .rsrc, .reloc, + 2 more)
- **Imports:** 860 functions from 46 DLLs
- **Exports:** 347 functions
- **Strings:** 1,135,629 ASCII + 653,911 Unicode

### Key Import DLLs

| DLL | Functions | Purpose |
|-----|-----------|---------|
| KERNEL32.dll | 208 | Core Windows API (includes ConnectNamedPipe) |
| USER32.dll | 109 | Window management |
| WS2_32.dll | 42 | Raw TCP/UDP sockets |
| WININET.dll | 14 | HTTP client (IE-based) |
| WINHTTP.dll | 2 | Proxy configuration |
| CRYPT32.dll | 5 | Certificate handling |
| Lua524.dll | 39 | Lua scripting runtime |
| MSVCP140.dll | 81 | C++ runtime |

### GALAXYIO.dll Analysis

- **File size:** 154KB
- **Imports:** 104 functions from 5 DLLs
- **Exports:** 4 functions (GALAXYIO_Init, GALAXYIO_Update, GALAXYIO_GetStatus, GALAXYIO_Delete)
- **Key imports:** WinHTTP (11 functions), WinUSB (8 functions), KERNEL32 (79 functions)
- **Key strings:** `https://cert2.nesys.jp`, card endpoint URL

### AcrGame.exe Analysis

- **File size:** 161KB
- **Machine:** x86_64 (0x8664)
- **Purpose:** Launcher/wrapper
- **Key imports:** CreateProcessW, ShellExecuteExW, LoadLibraryW, GetProcAddress
- **Key behavior:** Launches AcrGame-Win64-Shipping.exe with command-line arguments

## Source Code Module Structure

### Game-Specific Modules (378 unique source paths)

| Module | Files | Purpose |
|--------|-------|---------|
| BattleModule | 151 | Battle system (actions, AI, characters) |
| NetworkModule | 17 | Network protocol, HTTP, sessions |
| HudModule | 15 | UI widgets (menus, displays) |
| OutGameModule | 11 | Out-of-game systems (matching, disconnect, read card) |
| SystemModule | 5 | Game viewport, reporting |
| CommonDataModule | 3 | Battle settings, error messages |
| ResidentModule | 2 | OpenKey check, error observation |
| USBIOModule | 1 | GALAXYIO wrapper |
| ControllerModule | 1 | Player controller |
| UserDataModule | 1 | Player profile |
| TestModeModule | 1 | Device test |

### Engine Modules

| Module | Files | Purpose |
|--------|-------|---------|
| Runtime | 114 | Core UE4 engine |
| OnlineSubsystemUtils | 16 | Online subsystem |
| Private | 17 | Online subsystem null |
| TcpMessaging | 3 | TCP messaging |
| UdpMessaging | 2 | UDP messaging |
| HTML5Networking | 3 | WebSocket |
| Wwise | 1 | Audio |

### Test Files

| File | Purpose |
|------|---------|
| CPP_TestNesys.cpp | NESYS protocol test |
| CPP_TestTCP.cpp | TCP protocol test |
| CPP_HttpMockTest.cpp | HTTP mock test |

## Network Protocol Discovery

### HTTP Endpoints (from string analysis)

- `BindHttpMatchingMatchIdGenerate` - Match ID generation
- `BindHttpMatchingServer` - Matching server connection
- `BindHttpFestResult` - Festival result submission
- `BindHttpGameDataSaveData` - Game data save
- `BindHttpErrorCallback` - Error handling
- `https://log.starwing.jp/acr/public/` - Logging endpoint
- `dev.starwing.jp/mock` - Mock server endpoint

### NESYS Protocol

- Named pipe: `\\.\pipe\nesys_games`
- Certificate: `https://cert2.nesys.jp`
- Card endpoint: `/service/card/amic.php?RC=%s&ID=%s&CKV=%s&WCNT=%s&MAC_A=%s&PAD0=%s`

### Matching Protocol

- HTTP-based matching (`BindHttpMatchingServer`)
- TCP-based battle (`CPP_TestTCP.cpp`)
- Reconnect logic (`RequestNesysReconnect`)

### Game Server Communication

- HTTP for game data and matching
- TCP for battle sessions
- Protobuf for message serialization

## Key Findings

### Pipe Client Evidence

- `\\.\pipe\` found in strings (1 match)
- `nesys_games` found in strings (1 match)
- `ConnectNamedPipe` imported (2 matches - ConnectNamedPipe, DisconnectNamedPipe)
- `SetNamedPipeHandleState` imported
- `PeekNamedPipe` imported
- `WaitNamedPipeA` imported

### Network Path Evidence

- WININET.dll for HTTP (14 functions)
- WINHTTP.dll for proxy config (2 functions)
- WS2_32.dll for raw sockets (42 functions)
- GALAXYIO.dll uses WinHTTP (11 functions) for HTTP

### Configuration Evidence

- `OpenKeyCheck.cpp` - OpenKey configuration check
- `Game.ini` - Game configuration (minimal)
- `option.txt` - Operator options (ScreenType, EWF, MemoryLog)
- `SaveData.json` - Master data manifest
- `test_mode_setting.json` - Test mode settings

## Classification Decision

**Selected Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

**Rationale:** Static analysis of the game executables and DLLs reveals:
1. Clear pipe client behavior for NESYS communication
2. HTTP endpoints for game data and matching
3. TCP for battle sessions
4. Protobuf for message serialization
5. Source code paths revealing module structure
6. Configuration files for operator control

The evidence is sufficient to proceed with implementing a private server that handles:
- Game startup and configuration
- Player/card session initialization
- HTTP-based game data and matching
- TCP-based battle sessions
- Result submission
- Error handling and reconnection

## Next Steps

1. Complete G19 documentation and artifacts
2. Implement private server based on discovered contracts
3. Test with game client
4. Validate end-to-end functionality
