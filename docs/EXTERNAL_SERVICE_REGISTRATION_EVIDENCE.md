# External Service Registration Evidence

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

No direct evidence of external service registration was found in the operator-owned content. The service registration mechanism remains UNKNOWN. No scripts, configuration files, or logs contain evidence of NesysService installation or startup.

---

## Script and Configuration Inspection

### Scripts Found

| Type | Count | Service References | Registration Evidence |
|------|-------|-------------------|----------------------|
| .bat | 0 | NONE | NONE |
| .cmd | 0 | NONE | NONE |
| .ps1 | 8 | NONE | NONE (PostgreSQL tools) |
| .vbs | 0 | NONE | NONE |
| .js | 0 | NONE | NONE |

**No deployment scripts found.**

### Configuration Files Found

| File | Path | Service References | Registration Evidence |
|------|------|-------------------|----------------------|
| DefaultEngine.ini | WindowsNoEditor\AcrGame\Config\ | NONE | NONE |
| DefaultGame.ini | WindowsNoEditor\AcrGame\Config\ | NONE | NONE |
| DefaultInput.ini | WindowsNoEditor\AcrGame\Config\ | NONE | NONE |
| GameUserSettings.ini | D DRIVE CONTENTS\Saved\GalaxySaved\ | NONE | NONE |
| Engine.ini | D DRIVE CONTENTS\Saved\GalaxySaved\ | NONE | NONE |

**No service registration configuration found.**

---

## Log and Textual Residue

### Log Files Found

| File | Path | Size | Service References | Registration Evidence |
|------|------|------|-------------------|----------------------|
| Log.txt | D DRIVE CONTENTS\system\CmdFile\log\Log.txt | 1,725,914 | NONE | NONE |
| update.log | D DRIVE CONTENTS\system\update.log | 0 | NONE | NONE |

### Log.txt Analysis

| Pattern | Occurrences | Evidence |
|---------|-------------|----------|
| "service" | 0 | NONE |
| "install" | 0 | NONE |
| "NesysService" | 0 | NONE |
| "sc.exe" | 0 | NONE |
| "CreateService" | 0 | NONE |
| "startup" | 0 | NONE |
| "certificate" | 0 | NONE |
| "registry" | 0 | NONE |

**No service-related entries found in logs.**

### Log Content Summary

The Log.txt file contains update and command operations:
- Network function errors
- Update checks
- Command checks
- ZIPCOPY operations
- MKDIR operations

**No evidence of service installation or startup.**

---

## PE Resource and Signature Correlation

### NesysService.exe Resources

| Resource | Value | Evidence |
|----------|-------|----------|
| ProductName | NesysService | VERSIONINFO |
| FileDescription | NesysService | VERSIONINFO |
| CompanyName | Taito | VERSIONINFO |
| OriginalFilename | NesysService.exe | VERSIONINFO |
| InternalName | NesysService | VERSIONINFO |
| ProductVersion | 2.97(x64) 2017/11/07 | VERSIONINFO |
| FileVersion | 2.97(x64) 2017/11/07 | VERSIONINFO |
| PDB | NesysServiceCert_x64.pdb | Debug info |

**Analysis**: NesysService.exe is a service binary with version 2.97 from 2017. The PDB path indicates it was built with certificate support ("NesysServiceCert_x64.pdb").

### Installer API Imports

| API | Present | Evidence |
|-----|---------|----------|
| OpenSCManagerA | NO | NOT_FOUND |
| OpenSCManagerW | NO | NOT_FOUND |
| CreateServiceA | NO | NOT_FOUND |
| CreateServiceW | NO | NOT_FOUND |
| DeleteService | NO | NOT_FOUND |
| ChangeServiceConfigA | NO | NOT_FOUND |
| ChangeServiceConfigW | NO | NOT_FOUND |
| ChangeServiceConfig2A | NO | NOT_FOUND |
| ChangeServiceConfig2W | NO | NOT_FOUND |
| StartServiceCtrlDispatcherA | YES | Import table |
| RegisterServiceCtrlHandlerA | YES | Import table |
| SetServiceStatus | YES | Import table |

**Analysis**: NesysService.exe contains service control APIs but no installation APIs. It cannot register itself as a Windows Service.

---

## Service Configuration Reconstruction

