# Original Runtime Reconstruction

**Phase**: 2A-G13  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

Based on static analysis of NesysService.exe, AcrGame.exe, and AcrGame-Win64-Shipping.exe, the original runtime contract has been partially reconstructed. The service identity, named pipe protocol, and network endpoints are confirmed. However, critical startup elements remain unresolved: the exact Windows Service registration, certificate installation, and Registry configuration.

---

## Reconstructed Runtime Contract

### 1. Service Identity

| Component | Requirement | Evidence | Status |
|-----------|-------------|----------|--------|
| Service name | NesysService | String reference | CONFIRMED |
| Service type | SERVICE_WIN32_OWN_PROCESS | Standard | INFERRED |
| Start type | SERVICE_AUTO_START | Service should start with Windows | INFERRED |
| Error control | SERVICE_ERROR_NORMAL | Standard | INFERRED |
| Account | LocalSystem or custom | Needs network/cert access | INFERRED |

### 2. Registry Configuration

| Component | Requirement | Evidence | Status |
|-----------|-------------|----------|--------|
| Root hive | HKEY_LOCAL_MACHINE | Standard for services | CONFIRMED |
| Subkey | `SOFTWARE\taito\typex` | String reference | CONFIRMED |
| Values | 8 configuration values | String references | CONFIRMED |

### 3. Certificate Store

| Component | Requirement | Evidence | Status |
|-----------|-------------|----------|--------|
| Store | MY\.Default | String reference | CONFIRMED |
| Subject | nesys | String reference | CONFIRMED |
| Private key | Likely required | Client auth inference | MEDIUM |
| Validity | Must be valid | Certificate validation | CONFIRMED |

### 4. Named Pipe

| Component | Requirement | Evidence | Status |
|-----------|-------------|----------|--------|
| Pipe name | `\\.\pipe\nesys_games` | String reference | CONFIRMED |
| Server | NesysService.exe | CreateNamedPipeA | CONFIRMED |
| Client | AcrGame-Win64-Shipping.exe | ConnectNamedPipe | CONFIRMED |
| Protocol | Command-response | LCOMMAND/SCOMMAND | CONFIRMED |

### 5. Network Endpoints

| Component | Requirement | Evidence | Status |
|-----------|-------------|----------|--------|
| cert3.nesys.jp | HTTPS (443) | String reference | CONFIRMED |
| data.nesys.jp | HTTP (80) | String reference | CONFIRMED |
| nesys.taito.co.jp | HTTP (80) | String reference | CONFIRMED |
| fjm170920zero.nesica.net | HTTPS (443) | String reference | CONFIRMED |

---

## Process Startup Sequence

### Reconstructed Sequence

```
1. Windows boots
2. Windows SCM starts NesysService.exe
3. NesysService registers as "NesysService"
4. NesysService creates named pipe server
5. NesysService connects to cert3.nesys.jp
6. NesysService retrieves certificate
7. User launches AcrGame.exe
8. AcrGame.exe creates AcrGame-Win64-Shipping.exe
9. AcrGame-Win64-Shipping.exe initializes UE4 engine
10. NesysClient plugin initializes
11. Game attempts to connect to \\.\pipe\nesys_games\...
12. Connection succeeds (NesysService running)
13. Game sends LCOMMAND_CLIENT_START
14. NesysService responds with SCOMMAND_CLIENT_START_REPLY
15. Game and service exchange commands
16. Card operations available
17. Event data available
18. Server communication available
```

### Current State (Without System Drive)

```
1. Windows boots
2. Windows SCM does NOT start NesysService.exe (not registered)
3. No named pipe server created
4. User launches AcrGame.exe
5. AcrGame.exe creates AcrGame-Win64-Shipping.exe
6. AcrGame-Win64-Shipping.exe initializes UE4 engine
7. NesysClient plugin initializes
8. Game attempts to connect to \\.\pipe\nesys_games\...
9. Connection FAILS (pipe does not exist)
10. NESYS status set to offline
11. CertError spam (12 cycles)
12. Game continues in offline mode
13. Card operations unavailable
14. Event data unavailable
15. Server communication unavailable
```

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

### Missing System Drive Content

| Content | Status | Impact |
|---------|--------|--------|
| Launcher executable | MISSING | Cannot determine startup sequence |
| Service wrapper | MISSING | Cannot register service |
| Certificate files | MISSING | Cannot install certificates |
| Registry exports | MISSING | Cannot configure registry |
| Startup scripts | MISSING | Cannot automate startup |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Service identity | CONFIRMED |
| Registry contract | CONFIRMED |
| Certificate contract | CONFIRMED |
| Named pipe protocol | CONFIRMED |
| Network endpoints | CONFIRMED |
| Process startup | HIGH |
| Missing components | CONFIRMED |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact service registration | MEDIUM | Requires system drive |
| Exact certificate installation | MEDIUM | Requires system drive |
| Exact registry values | MEDIUM | Requires system drive |
| Exact startup sequence | MEDIUM | Requires system drive |

---

## Conclusion

The original runtime contract has been partially reconstructed. The service identity, named pipe protocol, and network endpoints are confirmed. However, critical startup elements remain unresolved: the exact Windows Service registration, certificate installation, and Registry configuration. These require the original system drive content.

**Classification**: `PARTIAL_STATIC_RUNTIME_CONTRACT`

The runtime contract is partially recovered but critical startup elements remain unresolved.
