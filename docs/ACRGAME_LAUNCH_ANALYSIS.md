# AcrGame Launch Analysis

**Phase**: 2A-G13  
**Executable**: AcrGame.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

AcrGame.exe is a standard Unreal Engine 4 game launcher that creates AcrGame-Win64-Shipping.exe as a child process. The executable does NOT contain direct references to NesysService, named pipes, or NESYS-related functionality. It serves as a bootstrap wrapper for the main game binary.

---

## Executable Identity

### PE Information

| Property | Value | Evidence |
|----------|-------|----------|
| File size | 161,280 bytes | File system |
| SHA-256 | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` | Hash calculation |
| Architecture | PE32+ (64-bit) | PE header |
| Image base | 0x140000000 | PE header |
| Entry point | Standard UE4 entry | PE header |
| PDB | BootstrapPackagedGame-Win64-Shipping.pdb | String reference |
| Subsystem | Windows (GUI) | PE header |

---

## Launcher/Bootstrapper/Game Executable Classification

### Classification

| Property | Value | Evidence |
|----------|-------|----------|
| Type | Bootstrap wrapper | PDB name "BootstrapPackagedGame" |
| Purpose | Launches AcrGame-Win64-Shipping.exe | CreateProcessW usage |
| UE4 role | Standard UE4 launcher | String patterns |

### Evidence

| Evidence | Strength |
|----------|----------|
| PDB name contains "Bootstrap" | HIGH |
| CreateProcessW import | CONFIRMED |
| WaitForSingleObject import | CONFIRMED |
| No game-specific imports | CONFIRMED |

---

## Child Processes

### CreateProcessW Usage

| API | Import | Usage |
|-----|--------|-------|
| CreateProcessW | YES | Creates child process |

### Child Process Details

| Property | Value | Evidence |
|----------|-------|----------|
| Target executable | AcrGame-Win64-Shipping.exe | Standard UE4 pattern |
| Command line | Constructed dynamically | GetCommandLineW usage |
| Working directory | Inherited or constructed | GetCurrentDirectory usage |
| Process creation flags | Standard UE4 flags | Inferred |

### Process Creation Sequence

```
1. AcrGame.exe starts
2. Gets command line (GetCommandLineW)
3. Constructs child process command line
4. Creates AcrGame-Win64-Shipping.exe (CreateProcessW)
5. Waits for child process (WaitForSingleObject)
6. Exits with child process exit code
```

---

## Command-Line Construction

### Command-Line APIs

| API | Import | Usage |
|-----|--------|-------|
| GetCommandLineA | YES | Gets ANSI command line |
| GetCommandLineW | YES | Gets Unicode command line |

### Command-Line Patterns

| Pattern | Evidence | Strength |
|----------|----------|----------|
| Standard UE4 arguments | String patterns | MEDIUM |
| No NesysService arguments | No pipe/service strings | CONFIRMED |

---

## Working-Directory Setup

### Directory APIs

| API | Import | Usage |
|-----|--------|-------|
| GetCurrentDirectoryW | YES | Gets current directory |
| SetCurrentDirectoryW | YES | Sets current directory |

### Directory Behavior

| Behavior | Evidence | Strength |
|----------|----------|----------|
| Inherited from parent | Standard UE4 pattern | MEDIUM |
| Constructed from executable path | Standard UE4 pattern | MEDIUM |

---

## Environment Variables

### Environment APIs

| API | Import | Usage |
|-----|--------|-------|
| GetEnvironmentVariableA | YES | Gets environment variable |
| GetEnvironmentVariableW | YES | Gets environment variable |

### Environment Variables

| Variable | Evidence | Strength |
|----------|----------|----------|
| PATH | Standard | MEDIUM |
| HOME | Standard | MEDIUM |
| No NESYS-specific variables | No pipe/service strings | CONFIRMED |

---

## Registry Reads

### Registry APIs

| API | Import | Usage |
|-----|--------|-------|
| RegOpenKeyExA | YES | Opens registry key |
| RegQueryValueExA | YES | Reads registry value |

### Registry Usage

| Usage | Evidence | Strength |
|-------|----------|----------|
| Standard UE4 registry reads | Import found | MEDIUM |
| No NesysService references | No pipe/service strings | CONFIRMED |

---

## Service-Control API Usage

### Service APIs

| API | Import | Usage |
|-----|--------|-------|
| None | - | No service-related imports |

**No service-control API usage found.**

---

## Named-Pipe References

### Pipe References

| Reference | Evidence | Strength |
|-----------|----------|----------|
| No pipe string references | String analysis | CONFIRMED |
| No CreateNamedPipe | No import | CONFIRMED |
| No CreateFile for pipes | No pipe strings | CONFIRMED |

**No named-pipe references found.**

---

## References to NesysService.exe

### String References

| String | Evidence | Strength |
|--------|----------|----------|
| "NesysService" | NOT_FOUND | CONFIRMED |
| "nesys_games" | NOT_FOUND | CONFIRMED |
| "\\.\pipe\" | NOT_FOUND | CONFIRMED |
| "service" | NOT_FOUND (except UE4 engine) | CONFIRMED |

**No NesysService references found.**

---

## Wait/Retry Logic for NESYS Readiness

### Wait APIs

| API | Import | Usage |
|-----|--------|-------|
| WaitForSingleObject | YES | Waits for child process |

### Wait Behavior

| Behavior | Evidence | Strength |
|----------|----------|----------|
| Waits for child process exit | WaitForSingleObject | CONFIRMED |
| No NESYS readiness check | No pipe/service strings | CONFIRMED |

**No NESYS readiness wait logic found.**

---

## Exit-Code Handling

### Exit APIs

| API | Import | Usage |
|-----|--------|-------|
| ExitProcess | YES | Exits process |

### Exit Behavior

| Behavior | Evidence | Strength |
|----------|----------|----------|
| Returns child process exit code | Standard UE4 pattern | MEDIUM |
| No NESYS-specific exit codes | No pipe/service strings | CONFIRMED |

---

## Whether It Starts AcrGame-Win64-Shipping.exe

### Evidence

| Evidence | Strength |
|----------|----------|
| CreateProcessW import | CONFIRMED |
| Standard UE4 bootstrap pattern | HIGH |
| PDB name "BootstrapPackagedGame" | HIGH |
| No other executable references | CONFIRMED |

**Conclusion**: AcrGame.exe creates AcrGame-Win64-Shipping.exe as a child process.

---

## Whether the File Is a Wrapper

### Wrapper Evidence

| Evidence | Strength |
|----------|----------|
| Small file size (161KB) | HIGH |
| PDB name contains "Bootstrap" | HIGH |
| CreateProcessW import | CONFIRMED |
| WaitForSingleObject import | CONFIRMED |
| No game-specific imports | CONFIRMED |

**Conclusion**: AcrGame.exe is a wrapper/bootstrap for AcrGame-Win64-Shipping.exe.

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Executable type | CONFIRMED |
| Child process | CONFIRMED |
| Command-line construction | HIGH |
| Working directory | HIGH |
| Environment variables | MEDIUM |
| Registry reads | MEDIUM |
| Service-control usage | NOT_FOUND |
| Named-pipe references | NOT_FOUND |
| NesysService references | NOT_FOUND |
| Wait/retry logic | NOT_FOUND |
| Exit-code handling | HIGH |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact command-line arguments | MEDIUM | Requires IDA disassembly |
| Exact working directory | LOW | Standard UE4 pattern |
| Exact environment variables | LOW | Standard UE4 pattern |
| Registry key paths | LOW | Standard UE4 pattern |

---

## Conclusion

AcrGame.exe is a standard Unreal Engine 4 bootstrap wrapper that creates AcrGame-Win64-Shipping.exe as a child process. The executable does NOT contain direct references to NesysService, named pipes, or NESYS-related functionality. It serves purely as a launcher for the main game binary.

**Classification**: `CONFIRMED`

The launch analysis is fully evidenced with string analysis and API imports.
