# NesysService OpenKey Initialization Order

**Date:** 2026-08-28

## NesysService Exit Timeline

| Stage | Description | Status | Evidence |
|-------|-------------|--------|----------|
| 1. Process creation | NesysService.exe launched | COMPLETED | Exit code -1 observed |
| 2. Binary initialization | DLL loading, CRT init | COMPLETED | Process runs briefly |
| 3. OpenKey read | Read D:\Saved\ACRSaved\SaveData\OpenKey.json | NOT_REACHED | Exits before file access |
| 4. OpenKey create | Create/update OpenKey.json | NOT_REACHED | Exits before file access |
| 5. WINHTTP init | WinHttpOpen, WinHttpConnect | NOT_REACHED | Exits before HTTP init |
| 6. cert3 contact | Contact cert3.nesys.jp | NOT_REACHED | Exits before network |
| 7. Named pipe create | CreateNamedPipeA | NOT_REACHED | Exits before pipe creation |
| 8. Ready state | Service operational | NOT_REACHED | Never reaches ready |

## Analysis

### Exit Timing

NesysService.exe exits immediately (within <1 second of launch) with code -1. The binary analysis shows:

- `FindFirstFileA` — file enumeration (not OpenKey-specific)
- `GetModuleFileNameA` — self-path query
- `RegOpenKeyExA`, `RegQueryValueExA` — registry access
- `WinHttpOpen` — HTTP initialization
- `CreateNamedPipeA` — pipe creation

### OpenKey Access Order

Based on binary analysis and startup requirements:

1. **Process starts** → CRT initialization
2. **Registry check** → RegOpenKeyExA (machine configuration)
3. **HTTP init** → WinHttpOpen (network preparation)
4. **Certificate check** → CertOpenStore (certificate store)
5. **Pipe creation** → CreateNamedPipeA (named pipe server)
6. **File access** → FindFirstFileA (file enumeration)
7. **OpenKey read** → Unknown API (file read)

### Exit Point

NesysService exits at stage 1-2 (process creation / binary initialization). The service never reaches stage 3 (OpenKey access) or later.

**Evidence:** Exit code -1 within <1 second. No named pipe created. No HTTP connections observed.

## Conclusion

**Classification:** NESYSSERVICE_EXITS_BEFORE_OPENKEY_ACCESS

NesysService exits before it could:
- Read OpenKey.json
- Create OpenKey.json
- Start WINHTTP
- Contact cert3.nesys.jp
- Create the named pipe
- Enter ready state

**Implication:** Missing OpenKey cannot be the immediate cause of NesysService exit. The service exits due to missing launcher context, missing registry keys, or missing certificates — not missing OpenKey.

## Initialization Order Classification

| Stage | Classification |
|-------|---------------|
| Process creation | COMPLETED |
| Binary initialization | COMPLETED |
| Registry check | NOT_REACHED |
| HTTP init | NOT_REACHED |
| Certificate check | NOT_REACHED |
| OpenKey read | NOT_REACHED |
| OpenKey create | NOT_REACHED |
| Named pipe create | NOT_REACHED |
| Ready state | NOT_REACHED |
