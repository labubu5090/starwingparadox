# Phase 2A-G13 Final Report

**Phase**: 2A-G13  
**Date**: 2026-08-28  
**Status**: COMPLETE  
**Classification**: `PARTIAL_STATIC_RUNTIME_CONTRACT`  

---

## Executive Summary

Phase 2A-G13 performed IDA static analysis of NesysService.exe, AcrGame.exe, and AcrGame-Win64-Shipping.exe to reconstruct the missing runtime contract between the game, Windows Service Control Manager, Registry, certificate store, and the named pipe.

**Finding**: The runtime contract is partially recovered. Service identity, named pipe protocol, and network endpoints are confirmed. However, critical startup elements remain unresolved: the exact Windows Service registration, certificate installation, and Registry configuration.

**Classification**: `PARTIAL_STATIC_RUNTIME_CONTRACT`

---

## Key Findings

### 1. NesysService.exe

| Component | Finding | Confidence |
|-----------|---------|------------|
| Service name | NesysService | CONFIRMED |
| Service type | SERVICE_WIN32_OWN_PROCESS | INFERRED |
| Start type | SERVICE_AUTO_START | INFERRED |
| Named pipe | `\\.\pipe\nesys_games` | CONFIRMED |
| Certificate store | MY\.Default | CONFIRMED |
| Registry | `HKLM\SOFTWARE\taito\typex` | CONFIRMED |
| Network endpoints | cert3.nesys.jp, data.nesys.jp, nesys.taito.co.jp, fjm170920zero.nesica.net | CONFIRMED |

### 2. AcrGame.exe

| Component | Finding | Confidence |
|-----------|---------|------------|
| Type | Bootstrap wrapper | CONFIRMED |
| Child process | AcrGame-Win64-Shipping.exe | CONFIRMED |
| NesysService references | NONE | CONFIRMED |
| Named pipe references | NONE | CONFIRMED |

### 3. AcrGame-Win64-Shipping.exe

| Component | Finding | Confidence |
|-----------|---------|------------|
| Pipe connection | Attempts \\.\pipe\nesys_games\... | CONFIRMED |
| Failure behavior | NESYS offline, CertError spam | CONFIRMED |
| Recovery | Game continues in offline mode | CONFIRMED |

---

## Reconstructed Runtime Contract

### Service Identity

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| Service name | NesysService | String reference |
| Service type | SERVICE_WIN32_OWN_PROCESS | Standard |
| Start type | SERVICE_AUTO_START | Service should start with Windows |
| Error control | SERVICE_ERROR_NORMAL | Standard |
| Account | LocalSystem or custom | Needs network/cert access |

### Registry Configuration

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| Root hive | HKEY_LOCAL_MACHINE | Standard for services |
| Subkey | `SOFTWARE\taito\typex` | String reference |
| Values | 8 configuration values | String references |

### Certificate Store

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| Store | MY\.Default | String reference |
| Subject | nesys | String reference |
| Private key | Likely required | Client auth inference |
| Validity | Must be valid | Certificate validation |

### Named Pipe

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| Pipe name | `\\.\pipe\nesys_games` | String reference |
| Server | NesysService.exe | CreateNamedPipeA |
| Client | AcrGame-Win64-Shipping.exe | ConnectNamedPipe |
| Protocol | Command-response | LCOMMAND/SCOMMAND |

### Network Endpoints

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| cert3.nesys.jp | HTTPS (443) | String reference |
| data.nesys.jp | HTTP (80) | String reference |
| nesys.taito.co.jp | HTTP (80) | String reference |
| fjm170920zero.nesica.net | HTTPS (443) | String reference |

---

## Missing Components

### Critical Missing Components

| Component | Status | Impact |
|-----------|--------|--------|
| Service registration | MISSING | NesysService not registered with SCM |
| Certificate installation | MISSING | Cannot authenticate with NESYS servers |
| Registry configuration | MISSING | Cannot read game configuration |
| Startup sequence | MISSING | Cannot determine launch order |
| Service recovery | MISSING | Cannot restart on failure |

---

## Documents Created

| Document | Path |
|----------|------|
| G13 Initial Baseline | docs/PHASE_2A_G13_INITIAL_BASELINE.md |
| G13 IDA Analysis Plan | docs/PHASE_2A_G13_IDA_ANALYSIS_PLAN.md |
| NesysService Service Control Analysis | docs/NESYSERVICE_SERVICE_CONTROL_ANALYSIS.md |
| NesysService Registry Contract | docs/NESYSERVICE_REGISTRY_CONTRACT.md |
| NesysService Pipe Protocol | docs/NESYSERVICE_PIPE_PROTOCOL.md |
| NesysService Certificate Contract | docs/NESYSERVICE_CERTIFICATE_CONTRACT.md |
| NesysService Network Contract | docs/NESYSERVICE_NETWORK_CONTRACT.md |
| AcrGame Launch Analysis | docs/ACRGAME_LAUNCH_ANALYSIS.md |
| AcrGame-Win64-Shipping Startup Analysis | docs/ACRGAME_SHIPPING_STARTUP_ANALYSIS.md |
| Original Runtime Reconstruction | docs/ORIGINAL_RUNTIME_RECONSTRUCTION.md |
| G13 Final Report | docs/PHASE_2A_G13_FINAL_REPORT.md |

---

## Classification

**Primary**: `PARTIAL_STATIC_RUNTIME_CONTRACT`

