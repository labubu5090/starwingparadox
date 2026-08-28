# GAME_CLIENT_EXECUTABLE_MODULE_MAP

## Status

**Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

## Source Modules (from binary debug strings)

### Private-Server-Relevant Modules

| Module | Files | Classification | Key files / role |
|--------|-------|----------------|------------------|
| NetworkModule | 17 | PRIVATE_SERVER_RELEVANT | AcrProtocol.cpp, CPP_Session.cpp, AcrGameSession.cpp, CPP_HttpRequester.cpp, CPP_HttpJsonSerialize.cpp, CPP_HttpFileDownload.cpp |
| OutGameModule | 11 | MATCHING_RELEVANT | CPP_MatchingMain.cpp, CPP_GameModeDisConnect.cpp |
| ResidentModule | 2 | STARTUP_CRITICAL | OpenKeyCheck.cpp, CPP_ErrorObserver.cpp |
| BattleModule | 151 | BATTLE_RELEVANT | Battle actors/actions/AI |
| CommonDataModule | 3 | OPTIONAL | ErrorMessageWork.cpp, battle settings |
| USBIOModule | 1 | LOCAL_IPC_RELEVANT | GALAXYMotionWrapper.cpp |
| UserDataModule | 1 | CARD_OR_PLAYER_RELEVANT | Player profile |

### Test Files (evidence-rich)

- `CPP_TestNesys.cpp` — NESYS pipe protocol tests
- `CPP_TestTCP.cpp` — TCP protocol tests
- `CPP_HttpMockTest.cpp` — HTTP mock tests (used by operator mock server)

## Executables and DLLs

### AcrGame-Win64-Shipping.exe (main game)

- **Size:** 163 MB (163,440,640 B), SHA-256 `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4`
- **Imports:** 860 funcs / 46 DLLs. Key: KERNEL32 (208, incl. pipe + `CreateProcessW`), WS2_32 (42, TCP), WININET (14, HTTP), WINHTTP (2, proxy config), CRYPT32 (5, certs), Lua524 (39).
- **Strings:** 1,135,629 ASCII + 653,911 Unicode.
- **Role:** Actually runs the Starwing game; hosts all HTTP/TCP/pipe/scripting and battle logic.

### AcrGame.exe (launcher)

- **Size:** 161,280 B, SHA-256 `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C`
- **Imports:** 81 funcs / 4 DLLs. Key: `CreateProcessW`, `ShellExecuteExW`, `LoadLibraryW`, `GetProcAddress`, `GetModuleFileNameW`.
- **Exports:** 0.
- **Role:** Thin launcher/wrapper. Locates and starts the Shipping build. Contains NO network protocol of its own.

### GALAXYIO.dll

- **Size:** 154,112 B, SHA-256 `47B4E1EDD13A7F94C74FF512C2CA705B0D9EEAF9C0355673452091BD882B9C92`
- **Exports:** 4 (`GALAXYIO_Init`, `GALAXYIO_Update`, `GALAXYIO_GetStatus`, `GALAXYIO_Delete`).
- **Imports:** WinHTTP (11, full HTTP client), WINUSB (8, USB I/O), SETUPAPI (4, device enumeration), KERNEL32 (79).
- **Role:** Card I/O layer. Contacts `https://cert2.nesys.jp` and the AMIC card endpoint. Uses WinHTTP + USB, NOT the named pipe.

### Lua524.dll

- **Size:** 231,936 B, SHA-256 `5B8F9941F91C1C9683CF248A57C698496629524E5B2D031F05670C1DC23389C9`
- **Exports:** 147 Lua API functions.
- **Role:** Lua 5.24 scripting runtime. OPTIONAL to private server.

### QRreader.dll

- **Size:** 770,048 B, SHA-256 `C6DDFDF673919CE5C5B4D1393CB44B311A26D22ADDC695CFA49B44693FF99383`
- **Exports:** 5 (`QRreader_Open` 1000, `QRreader_Close` 1001, `QRreader_GetState` 1002, `QRreader_GetBuffer` 1003, `QRreader_GetCode` 1004).
- **Role:** QR code reader for card scanning. CARD_OR_PLAYER_RELEVANT.

## Analysis Notes

- IDA headless was unavailable; analysis used pefile (imports/exports/sections/strings) only. RVAs not extracted.
- 378 unique source paths confirm module structure.
- The game's functionality is concentrated in the Shipping executable; AcrGame.exe is only a launcher.

## References

- `artifacts/phase_2a_g19/module_map.json`
- `tools/ida/pe_analysis_results.json`
- `tools/ida/source_paths.json`