### Recovered Properties

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Service name | NesysService | CONFIRMED | String reference |
| Binary path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | CONFIRMED | File exists |
| Service type | SERVICE_WIN32_OWN_PROCESS | INFERRED | Standard for standalone service |
| Start type | SERVICE_AUTO_START | INFERRED | Standard for game services |
| Error control | SERVICE_ERROR_NORMAL | INFERRED | Standard error handling |
| Account | LocalSystem | INFERRED | Needs network and cert access |
| Display name | NOT_FOUND | NOT_FOUND | No evidence |
| Description | NOT_FOUND | NOT_FOUND | No evidence |
| Dependencies | NOT_FOUND | NOT_FOUND | No evidence |
| Failure actions | NOT_FOUND | NOT_FOUND | No evidence |
| Working directory | NOT_REQUIRED | NOT_FOUND | No evidence |

### Unresolved Properties

| Property | Status | Impact |
|----------|--------|--------|
| Display name | NOT_FOUND | Service may appear differently in SCM |
| Description | NOT_FOUND | Service has no description |
| Dependencies | NOT_FOUND | Cannot determine startup order |
| Failure actions | NOT_FOUND | No automatic recovery |
| SID type | NOT_FOUND | Uses default configuration |
| Preshutdown timeout | NOT_FOUND | Uses default timeout |
| Event log source | NOT_FOUND | No event logging |
| Installation source | UNKNOWN | Cannot determine origin |
| Uninstall source | UNKNOWN | Cannot determine removal |

---

## Non-Secret Registry Provisioning

### Registry Values Found

| Value | Source Artifact | Declared Type | Declared Value | Classification |
|-------|-----------------|---------------|----------------|----------------|
| GameKind | NOT_FOUND | - | - | NOT_FOUND |
| EventNextTime | NOT_FOUND | - | - | NOT_FOUND |
| ConditionTime | NOT_FOUND | - | - | NOT_FOUND |
| TrafficCount | NOT_FOUND | - | - | NOT_FOUND |
| LogLevel | NOT_FOUND | - | - | NOT_FOUND |
| NewsPath | NOT_FOUND | - | - | NOT_FOUND |
| EventPath | NOT_FOUND | - | - | NOT_FOUND |
| LogPath | NOT_FOUND | - | - | NOT_FOUND |

**No registry provisioning data found in artifacts.**

---

## Startup Orchestration Evidence

### Startup Mechanisms Found

| Mechanism | Evidence | Confidence |
|-----------|----------|------------|
| Windows automatic service start | NOT_FOUND | NOT_FOUND |
| Delayed automatic service start | NOT_FOUND | NOT_FOUND |
| Startup-folder shortcut | NOT_FOUND | NOT_FOUND |
| Scheduled task | NOT_FOUND | NOT_FOUND |
| Launcher executable | NOT_FOUND | NOT_FOUND |
| Watchdog | NOT_FOUND | NOT_FOUND |
| Shell replacement | NOT_FOUND | NOT_FOUND |
| Kiosk startup | NOT_FOUND | NOT_FOUND |
| External cabinet-management | NOT_FOUND | NOT_FOUND |
| Installer-configured start | NOT_FOUND | NOT_FOUND |
| Recovery-image script | NOT_FOUND | NOT_FOUND |

**No startup orchestration evidence found.**

---

## Classification

**EXTERNAL_REGISTRATION_EVIDENCE**: `NO_EVIDENCE_FOUND`

**Rationale**:
- No deployment scripts found
- No configuration files with service references found
- No log entries with service installation evidence found
- No registry provisioning data found
- No startup orchestration evidence found
- NesysService.exe cannot self-register (no installation APIs)

---

## Conclusion

No direct evidence of external service registration was found in the operator-owned content. The service registration mechanism remains UNKNOWN. No scripts, configuration files, or logs contain evidence of NesysService installation or startup.

**Classification**: `NO_EXTERNAL_REGISTRATION_EVIDENCE`

The operator-owned content does not contain any evidence of how NesysService was registered or provisioned.

---

## G15 Audit Notes

This document was created in Phase 2A-G15 to identify external service registration evidence. No evidence was found in scripts, configuration files, logs, PE resources, or other artifacts. The service registration mechanism remains UNKNOWN.
