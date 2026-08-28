# Phase 2A-G15 Final Report

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  
**Classification**: `NO_NEW_REGISTRATION_EVIDENCE`  

---

## Executive Summary

Phase 2A-G15 performed a complete read-only forensic search of all operator-owned Starwing project content and original D-drive backup for evidence of the external mechanism that registered and provisioned NesysService.

**Finding**: No deployment artifacts, installer packages, recovery images, or service registration evidence were found. The complete in-scope search found no additional evidence beyond G14.

**Classification**: `NO_NEW_REGISTRATION_EVIDENCE`

---

## Key Findings

### 1. Deployment Artifact Inventory

| Category | Count | Notes |
|----------|-------|-------|
| Executables | 3 | Known three executables |
| Scripts (.bat, .cmd, .ps1, .vbs) | 0 | NONE |
| Archives (.zip, .7z, .rar, .iso) | 0 | NONE |
| Installers (.msi, .exe) | 0 | NONE |
| Disk images (.wim, .vhd, .vhdx) | 0 | NONE |
| Recovery images (.gho, .tib) | 0 | NONE |
| Registry files (.reg) | 0 | NONE |
| Certificate files | 0 | NONE |
| Service configuration | 0 | NONE |

**No deployment artifacts found.**

### 2. Installer and Image Candidates

| Candidate | Status | Analysis |
|-----------|--------|----------|
| AcrGame.inf | NOT_INSTALLER | Binary file without installer metadata |
| NesysService.exe | SUPPORT_SERVICE | Service binary, not installer |
| AcrGame.exe | GAME_EXECUTABLE | Game launcher, not installer |
| AcrGame-Win64-Shipping.exe | GAME_EXECUTABLE | Main game binary, not installer |

**No installer or image candidates found.**

### 3. External Service Registration Evidence

| Evidence Type | Status | Notes |
|---------------|--------|-------|
| Scripts with service references | NOT_FOUND | No deployment scripts |
| Logs with installation evidence | NOT_FOUND | No installation logs |
| Configurations with registration data | NOT_FOUND | No registration config |
| PE resources with installation APIs | NOT_FOUND | No installation APIs |
| Registry provisioning data | NOT_FOUND | No registry data |
| Startup orchestration evidence | NOT_FOUND | No startup evidence |

**No external registration evidence found.**

### 4. Service Configuration Reconstruction

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Service name | NesysService | CONFIRMED | String reference |
| Binary path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | CONFIRMED | File exists |
| Service type | SERVICE_WIN32_OWN_PROCESS | INFERRED | Standard |
| Start type | SERVICE_AUTO_START | INFERRED | Standard |
| Error control | SERVICE_ERROR_NORMAL | INFERRED | Standard |
| Account | LocalSystem | INFERRED | Standard |
| Display name | NOT_FOUND | NOT_FOUND | No evidence |
| Description | NOT_FOUND | NOT_FOUND | No evidence |
| Dependencies | NOT_FOUND | NOT_FOUND | No evidence |
| Failure actions | NOT_FOUND | NOT_FOUND | No evidence |

**Service configuration partially recovered.**

### 5. typex Registry Provisioning

| Value | Status | Evidence |
|-------|--------|----------|
| GameKind | NOT_FOUND | No artifact defines value |
| EventNextTime | NOT_FOUND | No artifact defines value |
| ConditionTime | NOT_FOUND | No artifact defines value |
| TrafficCount | NOT_FOUND | No artifact defines value |
| LogLevel | NOT_FOUND | No artifact defines value |
| NewsPath | NOT_FOUND | No artifact defines value |
| EventPath | NOT_FOUND | No artifact defines value |
| LogPath | NOT_FOUND | No artifact defines value |

**No registry provisioning evidence found.**

### 6. Startup Orchestration

| Mechanism | Status | Evidence |
|-----------|--------|----------|
| Windows automatic service start | NOT_FOUND | No service registration |
| Delayed automatic service start | NOT_FOUND | No service configuration |
| Startup-folder shortcut | NOT_FOUND | No .lnk files |
| Scheduled task | NOT_FOUND | No task files |
| Launcher executable | NOT_FOUND | No launcher binary |
| Watchdog | NOT_FOUND | No watchdog binary |
| Shell replacement | NOT_FOUND | No shell replacement |
| External cabinet-management | NOT_FOUND | No cabinet management |
| Installer-configured start | NOT_FOUND | No installer |
| Recovery-image script | NOT_FOUND | No recovery image |

**No startup orchestration evidence found.**

### 7. Authorized Recovery Source Matrix

| Source | Availability | Impact |
|--------|--------------|--------|
| Original C-drive image | NOT_FOUND | CRITICAL |
| Original physical system drive | NOT_FOUND | CRITICAL |
| Operator-created backup | AVAILABLE_BUT_INCOMPLETE | PARTIAL |
| Arcade distributor recovery image | NOT_FOUND | UNKNOWN |
| Authorized installer package | NOT_FOUND | UNKNOWN |
| Vendor deployment media | NOT_FOUND | UNKNOWN |
| Windows System32 service Registry hive | NOT_FOUND | CRITICAL |
| Exported service metadata | NOT_FOUND | CRITICAL |
| Old maintenance backup | NOT_FOUND | UNKNOWN |
| Installation log | NOT_FOUND | CRITICAL |
| Cabinet clone | NOT_FOUND | UNKNOWN |
| Legitimate spare cabinet image | NOT_FOUND | UNKNOWN |

**Most recovery sources NOT_AVAILABLE.**

### 8. G14 Classification Mapping

| G14 Classification | Predefined Classification | Mapping |
|--------------------|---------------------------|---------|
| EXTERNAL_REGISTRATION_REQUIRED | SYSTEM_IMAGE_OR_INSTALLER_REQUIRED | CLOSEST_MATCH |

