# Game Executable Candidates

## 1. Primary Executable

| Property | Value |
|----------|-------|
| File | `AcrGame-Win64-Shipping.exe` |
| Size | 163,440,640 bytes (163MB) |
| SHA-256 | `6c845e7433144b917d1df0d4e3937960ea2970a72ae218916013d0052a09f85a` |
| Architecture | x64 |
| Type | PE32+ (64-bit executable) |
| Linker | MSVC (Microsoft Visual C++) |
| Subsystem | Windows (GUI) |
| Project | AcrGame |
| Engine | UE4 4.16 |
| Build | Shipping |

## 2. Launcher Executable

| Property | Value |
|----------|-------|
| File | `AcrGame.exe` |
| Size | 161,280 bytes (161KB) |
| SHA-256 | `0202fc83f5f8027f641e90196549190a083cd5f3e67e0c83c682beef06ed780e` |
| Architecture | x64 |
| Type | PE32+ (64-bit executable) |
| Linker | MSVC |
| Subsystem | Windows (GUI) |
| Imports | XINPUT1_3.dll, KERNEL32.dll, USER32.dll, Winhttp.dll |

**Purpose**: Bootstrapper that launches the main game binary. Handles XInput initialization and system checks.

## 3. NESYS Service Executable

| Property | Value |
|----------|-------|
| File | `NesysService.exe` |
| Size | 548,352 bytes (548KB) |
| SHA-256 | `06ef9d72478198007435377564d054141039222b4d7243e6c629f7c5c2162f74` |
| Architecture | x64 |
| Type | PE32+ (64-bit executable) |
| Linker | MSVC |
| Subsystem | Windows (GUI) |
| Imports | KERNEL32.dll, WTSAPI32.dll, USER32.dll, ADVAPI32.dll, WS2_32.dll, Secur32.dll, ntdll.dll |

**Purpose**: Standalone network service for NESYS card operations. Communicates with the main game process.

## 4. Launch Recommendations

| Method | Command | Notes |
|--------|---------|-------|
| Via launcher | `AcrGame.exe` | Recommended (handles XInput) |
| Direct shipping | `AcrGame-Win64-Shipping.exe` | Bypasses launcher |
| Via command line | `AcrGame-Win64-Shipping.exe -game AcrGame` | Explicit game parameter |

## 5. Command Line Parameters (UE4 Standard)

| Parameter | Description |
|-----------|-------------|
| `-game` | Explicit game parameter |
| `-windowed` | Force windowed mode |
| `-resx=1280` | Horizontal resolution |
| `-resy=720` | Vertical resolution |
| `-log` | Enable logging |
| `-stdout` | Redirect output to stdout |
| `-nosound` | Disable audio |
| `-nopixel` | Skip pixel shaders |
| `-onethread` | Single-threaded mode |

## 6. Launch Sequence

```
1. User runs AcrGame.exe
2. AcrGame.exe loads XINPUT1_3.dll
3. AcrGame.exe starts NesysService.exe (if configured)
4. AcrGame.exe launches AcrGame-Win64-Shipping.exe
5. Game initializes D3D11 renderer
6. Game connects to 127.0.0.1:4001 (game server)
7. Game connects to 127.0.0.1:6666 (NESYS service)
8. Game displays title screen
```
