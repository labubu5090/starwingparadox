# Phase 2A-G12 Final Report

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: COMPLETE  
**Classification**: `D_DRIVE_ONLY_BACKUP_CONFIRMED`  

---

## Executive Summary

Phase 2A-G12 investigated the operator-owned Starwing Paradox content to determine whether the original launcher, startup artifact, process manager, service wrapper, or system-drive component exists that starts NesysService.exe with the required runtime context.

**Finding**: The operator-owned content is a D-drive only backup. The original Windows system drive (C:) is NOT included. The original launcher, startup configuration, certificate store, registry, and Windows Service configuration are missing.

**Classification**: `D_DRIVE_ONLY_BACKUP_CONFIRMED`

---

## Key Findings

### 1. Executables

Only three executables exist:

| Executable | Classification | Role |
|------------|----------------|------|
| AcrGame.exe | GAME_EXECUTABLE | UE4 game launcher |
| AcrGame-Win64-Shipping.exe | GAME_EXECUTABLE | Main game binary |
| NesysService.exe | SUPPORT_SERVICE | NESYS communication service |

**No launcher candidates found.**

### 2. Script Files

| Type | Count |
|------|-------|
| .bat | 0 |
| .cmd | 0 |
| .lnk | 0 |
| .reg | 0 |
| .vbs | 0 |
| .ps1 | 0 |

**No script files found.**

### 3. NesysService.exe Binary Analysis

NesysService.exe contains comprehensive evidence of its function:

| Component | Evidence |
|-----------|----------|
| **Service Control** | StartServiceCtrlDispatcherA, RegisterServiceCtrlHandlerA, SetServiceStatus |
| **Named Pipe** | `\\.\pipe\nesys_games`, CreateNamedPipeA, ConnectNamedPipe |
| **Certificate** | CertOpenStore, CertFindCertificateInStore, cert3.nesys.jp |
| **Network** | WSACreateEvent, WSAEventSelect, URL patterns |
| **Mutex** | CreateMutexA, ReleaseMutex |
| **Registry** | RegOpenKeyExA |
| **Process Creation** | CreateProcessA, GenerateConsoleCtrlEvent |

**NesysService is a Windows Service that requires external context.**

### 4. Missing System Drive Content

| Component | Status | Impact |
|-----------|--------|--------|
| Launcher executable | MISSING | Cannot determine startup sequence |
| Service registration | MISSING | NesysService not registered |
| Certificate store | MISSING | Cannot authenticate with NESYS |
| Registry | MISSING | Cannot read configuration |
| Startup shortcuts | MISSING | No startup folder placement |
| Scheduled tasks | MISSING | No task scheduler entries |
| Watchdog | MISSING | No crash recovery |
| Environment variables | MISSING | Cannot configure NESYS |
| NESYS runtime dependencies | MISSING | Cannot load NESYS functions |

### 5. Standalone Capability

| Capability | Status |
|------------|--------|
| Run without arguments | POSSIBLE |
| Run without parent | POSSIBLE |
| Run without service context | NOT_POSSIBLE |
| Run without certificates | NOT_POSSIBLE |
| Run without named pipe | NOT_POSSIBLE |
| Run without network | NOT_POSSIBLE |

**NesysService requires Windows Service context, certificate installation, and network access.**

---

## Documents Created

| Document | Path |
|----------|------|
| G12 Initial Baseline | docs/PHASE_2A_G12_INITIAL_BASELINE.md |
| Original Runtime Artifact Inventory | docs/ORIGINAL_RUNTIME_ARTIFACT_INVENTORY.md |
| Original Launcher Candidates | docs/ORIGINAL_LAUNCHER_CANDIDATES.md |
| Original Startup Sequence | docs/ORIGINAL_STARTUP_SEQUENCE.md |
| NesysService Invocation Evidence | docs/NESYSERVICE_INVOCATION_EVIDENCE.md |
| Original System Drive Gap Analysis | docs/ORIGINAL_SYSTEM_DRIVE_GAP_ANALYSIS.md |
| NesysService Standalone Capability | docs/NESYSERVICE_STANDALONE_CAPABILITY.md |

---

## Classification

**Primary**: `D_DRIVE_ONLY_BACKUP_CONFIRMED`

**Rationale**:
- Only D: drive content is present
- No C: drive content found
- No system drive components found
- No startup configuration found
- No registry found
- No certificate store found
- No Windows Service configuration found

---

## Safe Launch Test Decision

**Decision**: `PARTIAL_INVOCATION_NOT_SAFE_TO_TEST`

**Rationale**:
- Exact executable: CONFIRMED (NesysService.exe)
- Exact working directory: UNKNOWN
- Exact arguments: NONE REQUIRED
- Proven launch order: UNKNOWN
- Service registration: MISSING
- Certificate installation: MISSING

**Conclusion**: The invocation is incomplete. Service registration and certificate installation are missing. Not safe to test.

---

## Impact on NESYS Block

The D-drive only backup confirms that:

1. **No launcher** → Cannot determine how NesysService was started
2. **No service registration** → NesysService cannot be registered as a Windows Service
3. **No certificates** → NesysService cannot authenticate with NESYS servers
4. **No registry** → NesysService cannot read configuration
5. **No startup sequence** → Cannot determine startup order
6. **No watchdog** → Cannot recover from crashes

**The NESYS offline block cannot be resolved with the available content.**

---

## Recommendations

### Immediate

1. **Do NOT attempt to launch NesysService** - Service registration and certificate installation are missing
2. **Do NOT create fake named pipes** - Would not resolve the NESYS block
3. **Do NOT create fake OpenKey data** - Would not resolve the NESYS block
4. **Do NOT install certificates** - Would not resolve the NESYS block

### Long-term

1. **Seek original system drive** - Required for complete startup sequence
2. **Seek original launcher** - Required for startup configuration
3. **Seek certificate installation** - Required for NESYS authentication
4. **Seek service registration** - Required for Windows Service context

---

## Conclusion

Phase 2A-G12 confirms that the operator-owned Starwing Paradox content is a D-drive only backup. The original Windows system drive, launcher, startup configuration, certificate store, registry, and Windows Service configuration are missing.

**Classification**: `D_DRIVE_ONLY_BACKUP_CONFIRMED`

**The NESYS offline block cannot be resolved with the available content.**
