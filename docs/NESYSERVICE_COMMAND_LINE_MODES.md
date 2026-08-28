# NesysService Command-Line Modes

**Phase**: 2A-G14  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe does NOT contain self-installation, console, debug, or repair modes. The executable only implements service mode (ServiceMain + control handler). Service registration was performed externally.

---

## Command-Line Analysis

### argc/argv Processing

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| __argc reference | NONE | No import or string |
| __argv reference | NONE | No import or string |
| CommandLineToArgvW | NONE | No import |
| GetCommandLineA/W | NONE | No import |
| argc comparison | NONE | No comparison code |

### Mode Selection

| Mode | String | Evidence |
|------|--------|----------|
| -install | NONE | No string found |
| -uninstall | NONE | No string found |
| -register | NONE | No string found |
| -console | NONE | No string found |
| -debug | NONE | No string found |
| -repair | NONE | No string found |
| -service | NONE | No string found (service is default mode) |
| -app | NONE | No string found |

### Service Control APIs

| API | Import | Usage |
|-----|--------|-------|
| OpenSCManagerA | NONE | No import |
| OpenSCManagerW | NONE | No import |
| CreateServiceA | NONE | No import |
| CreateServiceW | NONE | No import |
| DeleteService | NONE | No import |
| ChangeServiceConfigA | NONE | No import |
| ChangeServiceConfigW | NONE | No import |
| ChangeServiceConfig2A | NONE | No import |
| ChangeServiceConfig2W | NONE | No import |
| StartServiceCtrlDispatcherA | YES | Service mode only |
| RegisterServiceCtrlHandlerA | YES | Service mode only |
| SetServiceStatus | YES | Service mode only |

---

## Execution Modes

### Mode Classification

| Mode | Present | Evidence |
|------|---------|----------|
| Service mode | YES | StartServiceCtrlDispatcherA import |
| Console mode | NOT_FOUND | No console allocation or attach |
| Debug mode | NOT_FOUND | No debug strings or flags |
| Install mode | NOT_FOUND | No CreateService/OpenSCManager |
| Uninstall mode | NOT_FOUND | No DeleteService |
| Repair mode | NOT_FOUND | No repair logic |

---

## Interactive Session Detection

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| GetConsoleWindow | NONE | No import |
| AttachConsole | NONE | No import |
| AllocConsole | NONE | No import |
| IsUserAnAdmin | NONE | No import |

**Interactive Session Detection**: `NOT_FOUND`

---

## Parent-Process Checks

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| GetParentProcessId | NONE | No import |
| NtQueryInformationProcess | NONE | No import |
| Process inheritance check | NONE | No code |

**Parent-Process Checks**: `NOT_FOUND`

---

## Process Creation

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| CreateProcessA | NONE | No import |
| CreateProcessW | NONE | No import |
| ShellExecute | NONE | No import |

**Process Creation**: `NOT_FOUND` (service does not launch child processes)

---

## Entry Point Analysis

### Service Entry

| Property | Value | Evidence |
|----------|-------|----------|
| Entry point | ServiceMain | StartServiceCtrlDispatcherA call |
| Parameters | argc, argv | Standard ServiceMain signature |
| Default mode | Service | Only mode implemented |

### Bootstrap Sequence

```
1. SCM loads NesysService.exe
2. SCM calls StartServiceCtrlDispatcherA
3. StartServiceCtrlDispatcherA calls ServiceMain(argc, argv)
4. ServiceMain initializes service
5. Service enters main loop
```

---

## Error Handling

### Invalid Mode

| Condition | Effect | Evidence |
|-----------|--------|----------|
| No command-line args | Service mode (default) | No mode selection code |
| Unknown args | Ignored | No argument parsing |
| Non-Service context | Service fails | StartServiceCtrlDispatcher fails |

---

## Self-Installation Evidence

### Required APIs (None Found)

| API | Required For | Present |
|-----|--------------|---------|
| OpenSCManagerA/W | Service registration | NO |
| CreateServiceA/W | Service creation | NO |
| DeleteService | Service removal | NO |
| ChangeServiceConfigA/W | Service modification | NO |
| ChangeServiceConfig2A/W | Service description, recovery | NO |

### Required Strings (None Found)

| String | Required For | Present |
|--------|--------------|---------|
| "install" | Install mode | NO |
| "uninstall" | Uninstall mode | NO |
| "register" | Register mode | NO |
| "console" | Console mode | NO |
| "debug" | Debug mode | NO |
| "repair" | Repair mode | NO |

---

## Classification

**Self-Installation**: `NOT_FOUND`

**Console Mode**: `NOT_FOUND`

**Debug Mode**: `NOT_FOUND`

**Service Mode**: `CONFIRMED`

---

## Conclusion

NesysService.exe does NOT contain self-installation, console, debug, or repair modes. The executable only implements service mode (ServiceMain + control handler). Service registration was performed by an external mechanism (installer, system image, or deployment package).

**Classification**: `SERVICE_MODE_ONLY`

The executable is a pure Windows Service implementation with no command-line mode selection.

---

## G14 Audit Notes

This document was created in Phase 2A-G14 to determine if NesysService has self-installation capability. No self-installation code was found. Service registration requires an external mechanism.
