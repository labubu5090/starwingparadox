# Static Dependency Audit

## 1. Executable Dependencies

### AcrGame.exe (Launcher/Bootstrapper)

| DLL | Type | Size |
|-----|------|------|
| XINPUT1_3.dll | Standard | XInput gamepad |
| KERNEL32.dll | System | Windows core |
| USER32.dll | System | Windows UI |
| Winhttp.dll | Standard | HTTP client |

**Purpose**: Minimal launcher that bootstraps the main game binary.

### AcrGame-Win64-Shipping.exe (Main Game)

| DLL | Type | Purpose |
|-----|------|---------|
| d3d11.dll | System | DirectX 11 rendering |
| d3dcompiler_46.dll | System | D3D shader compilation |
| d3dx11_43.dll | System | D3D11 utilities |
| xaudio2_7.dll | System | Audio |
| bink2w64.dll | Third-party | Video playback |
| mp3decoder.dll | Third-party | Audio decoding |
| vorbisinterp.dll | Third-party | Ogg Vorbis |
| Ogg.dll | Third-party | Ogg container |
| OpenAL.dll | Third-party | Audio API |
| vcomp100.dll | MSVC | OpenMP runtime |
| vcomp110.dll | MSVC | OpenMP runtime |
| vcomp140.dll | MSVC | OpenMP runtime |
| MSVCP100.dll | MSVC | C++ runtime |
| MSVCP110.dll | MSVC | C++ runtime |
| MSVCP140.dll | MSVC | C++ runtime |
| VCRUNTIME140.dll | MSVC | C++ runtime |
| api-ms-win-crt-*.dll (8) | CRT | Universal C runtime |

**Key observations**:
- D3D11 rendering (not D3D12)
- XAudio2 for audio
- Bink2 for video playback
- Multiple MSVC runtimes (100, 110, 140) — all present

### NesysService.exe (NESYS Service)

| DLL | Type | Purpose |
|-----|------|---------|
| KERNEL32.dll | System | Windows core |
| WTSAPI32.dll | System | Windows Terminal Services |
| USER32.dll | System | Windows UI |
| ADVAPI32.dll | System | Security/registry |
| WS2_32.dll | System | Winsock TCP/UDP |
| Secur32.dll | System | Security |
| ntdll.dll | System | NT kernel interface |

**Purpose**: Standalone network service handling NESYS card operations and TCP communication.

## 2. Game DLLs

| DLL | Size | Imports |
|-----|------|---------|
| `AcrGame-Win64-Shipping.pdb` | 318MB | N/A (debug symbols) |
| `AcrGame-Win64-Shipping.iobj` | 128MB | N/A (incremental link) |
| `AcrGame-Win64-Shipping.ipdb` | 144MB | N/A (incremental PDB) |
| `NesysNet.dll` | ~200KB | ws2_32.dll |

## 3. Implicit Dependencies

The game also depends on (not directly visible in PE imports):
- **XInput1_3.dll** — Gamepad support (via XINPUT1_3.dll in launcher)
- **D3D11 runtime** — DirectX 11 support
- **XAudio2 runtime** — Audio support
- **Windows Media Foundation** — Video decoding fallback
- **.NET Framework** — Possibly for NESYS service (not confirmed)

## 4. Dependency Status

| Category | Status |
|----------|--------|
| System DLLs | Present in Windows system32 |
| MSVC runtimes | Multiple versions present |
| D3D11 | Present (Windows 10/11) |
| XAudio2 | Present (Windows 10/11) |
| Bink2 | Bundled with game |
| Ogg/Vorbis | Bundled with game |
| OpenAL | Bundled with game |
| NesysNet | Bundled with game |
| XINPUT1_3 | Present (Windows 10/11) |

## 5. Missing Dependencies

No missing dependencies identified. All required DLLs are either:
- Present in the game installation directory
- Present in the Windows system directory