**G14 classification maps to closest predefined classification.**

---

## Documents Created

| Document | Path |
|----------|------|
| G15 Initial Baseline | docs/PHASE_2A_G15_INITIAL_BASELINE.md |
| G15 Analysis Plan | docs/PHASE_2A_G15_ANALYSIS_PLAN.md |
| Deployment Artifact Inventory | docs/DEPLOYMENT_ARTIFACT_INVENTORY.md |
| Installer and Image Candidates | docs/INSTALLER_AND_IMAGE_CANDIDATES.md |
| External Service Registration Evidence | docs/EXTERNAL_SERVICE_REGISTRATION_EVIDENCE.md |
| NesysService Deployment Residue | docs/NESYSERVICE_DEPLOYMENT_RESIDUE.md |
| NesysService Startup Orchestration | docs/NESYSERVICE_STARTUP_ORCHESTRATION.md |
| typex Provisioning Evidence | docs/TYPEX_PROVISIONING_EVIDENCE.md |
| Authorized Recovery Source Matrix | docs/AUTHORIZED_RECOVERY_SOURCE_MATRIX.md |
| G14 Classification Mapping | docs/G14_CLASSIFICATION_MAPPING.md |
| G15 Final Report | docs/PHASE_2A_G15_FINAL_REPORT.md |

---

## Artifacts Created

| Artifact | Path |
|----------|------|
| Deployment Artifact Inventory | artifacts/phase_2a_g15/deployment_artifact_inventory.json |
| External Registration Evidence | artifacts/phase_2a_g15/external_registration_evidence.json |
| Startup Orchestration | artifacts/phase_2a_g15/startup_orchestration.json |
| Recovery Source Matrix | artifacts/phase_2a_g15/recovery_source_matrix.json |

---

## Classification

**Primary**: `NO_NEW_REGISTRATION_EVIDENCE`

**Rationale**:
- No deployment artifacts found
- No installer packages found
- No recovery images found
- No service registration evidence found
- No registry provisioning data found
- No startup orchestration evidence found
- Most recovery sources NOT_AVAILABLE
- Complete in-scope search found no additional evidence beyond G14

---

## SHA-256 Integrity Confirmation

| Executable | SHA-256 | Status |
|------------|---------|--------|
| NesysService.exe | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` | UNCHANGED |
| AcrGame.exe | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` | UNCHANGED |
| AcrGame-Win64-Shipping.exe | `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4` | UNCHANGED |

**All executables unchanged. No game files modified.**

---

## Quality Gates

| Gate | Result |
|------|--------|
| pytest | 834 passed, 1 skipped, 0 failed |
| Ruff | 0 errors |
| Mypy | 0 errors on 64 source files |
| Game files modified | NO |
| Key material recorded | NO |
| Certificates installed | NO |
| Registry values created | NO |
| Fake named pipes created | NO |
| D: mapping left active | NO |

---

## Safety Boundary Confirmation

| Boundary | Status |
|----------|--------|
| Static analysis only | CONFIRMED |
| No patching or rewriting | CONFIRMED |
| No bypassing authentication | CONFIRMED |
| No suppressing certificate validation | CONFIRMED |
| No forging or installing certificates | CONFIRMED |
| No extracting private keys | CONFIRMED |
| No contacting production NESYS hosts | CONFIRMED |
| No emulating production infrastructure | CONFIRMED |
| No creating fake named pipes | CONFIRMED |
| No registering NesysService | CONFIRMED |
| No creating Registry values | CONFIRMED |
| No executing binaries | CONFIRMED |
| No altering Windows services | CONFIRMED |
| No recording secrets | CONFIRMED |
| No archive mounting | CONFIRMED |
| No image booting | CONFIRMED |
| No installer execution | CONFIRMED |

---

## Final Response

1. **Commit hash**: TBD
2. **Final classification**: `NO_NEW_REGISTRATION_EVIDENCE`
3. **Created and updated files**: 11 documents, 4 artifacts
4. **pytest, Ruff and Mypy results**: 834 passed, 0 errors, 0 errors
5. **Original executable SHA-256 integrity confirmation**: All unchanged
6. **Total deployment candidates found**: 0
7. **Installer candidates and confidence**: NONE
8. **Disk-image or recovery candidates and confidence**: NONE
9. **Service registration properties newly recovered**: NONE
10. **Service properties still unresolved**: Display name, description, dependencies, failure actions, SID type, preshutdown timeout, event log source, installation source, uninstall source
11. **Evidence of installation or provisioning scripts**: NONE
12. **Registry provisioning evidence**: NONE
13. **Startup orchestration evidence**: NONE
14. **Certificate-related deployment evidence**: NONE
15. **G14 classification mapping result**: EXTERNAL_REGISTRATION_REQUIRED → SYSTEM_IMAGE_OR_INSTALLER_REQUIRED (CLOSEST_MATCH)
16. **safe_to_register result**: FALSE
17. **Authorized recovery sources available or missing**: Only operator-created D-drive backup available (incomplete). All other sources NOT_AVAILABLE.
18. **Exact recommended next phase**: Phase 2A-G16: Service Registration Feasibility Assessment

---

## Conclusion

Phase 2A-G15 performed a complete read-only forensic search of all operator-owned Starwing project content and original D-drive backup for evidence of the external mechanism that registered and provisioned NesysService.

**Finding**: No deployment artifacts, installer packages, recovery images, or service registration evidence were found. The complete in-scope search found no additional evidence beyond G14.

**Classification**: `NO_NEW_REGISTRATION_EVIDENCE`

**The service registration and provisioning state cannot be recovered from the available content.**
