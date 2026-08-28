# Phase 2A-G14 Final Report

**Phase**: 2A-G14  
**Date**: 2026-08-28  
**Status**: COMPLETE  
**Classification**: `EXTERNAL_REGISTRATION_REQUIRED`  

---

## Executive Summary

Phase 2A-G14 performed offline service registration reconstruction and certificate dependency classification for NesysService.exe. The service does NOT contain self-installation code. Service registration was performed externally (installer, system image, or deployment package). The exact certificate dependency category is unresolved — private key acquisition and TLS client-certificate attachment are NOT_SHOWN.

**Classification**: `EXTERNAL_REGISTRATION_REQUIRED`

---

## Key Findings

### 1. Service Registration Contract

| Component | Finding | Confidence |
|-----------|---------|------------|
| Service name | NesysService | CONFIRMED |
| Binary path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | CONFIRMED |
| Service type | SERVICE_WIN32_OWN_PROCESS | INFERRED |
| Start type | SERVICE_AUTO_START | INFERRED |
| Error control | SERVICE_ERROR_NORMAL | INFERRED |
| Account | LocalSystem | INFERRED |
| Self-installation | NOT_FOUND | CONFIRMED |
| Registration mechanism | EXTERNAL | CONFIRMED |

### 2. Command-Line Modes

| Component | Finding | Confidence |
|-----------|---------|------------|
| Service mode | YES | CONFIRMED |
| Console mode | NOT_FOUND | CONFIRMED |
| Debug mode | NOT_FOUND | CONFIRMED |
| Install mode | NOT_FOUND | CONFIRMED |
| Uninstall mode | NOT_FOUND | CONFIRMED |
| Repair mode | NOT_FOUND | CONFIRMED |

### 3. Certificate Data Flow

| Component | Finding | Confidence |
|-----------|---------|------------|
| Certificate store | MY\.Default | CONFIRMED |
| Subject | nesys | CONFIRMED |
| Private key acquisition | NOT_SHOWN | NOT_SHOWN |
| TLS attachment | NOT_SHOWN | NOT_SHOWN |
| Server validation | NOT_SHOWN | NOT_SHOWN |
| cert3.nesys.jp purpose | UNRESOLVED | UNRESOLVED |

### 4. Registry Semantics

| Value | Classification | Mutability | Confidence |
|-------|----------------|------------|------------|
| GameKind | INSTALLATION_IDENTITY | STATIC | HIGH |
| EventNextTime | RUNTIME_STATE | RUNTIME_STATE | HIGH |
| ConditionTime | RUNTIME_STATE | RUNTIME_STATE | HIGH |
| TrafficCount | RUNTIME_STATE | RUNTIME_STATE | HIGH |
| LogLevel | LOGGING_CONFIGURATION | STATIC | HIGH |
| NewsPath | FILE_PATH | STATIC | HIGH |
| EventPath | FILE_PATH | STATIC | HIGH |
| LogPath | FILE_PATH | STATIC | HIGH |

### 5. File-Path Dependencies

| Value | Candidate Directory | Confidence |
|-------|---------------------|------------|
| NewsPath | X:\StarwingParadox\D DRIVE CONTENTS\system\DUA\news | POSSIBLE |
| EventPath | X:\StarwingParadox\D DRIVE CONTENTS\system\DUA\event | POSSIBLE |
| LogPath | X:\StarwingParadox\D DRIVE CONTENTS\system\CmdFile\log | POSSIBLE |

### 6. Safe-to-Register Decision

**Safe to Register**: `FALSE`

**Critical Unresolved Items**:
- Service account (INFERRED)
- Command-line arguments (NOT_FOUND)
- Certificate identity (PARTIAL)
- Private-key dependency (NOT_SHOWN)
- Registry identity (NOT_SHOWN)
- Production-network behavior (UNRESOLVED)
- Service dependencies (NOT_FOUND)
- Executable authorization (NOT_CHECKED)
- Working-directory requirements (NOT_SHOWN)

---

## Documents Created

| Document | Path |
|----------|------|
| G14 Initial Baseline | docs/PHASE_2A_G14_INITIAL_BASELINE.md |
| G14 Analysis Plan | docs/PHASE_2A_G14_ANALYSIS_PLAN.md |
| Service Registration Contract | docs/NESYSERVICE_REGISTRATION_CONTRACT.md |
| Command-Line Modes | docs/NESYSERVICE_COMMAND_LINE_MODES.md |
| Certificate Data Flow | docs/NESYSERVICE_CERTIFICATE_DATA_FLOW.md |
| cert3.nesys.jp Relationship | docs/CERT3_NESYS_JP_RELATIONSHIP.md |
| typex Registry Semantics | docs/TYPEX_REGISTRY_SEMANTICS.md |
| File-Path Dependencies | docs/NESYSERVICE_FILE_PATH_DEPENDENCIES.md |
| Safe Registration Assessment | docs/NESYSERVICE_SAFE_REGISTRATION_ASSESSMENT.md |
| G14 Final Report | docs/PHASE_2A_G14_FINAL_REPORT.md |

