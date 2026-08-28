# NesysService Standalone Capability

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Summary

NesysService.exe is a Windows Service that requires external context to function. It is NOT standalone-capable. It requires:
- Windows Service registration
- Certificate store access
- Named pipe server
- Network access to cert3.nesys.jp

---

## Static Evidence Analysis

### What NesysService Contains

| Component | Evidence | Strength |
|-----------|----------|----------|
| **Service Control** | StartServiceCtrlDispatcherA, RegisterServiceCtrlHandlerA, SetServiceStatus | CONFIRMED |
| **Named Pipe Server** | `\\.\pipe\nesys_games`, CreateNamedPipeA, ConnectNamedPipe | CONFIRMED |
| **Certificate Operations** | CertOpenStore, CertFindCertificateInStore, cert3.nesys.jp | CONFIRMED |
| **Network Operations** | WSACreateEvent, WSAEventSelect, URL patterns | CONFIRMED |
| **Mutex** | CreateMutexA, ReleaseMutex | CONFIRMED |
| **Registry** | RegOpenKeyExA | CONFIRMED |
| **Process Creation** | CreateProcessA, GenerateConsoleCtrlEvent | CONFIRMED |

### What NesysService Does NOT Contain

| Component | Evidence | Strength |
|-----------|----------|----------|
| **Command-line parsing** | No argv processing found | CONFIRMED |
| **Parent process check** | No parent process validation | CONFIRMED |
| **Named event** | Only mutex found | CONFIRMED |
| **Shared memory** | No shared memory API | CONFIRMED |
| **Cabinet IO device** | No USBIO reference | CONFIRMED |
| **Cabinet network adapter** | No network adapter reference | CONFIRMED |

---

## Capability Assessment

### Standalone Capability

| Capability | Status | Evidence |
|------------|--------|----------|
| **Run without arguments** | POSSIBLE | No argv parsing found |
| **Run without parent** | POSSIBLE | No parent process check |
| **Run without service context** | NOT_POSSIBLE | StartServiceCtrlDispatcherA requires service context |
| **Run without certificates** | NOT_POSSIBLE | CertOpenStore, cert3.nesys.jp required |
| **Run without named pipe** | NOT_POSSIBLE | `\\.\pipe\nesys_games` required |
| **Run without network** | NOT_POSSIBLE | cert3.nesys.jp communication required |

### Required Context

| Context | Requirement | Evidence |
|---------|-------------|----------|
| **Windows Service** | REQUIRED | StartServiceCtrlDispatcherA |
| **Certificate Store** | REQUIRED | CertOpenStore, CertFindCertificateInStore |
| **Named Pipe** | REQUIRED | `\\.\pipe\nesys_games` |
| **Network** | REQUIRED | cert3.nesys.jp |
| **Mutex** | REQUIRED | CreateMutexA (single instance) |
| **Registry** | REQUIRED | RegOpenKeyExA |

---

## Invocation Requirements

### Exact Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Exact executable** | NesysService.exe | CONFIRMED |
| **Exact working directory** | Unknown | No evidence found |
| **Exact arguments** | None required | No argv parsing found |
| **Service registration** | REQUIRED | Windows Service context |
| **Certificate installation** | REQUIRED | cert3.nesys.jp certificates |
| **Named pipe creation** | REQUIRED | `\\.\pipe\nesys_games` |
| **Network access** | REQUIRED | cert3.nesys.jp |
| **Registry access** | REQUIRED | RegOpenKeyExA |

### Missing Requirements

| Requirement | Status | Impact |
|-------------|--------|--------|
| **Service registration** | MISSING | Cannot register as Windows Service |
| **Certificate installation** | MISSING | Cannot authenticate with NESYS |
| **Startup sequence** | MISSING | Cannot determine launch order |
| **Configuration** | MISSING | Cannot configure service parameters |

---

## Classification

**STANDALONE_CAPABILITY**: `PARENT_CONTEXT_REQUIRED`

**Rationale**:
- NesysService.exe is a Windows Service (StartServiceCtrlDispatcherA)
- Requires certificate store access (CertOpenStore, cert3.nesys.jp)
- Requires named pipe server (`\\.\pipe\nesys_games`)
- Requires network access (cert3.nesys.jp)
- No command-line arguments required
- No parent process required
- No shared memory required
- No cabinet IO device required

**Conclusion**: NesysService.exe requires Windows Service context, certificate installation, and network access. It is NOT standalone-capable.

---

## Safe Launch Test Decision

| Criterion | Status | Notes |
|-----------|--------|-------|
| **Exact executable** | CONFIRMED | NesysService.exe |
| **Exact working directory** | UNKNOWN | No evidence found |
| **Exact arguments** | NONE REQUIRED | No argv parsing found |
| **Proven launch order** | UNKNOWN | No startup sequence found |
| **No fabricated values** | CONFIRMED | No values invented |
| **No authentication bypass** | CONFIRMED | No bypass attempted |
| **No Registry modification** | CONFIRMED | No Registry entries created |
| **No certificate installation** | CONFIRMED | No certificates installed |

**DECISION**: `PARTIAL_INVOCATION_NOT_SAFE_TO_TEST`

**Rationale**:
- Exact executable: CONFIRMED
- Exact working directory: UNKNOWN
- Exact arguments: NONE REQUIRED
- Proven launch order: UNKNOWN
- Service registration: MISSING
- Certificate installation: MISSING

**Conclusion**: The invocation is incomplete. Service registration and certificate installation are missing. Not safe to test.
