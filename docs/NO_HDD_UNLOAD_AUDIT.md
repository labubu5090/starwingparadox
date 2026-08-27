# NoHDDUnload Audit

## 1. File Properties

| Property | Value |
|----------|-------|
| File | `X:\StarwingParadox\NoHDDUnload.dll` |
| Size | 76,800 bytes (77KB) |
| SHA-256 | `3091505950470abdd2e140400c0e04503e5e6b320637393f6214df612d8406f0` |
| Architecture | x86 (32-bit) |
| Type | PE32 (32-bit DLL) |
| Linker | MSVC (Microsoft Visual C++) |

## 2. PE Header Analysis

| Field | Value |
|-------|-------|
| Machine | 0x014C (I386) |
| TimeDateStamp | 0x5122C5D4 (2013-02-20) |
| MajorLinkerVersion | 10 |
| MinorLinkerVersion | 0 |
| SizeOfCode | 57,344 bytes |
| SizeOfInitializedData | 19,456 bytes |
| SizeOfUninitializedData | 0 |

## 3. DLL Imports

| DLL | Functions |
|-----|-----------|
| KERNEL32.dll | CreateFileA, WriteFile, GetPrivateProfileStringA, GetModuleFileNameA, Sleep, GetTickCount, HeapAlloc, HeapFree, GlobalAlloc, GlobalFree, lstrcmpA, lstrlenA, etc. |
| SHLWAPI.dll | PathFileExistsA, PathAppendA, PathRemoveFileSpecA, wvnsprintfA |
| ole32.dll | CoCreateInstance, CoTaskMemAlloc, CoTaskMemFree |

## 4. Configuration

From `X:\StarwingParadox\NoHDDUnload.ini`:
```ini
WriteFileInterval=50000
```

50,000 milliseconds = 50 seconds

## 5. Purpose Analysis

Based on the imports and filename:

1. **Storage helper** for arcade cabinet
2. **Periodic file writing** (every 50 seconds)
3. **Monitors file system** (PathFileExistsA, GetModuleFileNameA)
4. **Creates files** (CreateFileA, WriteFile)
5. **Uses COM** (CoCreateInstance) — possibly for storage management
6. **32-bit DLL** running in a 64-bit process (WOW64)

## 6. Likely Function

The DLL appears to be a **storage management helper** that:
- Periodically writes game state/save data to disk
- Monitors file system for changes
- Handles storage allocation/cleanup
- Manages temporary storage for arcade cabinet

## 7. Implications

| Aspect | Implication |
|--------|-------------|
| Required | Yes (game imports it) |
| Safe to remove | No |
| Can be mocked | Possibly (if we intercept DLL loading) |
| Storage format | Unknown (needs runtime analysis) |
| Dependency | None visible (self-contained) |

## 8. Recommendation

- **Do NOT remove** from game content
- **Do NOT modify** game files
- **Runtime monitoring** recommended to understand actual behavior
- **DLL hooking** may be needed for cabinet emulation (not yet implemented)
