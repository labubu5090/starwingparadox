# Game Runtime Dependencies

## 1. System Requirements

| Component | Requirement | Status |
|-----------|-------------|--------|
| OS | Windows 10/11 (x64) | Present |
| CPU | x86-64 compatible | Present |
| RAM | 4GB+ | Present |
| GPU | DirectX 11 compatible | Present |
| D3D11 Runtime | DirectX 11 | Present |
| XAudio2 Runtime | DirectX Audio | Present |

## 2. Required DLLs (System)

| DLL | Purpose | Status |
|-----|---------|--------|
| d3d11.dll | DirectX 11 | Present |
| d3dcompiler_46.dll | Shader compilation | Present |
| d3dx11_43.dll | D3D11 utilities | Present |
| xaudio2_7.dll | Audio | Present |
| kernel32.dll | Core Windows | Present |
| user32.dll | Windows UI | Present |
| advapi32.dll | Security | Present |
| ws2_32.dll | Winsock | Present |
| secur32.dll | Security | Present |
| ntdll.dll | NT kernel | Present |
| wtsapi32.dll | Terminal Services | Present |

## 3. Required DLLs (Game)

| DLL | Purpose | Status |
|-----|---------|--------|
| bink2w64.dll | Video playback | Bundled |
| mp3decoder.dll | Audio decoding | Bundled |
| vorbisinterp.dll | Ogg Vorbis | Bundled |
| ogg.dll | Ogg container | Bundled |
| openal.dll | Audio API | Bundled |
| NesysNet.dll | NESYS networking | Bundled |

## 4. MSVC Runtimes

| Runtime | Version | Status |
|---------|---------|--------|
| vcomp100.dll | MSVC 2010 | Present |
| vcomp110.dll | MSVC 2012 | Present |
| vcomp140.dll | MSVC 2015 | Present |
| MSVCP100.dll | MSVC 2010 | Present |
| MSVCP110.dll | MSVC 2012 | Present |
| MSVCP140.dll | MSVC 2015 | Present |
| VCRUNTIME140.dll | MSVC 2015 | Present |
| api-ms-win-crt-*.dll | Universal CRT | Present |

## 5. XInput

| DLL | Purpose | Status |
|-----|---------|--------|
| XINPUT1_3.dll | Gamepad support | Present |

## 6. Implicit Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Windows Media Foundation | Video decoding | Present |
| .NET Framework | NESYS service (maybe) | Unknown |
| Visual C++ Redistributable | Runtime | Present |

## 7. No Missing Dependencies

All required DLLs are either:
- Bundled with the game installation
- Present in Windows system directory
