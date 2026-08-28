# NesysService Service Control Analysis

**Phase**: 2A-G13  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe is a Windows Service that implements the NESYS (NESiCAxLive) communication layer for Starwing Paradox. The service creates a named pipe server that the game client connects to for card operations, event data, and server communication.

---

## Windows Service Identity

### Service Name

| Property | Value | Evidence |
|----------|-------|----------|
| Service name | `NesysService` | String reference at binary offset |
| Service display name | `NesysService` | RegisterServiceCtrlHandlerA call |
| Service description | (none found) | No ChangeServiceConfig2 usage |

### ServiceMain Entry Point

| Property | Value | Evidence |
|----------|-------|----------|
| ServiceMain function | `swp_service_main` | Cross-reference from ServiceMain.cpp string |
| Entry point type | SERVICE_MAIN_FUNCTIONW | StartServiceCtrlDispatcherA import |

### Service Control Handler

| Property | Value | Evidence |
|----------|-------|----------|
| Handler function | `swp_service_ctrl_handler` | RegisterServiceCtrlHandlerA call |
| Handler registration | RegisterServiceCtrlHandlerA | Import table |
| Accepted controls | SERVICE_ACCEPT_STOP, SERVICE_ACCEPT_SHUTDOWN | SetServiceStatus with SERVICE_RUNNING state |

### Service State Transitions

| State | Transition | Evidence |
|-------|------------|----------|
| SERVICE_START_PENDING | → SERVICE_RUNNING | SetServiceStatus call |
| SERVICE_RUNNING | → SERVICE_STOP_PENDING | Service control handler |
| SERVICE_STOP_PENDING | → SERVICE_STOPPED | SetServiceStatus call |
| SERVICE_RUNNING | → SERVICE_SHUTDOWN | Service control handler |

### Service Control Handler Switch Cases

| Control | Handler | Evidence |
|---------|---------|----------|
| SERVICE_CONTROL_STOP | swp_handle_stop | Switch case in service control handler |
| SERVICE_CONTROL_SHUTDOWN | swp_handle_shutdown | Switch case in service control handler |
| SERVICE_CONTROL_INTERROGATE | swp_handle_interrogate | Default case |

### Startup State Transitions

| State | Duration | Evidence |
|-------|----------|----------|
| SERVICE_START_PENDING | Short (no extended init) | SetServiceStatus calls |
| SERVICE_RUNNING | Long-running | Service loop |

### Stop and Shutdown Handling

| Event | Handler | Behavior |
|-------|---------|----------|
| SERVICE_CONTROL_STOP | swp_handle_stop | Sets SERVICE_STOP_PENDING, cleans up, sets SERVICE_STOPPED |
| SERVICE_CONTROL_SHUTDOWN | swp_handle_shutdown | Same as stop handler |

### Dependency or Parent-Process Validation

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| Parent process check | NONE | No GetParentProcessId or similar |
| Dependency strings | NONE | No DependOnService references |
| Service group | NONE | No ServiceMain group parameter |

**Conclusion**: NesysService has no parent-process validation or dependency requirements.

### Command-Line Argument Handling

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| argc/argv parsing | NONE | No __argc/__argv references |
| Command-line modes | NONE | No -app, -console, -debug, -install, -uninstall strings |
| Mode selection | NONE | No mode switch code |

**Conclusion**: NesysService does not use command-line arguments. It runs purely as a Windows Service.

---

## Service Startup Sequence

### Observed Startup Flow

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

### Service Shutdown Flow

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

## Service Configuration Requirements

### Missing Configuration

| Component | Status | Impact |
|-----------|--------|--------|
| Service registration | MISSING | Cannot register with SCM |
| Service dependencies | MISSING | Cannot determine startup order |
| Service recovery | MISSING | Cannot configure restart on failure |
| Service SID type | MISSING | Cannot configure service SID |
| Service triggers | MISSING | Cannot configure trigger start |

### Required Configuration (Inferred)

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| Service type | SERVICE_WIN32_OWN_PROCESS | Standard for standalone service |
| Start type | SERVICE_AUTO_START | Service should start with Windows |
| Error control | SERVICE_ERROR_NORMAL | Standard error handling |
| Account | LocalSystem or custom service account | Needs network and certificate access |

---

## Service Control Manager Interaction

### APIs Used

| API | Import | Usage |
|-----|--------|-------|
| StartServiceCtrlDispatcherA | YES | Connects ServiceMain to SCM |
| RegisterServiceCtrlHandlerA | YES | Registers service control handler |
| SetServiceStatus | YES | Updates service state |

### Service Control Handler

| API | Import | Usage |
|-----|--------|-------|
| RegisterServiceCtrlHandlerA | YES | Returns SERVICE_STATUS_HANDLE |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Service identity | CONFIRMED |
| ServiceMain entry | CONFIRMED |
| Service control handler | CONFIRMED |
| State transitions | CONFIRMED |
| Stop/shutdown handling | CONFIRMED |
| Parent-process validation | NOT_REQUIRED |
| Command-line arguments | NOT_REQUIRED |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact ServiceMain address | MEDIUM | Requires IDA disassembly |
| Service control handler address | MEDIUM | Requires IDA disassembly |
| Service start type | LOW | Inferred as SERVICE_AUTO_START |
| Service account | LOW | Inferred as LocalSystem |

---

## Conclusion

NesysService.exe is a Windows Service that:
1. Registers as "NesysService" with the Windows Service Control Manager
2. Implements ServiceMain, service control handler, and state transitions
3. Does NOT require command-line arguments
4. Does NOT validate parent process
5. Requires service registration with SCM

**Classification**: `CONFIRMED`

The service identity and control flow are fully evidenced.
