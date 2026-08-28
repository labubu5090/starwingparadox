# NesysService Deployment Residue

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

No deployment residue was found for NesysService.exe. The service binary exists in the D-drive backup but contains no installation logic, no configuration files, no certificates, and no deployment scripts. The service requires external context that is not present in the operator-owned content.

---

## NesysService.exe Binary Analysis

### Binary Properties

| Property | Value | Evidence |
|----------|-------|----------|
| Path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | File exists |
| Size | 548,352 bytes | File size |
| SHA-256 | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` | Verified |
| Architecture | PE32+ (64-bit) | PE header |
| Product name | NesysService | VERSIONINFO |
| Company | Taito | VERSIONINFO |
| PE subsystem | Console | PE header |
| Version | 2.97(x64) 2017/11/07 | VERSIONINFO |
| PDB | NesysServiceCert_x64.pdb | Debug info |

### Service Control APIs

| API | Import | Usage |
|-----|--------|-------|
| StartServiceCtrlDispatcherA | YES | Connects ServiceMain to SCM |
| RegisterServiceCtrlHandlerA | YES | Registers service control handler |
| SetServiceStatus | YES | Updates service state |

### Installation APIs

| API | Import | Usage |
|-----|--------|-------|
| OpenSCManagerA | NO | NOT_FOUND |
| OpenSCManagerW | NO | NOT_FOUND |
| CreateServiceA | NO | NOT_FOUND |
| CreateServiceW | NO | NOT_FOUND |
| DeleteService | NO | NOT_FOUND |
| ChangeServiceConfigA | NO | NOT_FOUND |
| ChangeServiceConfigW | NO | NOT_FOUND |
| ChangeServiceConfig2A | NO | NOT_FOUND |
| ChangeServiceConfig2W | NO | NOT_FOUND |

**Conclusion**: NesysService.exe contains service control APIs but no installation APIs. It cannot register itself as a Windows Service.

---

## Service Directory Contents

### Directory: X:\StarwingParadox\D DRIVE CONTENTS\system\Service\

| File | Size | Notes |
|------|------|-------|
| NesysService.exe | 548,352 | Service binary |

**No other files in Service directory.** No DLLs, no config files, no certificates, no scripts.

---

## Deployment Artifacts Found

| Artifact | Status | Notes |
|----------|--------|-------|
| Installer package | NOT_FOUND | No .msi, .exe installer |
| Installation script | NOT_FOUND | No .bat, .cmd, .ps1 |
| Registry file | NOT_FOUND | No .reg file |
| Certificate files | NOT_FOUND | No .cer, .pfx, .pem |
| Configuration files | NOT_FOUND | No .ini, .xml, .json |
| Service wrapper | NOT_FOUND | No wrapper executable |
| Uninstall script | NOT_FOUND | No removal script |
| README or documentation | NOT_FOUND | No installation guide |

**No deployment residue found.**

---

## Service Registration Requirements

### Required Context (Missing)

| Requirement | Status | Impact |
|-------------|--------|--------|
| Windows Service registration | MISSING | Cannot register with SCM |
| Certificate installation | MISSING | Cannot authenticate with NESYS |
| Registry configuration | MISSING | Cannot read configuration |
| Service account | MISSING | Cannot determine logon rights |
| Service dependencies | MISSING | Cannot determine startup order |
| Service recovery | MISSING | Cannot restart on failure |
| Working directory | MISSING | Cannot access files |
| Environment variables | MISSING | Cannot configure runtime |

### Service Binary Requirements

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Named pipe server | CONFIRMED | CreateNamedPipeA import |
| Certificate store access | CONFIRMED | CertOpenStore import |
| Registry access | CONFIRMED | RegOpenKeyExA import |
| Network access | CONFIRMED | WinHTTP imports |
| Mutex creation | CONFIRMED | CreateMutexA import |
| Process creation | CONFIRMED | CreateProcessA import |

---

## Service Startup Requirements

### Required Sequence (Missing)

```
1. Windows boots
2. SCM starts NesysService.exe (if registered)
3. ServiceMain called
4. RegisterServiceCtrlHandlerA called
5. SetServiceStatus(SERVICE_START_PENDING)
6. CreateMutexA
7. WSAStartup
8. CreateNamedPipeA
9. Start worker threads
10. SetServiceStatus(SERVICE_RUNNING)
11. Service enters main loop
```

### Missing Steps

| Step | Status | Impact |
|------|--------|--------|
| Service registration | MISSING | SCM cannot start service |
| Certificate installation | MISSING | Service cannot authenticate |
| Registry configuration | MISSING | Service cannot read config |
| Service account | MISSING | Service cannot log on |
| Service dependencies | MISSING | Service cannot start |

---

## Service Runtime Requirements

### Named Pipe

| Property | Value | Evidence |
|----------|-------|----------|
| Pipe name | \\.\pipe\nesys_games | String reference |
| Server | NesysService.exe | CreateNamedPipeA |
| Client | AcrGame-Win64-Shipping.exe | ConnectNamedPipe |
| Protocol | Command-response (LCOMMAND/SCOMMAND) | String references |

### Certificate Store

| Property | Value | Evidence |
|----------|-------|----------|
| Store | MY\.Default | String reference |
| Subject | nesys | String reference |
| Private key | PROBABLY_REQUIRED | Inference |

### Registry

| Property | Value | Evidence |
|----------|-------|----------|
| Key | HKLM\SOFTWARE\taito\typex | String reference |
| Values | 8 values (5 DWORD, 3 SZ) | String references |

### Network

| Property | Value | Evidence |
|----------|-------|----------|
| cert3.nesys.jp | UNRESOLVED | Hostname reference |
| data.nesys.jp | UNRESOLVED | Hostname reference |
| nesys.taito.co.jp | UNRESOLVED | Hostname reference |
| fjm170920zero.nesica.net | UNRESOLVED | Hostname reference |

---

## Classification

**DEPLOYMENT_RESIDUE**: `NOT_FOUND`

**Rationale**:
- No installer package found
- No installation scripts found
- No configuration files found
- No certificate files found
- No registry files found
- No service wrapper found
- No documentation found
- Service binary cannot self-register

---

## Conclusion

No deployment residue was found for NesysService.exe. The service binary exists in the D-drive backup but contains no installation logic, no configuration files, no certificates, and no deployment scripts. The service requires external context that is not present in the operator-owned content.

**Classification**: `NO_DEPLOYMENT_RESIDUE`

The operator-owned content does not contain any deployment artifacts for NesysService.

---

## G15 Audit Notes

This document was created in Phase 2A-G15 to identify NesysService deployment residue. No deployment residue was found. The service binary exists but cannot self-register and requires external context that is not present.
