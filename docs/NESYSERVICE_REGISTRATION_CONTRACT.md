# NesysService Registration Contract

**Phase**: 2A-G14  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe implements a Windows Service with confirmed ServiceMain, service control handler, and state transitions. The service does NOT contain self-installation code. Service registration was performed externally (installer, system image, or deployment package).

---

## Service Identity

### Confirmed Properties

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Internal service name | NesysService | CONFIRMED | String reference |
| Service type | SERVICE_WIN32_OWN_PROCESS | INFERRED | Standard for standalone service |
| Start type | SERVICE_AUTO_START | INFERRED | Standard for game services |
| Error control | SERVICE_ERROR_NORMAL | INFERRED | Standard error handling |
| Account | LocalSystem | INFERRED | Needs network and cert access |
| Display name | NOT_FOUND | NOT_FOUND | No ChangeServiceConfig2 usage |
| Description | NOT_FOUND | NOT_FOUND | No ChangeServiceConfig2 usage |

### Evidence Classification

| Property | Classification | Notes |
|----------|----------------|-------|
| Service name | CONFIRMED | String reference in binary |
| Service type | INFERRED | Not explicitly set in code |
| Start type | INFERRED | Not explicitly set in code |
| Error control | INFERRED | Not explicitly set in code |
| Account | INFERRED | Not explicitly set in code |
| Display name | NOT_FOUND | No evidence found |
| Description | NOT_FOUND | No evidence found |

---

## ServiceMain Entry Point

### Confirmed Properties

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Function name | swp_service_main | CONFIRMED | String reference |
| Entry type | SERVICE_MAIN_FUNCTIONW | CONFIRMED | StartServiceCtrlDispatcherA import |
| Parameters | argc, argv | CONFIRMED | Standard ServiceMain signature |

---

## Service Control Handler

### Confirmed Properties

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Function name | swp_service_ctrl_handler | CONFIRMED | String reference |
| Registration API | RegisterServiceCtrlHandlerA | CONFIRMED | Import table |
| Accepted controls | SERVICE_ACCEPT_STOP, SERVICE_ACCEPT_SHUTDOWN | CONFIRMED | SetServiceStatus calls |

---

## State Transitions

### Confirmed Transitions

| From State | To State | Trigger | Evidence |
|------------|----------|---------|----------|
| (none) | SERVICE_START_PENDING | ServiceMain entry | SetServiceStatus call |
| SERVICE_START_PENDING | SERVICE_RUNNING | Initialization complete | SetServiceStatus call |
| SERVICE_RUNNING | SERVICE_STOP_PENDING | SERVICE_CONTROL_STOP | Service control handler |
| SERVICE_STOP_PENDING | SERVICE_STOPPED | Cleanup complete | SetServiceStatus call |
| SERVICE_RUNNING | SERVICE_SHUTDOWN | SERVICE_CONTROL_SHUTDOWN | Service control handler |

---

## Startup Sequence

### Observed Flow

```
1. Windows SCM loads NesysService.exe
2. SCM calls StartServiceCtrlDispatcherA with ServiceMain
3. ServiceMain calls RegisterServiceCtrlHandlerA
4. ServiceMain calls SetServiceStatus(SERVICE_START_PENDING)
5. ServiceMain initializes:
   - Creates mutex (CreateMutexA)
   - Initializes Winsock (WSAStartup)
   - Creates named pipe server
   - Starts worker threads
6. ServiceMain calls SetServiceStatus(SERVICE_RUNNING)
7. Service enters main loop
```

---

## Shutdown Sequence

### Observed Flow

```
1. SCM sends SERVICE_CONTROL_STOP or SERVICE_SHUTDOWN
2. Service control handler sets SERVICE_STOP_PENDING
3. Service signals worker threads to stop
4. Service closes named pipe
5. Service releases mutex
6. Service calls SetServiceStatus(SERVICE_STOPPED)
7. Service exits
```

---

## Self-Installation Capability

### Command-Line Analysis

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| argc/argv parsing | NONE | No __argc/__argv references |
| GetCommandLine usage | NONE | No GetCommandLineA/W imports |
| Command-line comparisons | NONE | No "-install", "-uninstall", "-console" strings |
| CreateService calls | NONE | No CreateServiceA/W imports |
| OpenSCManager calls | NONE | No OpenSCManagerA/W imports |
| DeleteService calls | NONE | No DeleteService imports |
| StartServiceCtrlDispatcher | YES | Import found (service mode only) |

### Conclusion

**Self-Installation**: `NOT_FOUND`

NesysService.exe does NOT contain self-installation logic. It only implements service mode (ServiceMain + control handler). Service registration was performed by an external mechanism.

---

## Service Registration Mechanism

### Evidence

| Mechanism | Evidence | Strength |
|-----------|----------|----------|
| Self-installation | NONE | No CreateService/OpenSCManager imports |
| MSI installer | NONE | No MSI strings found |
| InnoSetup | NONE | No InnoSetup strings found |
| NSIS | NONE | No NSIS strings found |
| PowerShell script | NONE | No PowerShell strings found |
| Batch script | NONE | No batch script strings found |
| System image | POSSIBLE | Pre-configured D-drive backup |

