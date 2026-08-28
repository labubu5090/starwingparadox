# NesysService Safe Registration Assessment

**Phase**: 2A-G14  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

Service registration is NOT safe or complete. Critical items remain unresolved: service account, command-line arguments, required certificate identity, private-key dependency, installation-specific Registry identity, production-network behavior, service dependencies, executable authorization, and working-directory requirements.

---

## Decision

**Safe to Register**: `FALSE`

---

## Critical Unresolved Items

### 1. Service Account

| Property | Status | Impact |
|----------|--------|--------|
| Exact account | INFERRED (LocalSystem) | May require custom service account |
| Account permissions | NOT_SHOWN | Cannot determine required privileges |
| Account type | NOT_SHOWN | May require domain account |

**Status**: `UNRESOLVED`

### 2. Command-Line Arguments

| Property | Status | Impact |
|----------|--------|--------|
| Arguments | NOT_FOUND | Service does not use arguments |
| Mode selection | NOT_FOUND | Only service mode implemented |
| External arguments | NOT_SHOWN | May require external configuration |

**Status**: `UNRESOLVED` (external configuration may be required)

### 3. Required Certificate Identity

| Property | Status | Impact |
|----------|--------|--------|
| Store | CONFIRMED (MY\.Default) | Known |
| Subject | CONFIRMED (nesys) | Known |
| Issuer | NOT_FOUND | Cannot validate certificate chain |
| Thumbprint | NOT_FOUND | Cannot identify specific certificate |
| Private key | PROBABLY_REQUIRED | Cannot acquire private key |

**Status**: `UNRESOLVED` (issuer and thumbprint unknown)

### 4. Private-Key Dependency

| Property | Status | Impact |
|----------|--------|--------|
| Acquisition | NOT_SHOWN | Cannot acquire private key |
| Storage | NOT_SHOWN | Cannot locate private key |
| Usage | NOT_SHOWN | Cannot use private key |

**Status**: `UNRESOLVED` (private key acquisition not shown)

### 5. Installation-Specific Registry Identity

| Property | Status | Impact |
|----------|--------|--------|
| GameKind | NOT_SHOWN | Cannot determine game identifier |
| EventNextTime | NOT_SHOWN | Cannot determine event timing |
| ConditionTime | NOT_SHOWN | Cannot determine condition timing |
| TrafficCount | NOT_SHOWN | Cannot determine traffic count |
| LogLevel | NOT_SHOWN | Cannot determine logging level |
| NewsPath | NOT_SHOWN | Cannot determine news path |
| EventPath | NOT_SHOWN | Cannot determine event path |
| LogPath | NOT_SHOWN | Cannot determine log path |

**Status**: `UNRESOLVED` (default values unknown)

### 6. Production-Network Behavior

| Property | Status | Impact |
|----------|--------|--------|
| cert3.nesys.jp | UNRESOLVED | Cannot determine purpose |
| data.nesys.jp | UNRESOLVED | Cannot determine purpose |
| nesys.taito.co.jp | UNRESOLVED | Cannot determine purpose |
| fjm170920zero.nesica.net | UNRESOLVED | Cannot determine purpose |

**Status**: `UNRESOLVED` (hostname purposes unknown)

### 7. Service Dependencies

| Property | Status | Impact |
|----------|--------|--------|
| DependOnService | NOT_FOUND | No service dependencies found |
| Service group | NOT_FOUND | No service group |
| Network dependency | INFERRED | May require network stack |

**Status**: `UNRESOLVED` (exact dependencies unknown)

### 8. Executable Authorization

| Property | Status | Impact |
|----------|--------|--------|
| Digital signature | NOT_CHECKED | Cannot verify authenticity |
| Signature validation | NOT_CHECKED | Cannot validate signature |
| Certificate chain | NOT_CHECKED | Cannot validate chain |

**Status**: `UNRESOLVED` (executable authorization not verified)

### 9. Working-Directory Requirements

| Property | Status | Impact |
|----------|--------|--------|
| Working directory | NOT_REQUIRED | Service runs from system directory |
| File access | NOT_SHOWN | Cannot determine file access pattern |
| Directory creation | NOT_SHOWN | Cannot determine creation behavior |