---

## Artifacts Created

| Artifact | Path |
|----------|------|
| Registration Manifest | artifacts/phase_2a_g14/nesys_service_registration_manifest.json |
| Certificate Dependency | artifacts/phase_2a_g14/certificate_dependency.json |
| Registry Semantics | artifacts/phase_2a_g14/registry_semantics.json |

---

## G13 Corrections Applied

| Document | Correction | Reason |
|----------|------------|--------|
| PHASE_2A_G13_FINAL_REPORT.md | Removed "connects to cert3.nesys.jp" | Hostname reference ≠ connection |
| PHASE_2A_G13_FINAL_REPORT.md | Removed "retrieves certificate" | Store API ≠ retrieval |
| NESYSERVICE_CERTIFICATE_CONTRACT.md | Corrected "retrieve NESYS certificates" | Overstated evidence |
| NESYSERVICE_CERTIFICATE_CONTRACT.md | Corrected "Private key: (required)" | Inference, not confirmed |
| NESYSERVICE_NETWORK_CONTRACT.md | Corrected "connects to cert3.nesys.jp for certificate operations" | Overstated evidence |
| artifacts/phase_2a_g13/runtime_contract.json | Updated service, certificates, and network sections | Corrected overstated claims |

---

## Classification

**Primary**: `EXTERNAL_REGISTRATION_REQUIRED`

**Rationale**:
- Service identity: CONFIRMED
- Binary path: CONFIRMED
- Self-installation: NOT_FOUND
- Registration mechanism: EXTERNAL
- Certificate store: CONFIRMED
- Private key: NOT_SHOWN
- cert3.nesys.jp: UNRESOLVED
- Registry semantics: HIGH
- File dependencies: POSSIBLE
- Safe to register: FALSE

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
| No executing binaries through IDA debugger | CONFIRMED |
| No altering Windows services | CONFIRMED |
| No recording secrets or key material | CONFIRMED |

---

## Confirmed Evidence

### Service Identity

| Property | Value | Evidence |
|----------|-------|----------|
| Service name | NesysService | String reference |
| Binary path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | File exists |
| SHA-256 | 3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F | Verified |
| ServiceMain | swp_service_main | String reference |
| Control handler | swp_service_ctrl_handler | String reference |

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

### Named Pipe

| Property | Value | Evidence |
|----------|-------|----------|
| Pipe name | \\.\pipe\nesys_games | String reference |
| Server | NesysService.exe | CreateNamedPipeA |
| Client | AcrGame-Win64-Shipping.exe | ConnectNamedPipe |

---

## Unresolved Items

| Item | Status | Impact |
|------|--------|--------|
| Service registration mechanism | EXTERNAL | Cannot self-register |
| Display name | NOT_FOUND | Service may appear differently |
| Description | NOT_FOUND | Service has no description |
| Failure actions | NOT_FOUND | No automatic recovery |
| SID type | NOT_FOUND | Uses default configuration |
| Preshutdown timeout | NOT_FOUND | Uses default timeout |
| Default registry values | NOT_SHOWN | Cannot determine defaults |
| Registry validation | NOT_SHOWN | Cannot validate values |
| File path requirements | NOT_SHOWN | Cannot determine exact paths |
| Certificate private key | NOT_SHOWN | Cannot acquire private key |
| cert3.nesys.jp purpose | UNRESOLVED | Cannot determine relationship |
| Network operations | UNRESOLVED | Cannot determine operations |
| TLS attachment | NOT_SHOWN | Cannot attach certificate |

---

## Conclusion

Phase 2A-G14 performed offline service registration reconstruction and certificate dependency classification for NesysService.exe. The service does NOT contain self-installation code. Service registration was performed externally (installer, system image, or deployment package). The exact certificate dependency category is unresolved — private key acquisition and TLS client-certificate attachment are NOT_SHOWN.

**Classification**: `EXTERNAL_REGISTRATION_REQUIRED`

**Service registration is NOT safe or complete. Critical items remain unresolved.**

---

## Recommended Next Phase

**Phase 2A-G15**: External Registration Mechanism Investigation

**Objective**: Determine whether the external registration mechanism can be identified from available evidence, or whether system-drive content is required.

**Rationale**: The service does not contain self-installation code. The exact external mechanism (installer, system image, or deployment package) is UNKNOWN from available evidence. The next phase should investigate whether this mechanism can be identified without system-drive content.
