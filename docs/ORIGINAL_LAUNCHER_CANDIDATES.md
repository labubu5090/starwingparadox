# Original Launcher Candidates

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executables Found

Only three executables exist in the operator-owned content:

### 1. AcrGame.exe

| Property | Value |
|----------|-------|
| Relative path | WindowsNoEditor\AcrGame.exe |
| SHA-256 | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` |
| Size | 161,280 bytes |
| Last write | 30/9/2020 8:54:04 |
| Classification | **GAME_EXECUTABLE** |
| Architecture | PE32+ (64-bit) |
| Product name | AcrGame |
| Company | Taito |
| PE subsystem | GUI |
| Signature | None verifiable |
| Imported process creation | CreateProcessW |
| NesysService reference | NONE |
| Launcher strings | NONE |
| Working directory strings | NONE |
| Service management APIs | NONE |
| Child process evidence | CreateProcessW (standard UE4 pattern) |

**Analysis**: This is the game launcher executable. It is NOT a custom launcher - it is the standard Unreal Engine 4 game executable that launches AcrGame-Win64-Shipping.exe.

### 2. AcrGame-Win64-Shipping.exe

| Property | Value |
|----------|-------|
| Relative path | WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe |
| SHA-256 | `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4` |
| Size | 163,119,104 bytes |
| Last write | 30/9/2020 8:56:12 |
| Classification | **GAME_EXECUTABLE** |
| Architecture | PE32+ (64-bit) |
| Product name | AcrGame |
| Company | Taito |
| PE subsystem | Windows subsystem |
| Signature | None verifiable |
| Imported process creation | Unknown (163MB - timeout on full scan) |
| NesysService reference | NONE (timeout) |
| Launcher strings | NONE (timeout) |
| Working directory strings | NONE (timeout) |
| Service management APIs | NONE (timeout) |
| Child process evidence | Unknown (timeout) |

**Analysis**: This is the main game shipping executable. It is the actual game binary that runs the Starwing Paradox game.

### 3. NesysService.exe

| Property | Value |
|----------|-------|
| Relative path | D DRIVE CONTENTS\system\Service\NesysService.exe |
| SHA-256 | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` |
| Size | 548,352 bytes |
| Last write | 23/3/2018 17:55:00 |
| Classification | **SUPPORT_SERVICE** |
| Architecture | PE32+ (64-bit) |
| Product name | NesysService |
| Company | Taito |
| PE subsystem | Console |
| Signature | None verifiable |
| Imported process creation | CreateProcessA |
| NesysService reference | YES (self-reference) |
| Launcher strings | NONE |
| Working directory strings | NONE |
| Service management APIs | StartServiceCtrlDispatcherA, RegisterServiceCtrlHandlerA, SetServiceStatus |
| Child process evidence | CreateProcessA, GenerateConsoleCtrlEvent |

**Analysis**: This is a Windows Service that manages NESYS (NESiCAxLive) communication. It is NOT a launcher. It is a support service that handles:
- Named pipe communication (`\\.\pipe\nesys_games`)
- Certificate operations (cert3.nesys.jp)
- Card service communication
- Event data download

---

## No Other Executables Found

| Search criteria | Result |
|-----------------|--------|
| .exe files | 3 (all known) |
| .bat files | 0 |
| .cmd files | 0 |
| .lnk files | 0 |
| .vbs files | 0 |
| .ps1 files | 0 |

---

## Classification

**ORIGINAL_LAUNCHER_CANDIDATE**: NOT_FOUND

**Rationale**:
- AcrGame.exe is a standard UE4 game executable, not a custom launcher
- AcrGame-Win64-Shipping.exe is the main game binary
- NesysService.exe is a Windows Service, not a launcher
- No .bat, .cmd, .lnk, .vbs, or .ps1 files exist
- No startup scripts or batch files found
- No Windows Service wrapper found

**Conclusion**: The original launcher is NOT present in the operator-owned content. The game was likely launched by a system-drive component that is not included in this backup.

---

## Comparison to Known Three

| Executable | Classification | Role |
|------------|----------------|------|
| AcrGame.exe | GAME_EXECUTABLE | UE4 game launcher |
| AcrGame-Win64-Shipping.exe | GAME_EXECUTABLE | Main game binary |
| NesysService.exe | SUPPORT_SERVICE | NESYS communication service |

**No additional candidates exist.**