**Status**: `UNRESOLVED` (file access pattern unknown)

---

## Evaluation Criteria

### Safe Registration Requirements

| Requirement | Status | Met |
|-------------|--------|-----|
| Service account known | INFERRED | NO |
| Command-line arguments known | NOT_FOUND | NO |
| Certificate identity known | PARTIAL | NO |
| Private-key dependency resolved | NOT_SHOWN | NO |
| Registry identity known | NOT_SHOWN | NO |
| Production-network behavior known | UNRESOLVED | NO |
| Service dependencies known | NOT_FOUND | NO |
| Executable authorization verified | NOT_CHECKED | NO |
| Working-directory requirements known | NOT_SHOWN | NO |

**All Requirements Met**: `NO`

---

## Risk Assessment

### High Risk

| Risk | Impact | Likelihood |
|------|--------|------------|
| Wrong service account | Service fails to start | HIGH |
| Missing certificate | Service cannot authenticate | HIGH |
| Missing private key | Service cannot authenticate | HIGH |
| Wrong registry values | Service reads incorrect config | HIGH |
| Production-network access | Service contacts external hosts | HIGH |

### Medium Risk

| Risk | Impact | Likelihood |
|------|--------|------------|
| Missing dependencies | Service fails to start | MEDIUM |
| Wrong working directory | Service cannot access files | MEDIUM |
| Missing file paths | Service cannot read/write files | MEDIUM |

### Low Risk

| Risk | Impact | Likelihood |
|------|--------|------------|
| Wrong error control | Service handles errors incorrectly | LOW |
| Wrong start type | Service starts at wrong time | LOW |
| Missing description | Service has no description | LOW |

---

## Conclusion

Service registration is NOT safe or complete. Critical items remain unresolved: service account, command-line arguments, required certificate identity, private-key dependency, installation-specific Registry identity, production-network behavior, service dependencies, executable authorization, and working-directory requirements.

**Classification**: `NOT_SAFE_TO_REGISTER`

The service cannot be safely registered without resolving critical unresolved items. "SCM can technically register an executable" ≠ "service registration is safe or correct".

---

## Recommendations

### Do NOT

| Action | Reason |
|--------|--------|
| Register NesysService with Windows SCM | Critical items unresolved |
| Run sc.exe create | Critical items unresolved |
| Run New-Service | Critical items unresolved |
| Call CreateService | Critical items unresolved |
| Start NesysService.exe | Critical items unresolved |
| Execute any original game binary | Critical items unresolved |
| Create HKLM Registry values | Critical items unresolved |
| Install or import certificates | Critical items unresolved |
| Export certificates or private keys | Critical items unresolved |
| Contact cert3.nesys.jp | Critical items unresolved |
| Redirect production hostnames | Critical items unresolved |
| Modify DNS or hosts file | Critical items unresolved |
| Suppress TLS or certificate validation | Critical items unresolved |
| Patch any executable | Critical items unresolved |
| Create a live named pipe | Critical items unresolved |
| Impersonate NESYS infrastructure | Critical items unresolved |

---

## G14 Audit Notes

This document was created in Phase 2A-G14 to evaluate whether future service registration could be considered safe and complete. The decision remains false because critical items are unresolved. "SCM can technically register an executable" ≠ "service registration is safe or correct".

## G16 Audit Notes

**Date**: 2026-08-28
**Phase**: 2A-G16

This document was reviewed during Phase 2A-G16 (Original Runtime Recovery Closure and Clean-room Compatibility Boundary). The following updates were applied:

1. **Recovery branch closed**: The original runtime recovery branch has been formally closed. No safe reconstruction is possible from the available backup.
2. **Safe registration remains FALSE**: All 9 safety criteria evaluated — ALL FAIL
3. **Decision record created**: ADR_ORIGINAL_NESYSERVICE_RECOVERY_CLOSURE.md documents the decision to close the recovery branch
4. **Clean-room boundary established**: An explicit security and authorization boundary has been established for the Python rewrite

The safe registration assessment remains FALSE. The recovery branch may be reopened ONLY when legitimate new evidence becomes available.
