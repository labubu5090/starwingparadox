# G14 Classification Mapping

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

The G14 classification `EXTERNAL_REGISTRATION_REQUIRED` is a project-specific refinement most closely corresponding to `SYSTEM_IMAGE_OR_INSTALLER_REQUIRED`. The mapping explains why the G14 classification was selected and how it maps to the predefined classification.

---

## G14 Classification

**Classification**: `EXTERNAL_REGISTRATION_REQUIRED`

**Definition**: NesysService.exe implements service mode only and contains no confirmed self-installation mechanism. Windows service registration was therefore performed by an external installer, deployment package, recovery image or equivalent provisioning process.

---

## Predefined Classification

**Closest Match**: `SYSTEM_IMAGE_OR_INSTALLER_REQUIRED`

**Definition**: Critical configuration is confirmed to originate from missing installer or system-drive state.

---

## Mapping Analysis

### Why G14 Classification Was Selected

| Factor | Evidence | Impact |
|--------|----------|--------|
| Self-installation | NOT_FOUND | Service cannot register itself |
| Installation APIs | NOT_FOUND | No OpenSCManager, CreateService |
| Registration mechanism | EXTERNAL | Must be performed externally |
| Critical items unresolved | YES | Cannot safely register |

**Rationale**: The G14 classification was selected because the service binary cannot self-register and requires external context that is not present in the operator-owned content.

### How It Maps to Predefined Classification

| G14 Classification | Predefined Classification | Mapping |
|--------------------|---------------------------|---------|
| EXTERNAL_REGISTRATION_REQUIRED | SYSTEM_IMAGE_OR_INSTALLER_REQUIRED | CLOSEST_MATCH |

**Mapping**: The G14 classification is a project-specific refinement of the predefined classification. Both indicate that critical configuration originates from missing external sources.

---

## Evidence Supporting Mapping

### Service Cannot Self-Register

| Evidence | Source | Confidence |
|----------|--------|------------|
| No OpenSCManagerA/W import | PE analysis | CONFIRMED |
| No CreateServiceA/W import | PE analysis | CONFIRMED |
| No DeleteService import | PE analysis | CONFIRMED |
| No ChangeServiceConfig import | PE analysis | CONFIRMED |
| Only service control APIs | PE analysis | CONFIRMED |

### External Registration Required

| Evidence | Source | Confidence |
|----------|--------|------------|
| Service registration MISSING | G12/G13/G14 | CONFIRMED |
| Certificate installation MISSING | G12/G13/G14 | CONFIRMED |
| Registry configuration MISSING | G12/G13/G14 | CONFIRMED |
| Startup configuration MISSING | G12/G13/G14 | CONFIRMED |

### Critical Items Unresolved

| Item | Status | Impact |
|------|--------|--------|
| Service account | INFERRED | May require custom account |
| Command-line arguments | NOT_FOUND | May require external config |
| Certificate identity | PARTIAL | Issuer and thumbprint unknown |
| Private-key dependency | NOT_SHOWN | Cannot acquire private key |
| Registry identity | NOT_SHOWN | Default values unknown |
| Production-network behavior | UNRESOLVED | Hostname purposes unknown |
| Service dependencies | NOT_FOUND | Exact dependencies unknown |
| Executable authorization | NOT_CHECKED | Signature not verified |
| Working-directory requirements | NOT_SHOWN | File access pattern unknown |

---

## Audit Trail

### G14 Classification Selection

| Step | Action | Result |
|------|--------|--------|
| 1 | Analyzed NesysService.exe | No self-installation code |
| 2 | Checked installation APIs | None found |
| 3 | Determined registration mechanism | EXTERNAL |
| 4 | Assessed safety | NOT SAFE OR COMPLETE |
| 5 | Selected classification | EXTERNAL_REGISTRATION_REQUIRED |

### G15 Classification Mapping

| Step | Action | Result |
|------|--------|--------|
| 1 | Reviewed G14 classification | EXTERNAL_REGISTRATION_REQUIRED |
| 2 | Compared to predefined classifications | SYSTEM_IMAGE_OR_INSTALLER_REQUIRED |
| 3 | Analyzed mapping | CLOSEST_MATCH |
| 4 | Documented rationale | Service cannot self-register |
| 5 | Created audit trail | This document |

---

## Why Not Other Classifications

### Not EXTERNAL_REGISTRATION_ARTIFACT_RECOVERED

| Reason | Evidence |
|--------|----------|
| No installer package found | G15 inventory |
| No deployment scripts found | G15 inventory |
| No recovery images found | G15 inventory |
| No service registration artifacts | G15 inventory |

### Not PARTIAL_EXTERNAL_REGISTRATION_EVIDENCE

| Reason | Evidence |
|--------|----------|
| No external registration evidence | G15 analysis |
| No scripts with service references | G15 analysis |
| No logs with installation evidence | G15 analysis |
| No configuration with registration data | G15 analysis |

### Not AUTHORIZED_INSTALLER_REQUIRED

| Reason | Evidence |
|--------|----------|
| No installer package found | G15 inventory |
| No installer metadata found | G15 analysis |
| No installation logs found | G15 analysis |

### Not AUTHORIZATION_BOUNDARY_REACHED

| Reason | Evidence |
|--------|----------|
| No credentials required | Analysis complete |
| No private keys required | Analysis complete |
| No production access required | Analysis complete |
| Analysis is read-only | Safety maintained |

### Not NO_NEW_REGISTRATION_EVIDENCE

| Reason | Evidence |
|--------|----------|
| G14 found new evidence | Service cannot self-register |
| G15 confirmed no evidence | No deployment artifacts found |
| Classification is valid | Mapping is correct |

---

## Conclusion

The G14 classification `EXTERNAL_REGISTRATION_REQUIRED` is a project-specific refinement most closely corresponding to `SYSTEM_IMAGE_OR_INSTALLER_REQUIRED`. The mapping explains why the G14 classification was selected (service cannot self-register) and how it maps to the predefined classification (closest match).

**Classification Mapping**: `EXTERNAL_REGISTRATION_REQUIRED` → `SYSTEM_IMAGE_OR_INSTALLER_REQUIRED` (CLOSEST_MATCH)

---

## G15 Audit Notes

This document was created in Phase 2A-G15 to map the G14 classification to predefined classifications. The mapping is documented with evidence and audit trail. The G14 classification is valid and correctly maps to the closest predefined classification.