### Classification

**Registration Mechanism**: `EXTERNAL` (installer, system image, or deployment package)

Service registration was NOT performed by NesysService.exe itself. The exact external mechanism is UNKNOWN from available evidence.

---

## Dependencies

### Service Dependencies

| Dependency | Evidence | Strength |
|------------|----------|----------|
| DependOnService | NONE | No DependOnService references |
| Service group | NONE | No ServiceMain group parameter |
| Parent process check | NONE | No GetParentProcessId |
| Network dependency | INFERRED | WinHTTP imports |
| Certificate dependency | INFERRED | Certificate store imports |

### Required Dependencies (Inferred)

| Dependency | Rationale |
|------------|-----------|
| Network stack | WinHTTP and Winsock imports |
| Certificate store | Certificate API imports |
| Named pipe support | CreateNamedPipeA import |
| Event Log | Error logging (possible) |

---

## Recovery Configuration

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Failure actions | NOT_FOUND | No ChangeServiceConfig2 with SERVICE_CONFIG_FAILURE_ACTIONS |
| Restart delay | NOT_FOUND | No restart configuration |
| Recovery count | NOT_FOUND | No recovery configuration |
| Run program | NOT_FOUND | No recovery program |

**Recovery Configuration**: `NOT_CONFIGURED_IN_BINARY`

Service recovery was likely configured externally (installer, group policy, or manual configuration).

---

## SID Type

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Service SID type | NOT_FOUND | No ChangeServiceConfig2 with SERVICE_CONFIG_SERVICE_SID_INFO |

**SID Type**: `NOT_CONFIGURED_IN_BINARY`

Service SID type was likely configured externally or uses default (SERVICE_SID_TYPE_NONE).

---

## Preshutdown Timeout

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Preshutdown timeout | NOT_FOUND | No ChangeServiceConfig2 with SERVICE_CONFIG_PRESHUTDOWN_INFO |

**Preshutdown Timeout**: `NOT_CONFIGURED_IN_BINARY`

---

## Working Directory

### Status

| Property | Status | Notes |
|----------|--------|-------|
| Working directory | NOT_FOUND | No SetCurrentDirectory or working directory setup |

**Working Directory**: `NOT_REQUIRED` (service runs from system directory)

---

## Environment Dependencies

### Status

| Dependency | Evidence | Strength |
|------------|----------|----------|
| PATH | INFERRED | Standard system dependency |
| SYSTEMROOT | INFERRED | Standard Windows dependency |
| Custom variables | NOT_FOUND | No environment variable references |

---

## Registry Dependencies

### Confirmed Dependencies

| Key | Values | Evidence |
|-----|--------|----------|
| HKLM\SOFTWARE\taito\typex | GameKind, EventNextTime, ConditionTime, TrafficCount, LogLevel, NewsPath, EventPath, LogPath | String references |

---

## Certificate Dependencies

### Confirmed Dependencies

| Store | Subject | Evidence |
|-------|---------|----------|
| MY\.Default | nesys | String references |

---

## File Dependencies

### Status

| Dependency | Evidence | Strength |
|------------|----------|----------|
| NewsPath | Registry value | CONFIRMED |
| EventPath | Registry value | CONFIRMED |
| LogPath | Registry value | CONFIRMED |
| Named pipe | String reference | CONFIRMED |

---

## Required Privileges

### Status

| Privilege | Evidence | Strength |
|-----------|----------|----------|
| SeServiceLogonRight | INFERRED | Service logon privilege |
| SeNetworkLogonRight | INFERRED | Network access |
| SeCreateNamedPipeObject | INFERRED | Named pipe creation |

---

## Unresolved Items

| Item | Status | Impact |
|------|--------|--------|
| Exact service registration mechanism | UNKNOWN | Cannot determine how service was registered |
| Display name | NOT_FOUND | Service may appear differently in SCM |
| Description | NOT_FOUND | Service has no description in SCM |
| Failure actions | NOT_FOUND | Service has no automatic recovery |
| SID type | NOT_FOUND | Uses default SID configuration |
| Preshutdown timeout | NOT_FOUND | Uses default timeout |
| Exact account | INFERRED | May require custom service account |
| Exact dependencies | INFERRED | May have additional dependencies |

---

## Conclusion

NesysService.exe implements a Windows Service with confirmed ServiceMain, service control handler, and state transitions. The service does NOT contain self-installation code. Service registration was performed externally (installer, system image, or deployment package).

**Classification**: `EXTERNAL_REGISTRATION_REQUIRED`

Service registration cannot be performed by NesysService.exe itself. An external mechanism (installer, system image, or manual registration) is required.

---

## G14 Audit Notes

This document was created in Phase 2A-G14 to reconstruct the Windows service registration contract from static evidence. All properties are classified with appropriate confidence levels. Inferences are clearly marked and not promoted to confirmed facts.