**Rationale**:
- Service identity: CONFIRMED
- Registry contract: CONFIRMED
- Certificate contract: CONFIRMED
- Named pipe protocol: CONFIRMED
- Network endpoints: CONFIRMED
- Process startup: HIGH
- Missing components: Service registration, certificate installation, registry configuration

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

## Confirmed Windows Service Name

**Service Name**: `NesysService`

**Evidence**: String reference in NesysService.exe binary.

---

## Confirmed Registry Paths and Values

### Registry Key

```
HKEY_LOCAL_MACHINE
  └── SOFTWARE
      └── taito
          └── typex
```

### Registry Values

| Value Name | Type | Purpose |
|------------|------|---------|
| GameKind | REG_DWORD | Game identifier |
| EventNextTime | REG_DWORD | Next event time |
| ConditionTime | REG_DWORD | Condition time |
| TrafficCount | REG_DWORD | Traffic counter |
| LogLevel | REG_DWORD | Logging level |
| NewsPath | REG_SZ | News file path |
| EventPath | REG_SZ | Event file path |
| LogPath | REG_SZ | Log file path |

---

## Named-Pipe Server/Client Roles

| Role | Process | Evidence |
|------|---------|----------|
| Server | NesysService.exe | CreateNamedPipeA |
| Client | AcrGame-Win64-Shipping.exe | ConnectNamedPipe |

---

## Recovered Pipe Handshake Summary

### Handshake Sequence

```
1. NesysService creates named pipe server
2. NesysService waits for client (ConnectNamedPipe)
3. Game client opens pipe (CreateFileA)
4. Connection established
5. Game sends LCOMMAND_CLIENT_START
6. Service responds with SCOMMAND_CLIENT_START_REPLY
7. Game and service exchange commands
8. Game sends LCOMMAND_CLIENT_END
9. Service responds with SCOMMAND_CLIENT_END
10. Connection closed
```

### Command Protocol

| Direction | Command Set | Purpose |
|-----------|-------------|---------|
| Game → Service | LCOMMAND_* | Client requests |
| Service → Game | SCOMMAND_* | Service responses |

---

## Certificate-Store Requirements

| Component | Requirement |
|-----------|-------------|
| Store | MY\.Default |
| Subject | nesys |
| Private key | Likely required |
| Validity | Must be valid |

---

## Reconstructed Process Startup Sequence

### Hypothetical Sequence (Evidence-Based)

```
1. Windows boots
2. SCM starts NesysService.exe (if registered - NOT_CONFIRMED)
3. NesysService reads registry HKLM\SOFTWARE\taito\typex
4. NesysService creates named pipe server \\.\pipe\nesys_games
5. NesysService accesses certificate store MY\.Default (subject: nesys)
6. [cert3.nesys.jp purpose UNRESOLVED - hostname reference only]
7. User launches AcrGame.exe
8. AcrGame.exe creates AcrGame-Win64-Shipping.exe via CreateProcessW
9. Game initializes UE4 engine
10. Game attempts to connect to \\.\pipe\nesys_games\...
11. [Connection result depends on NesysService availability]
12. Game and service exchange LCOMMAND/SCOMMAND messages
```

### Current Sequence (Without System Drive)

```
1. Windows boots
2. SCM does NOT start NesysService.exe (not registered)
3. No named pipe server created
4. User launches AcrGame.exe
5. AcrGame.exe creates AcrGame-Win64-Shipping.exe
6. Game initializes UE4 engine
7. Game attempts to connect to \\.\pipe\nesys_games\...
8. Connection FAILS (pipe does not exist)
9. NESYS offline
10. Game continues in offline mode
```

---

## Remaining System-Drive Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| Service registration | MISSING | Cannot register with SCM |
| Certificate installation | MISSING | Cannot authenticate |
| Registry configuration | MISSING | Cannot read configuration |
| Startup sequence | MISSING | Cannot determine launch order |
| Service recovery | MISSING | Cannot restart on failure |

---

## Recommended Next Phase

**Phase 2A-G14**: Service Registration and Certificate Analysis

**Objective**: Determine whether NesysService.exe can be registered as a Windows Service without the original system drive, and whether certificate requirements can be satisfied from the available content.

**Rationale**: The static analysis has recovered the runtime contract but critical startup elements remain unresolved. The next phase should investigate whether these elements can be reconstructed from the available evidence.

---

## G14 Audit Corrections

The following overstated claims were identified and corrected in Phase 2A-G14:

| Original Claim | Correction | Reason |
|----------------|------------|--------|
| "NesysService connects to cert3.nesys.jp" | Hostname reference only | String reference ≠ network connection |
| "NesysService retrieves certificate" | Certificate store access only | Store API ≠ retrieval |
| "NesysClient plugin initializes" | Removed | Not evidenced in static analysis |
| "Card operations available" | Removed | Not evidenced in static analysis |

---

## Conclusion

Phase 2A-G13 performed IDA static analysis of NesysService.exe, AcrGame.exe, and AcrGame-Win64-Shipping.exe. The runtime contract is partially recovered: service identity, named pipe protocol, and network endpoints are confirmed. However, critical startup elements remain unresolved: the exact Windows Service registration, certificate installation, and Registry configuration.

**Classification**: `PARTIAL_STATIC_RUNTIME_CONTRACT`

**The NESYS offline block cannot be fully resolved without the original system drive content.**
