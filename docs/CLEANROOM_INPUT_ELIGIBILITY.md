# Clean-room Input Eligibility

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: D

## Classification Categories

| Category | Definition | Permitted Use |
|----------|------------|---------------|
| ELIGIBLE_INTERFACE_FACT | Externally observable or statically confirmed interface behavior | May inform independent compatibility specification |
| ELIGIBLE_FAILURE_BEHAVIOR | Observable error, timeout or unavailable-service behavior | May be represented in isolated tests |
| DOCUMENTATION_ONLY | Evidence useful for historical understanding but not required in implementation | May inform documentation |
| RESTRICTED_SECURITY_BEHAVIOR | Certificate, authentication, credential, production-host or trust behavior | Must not be reproduced or bypassed |
| UNKNOWN_DO_NOT_IMPLEMENT | Behavior lacking sufficient evidence | Must not be implemented |
| PROPRIETARY_INTERNAL_DETAIL_EXCLUDED | Internal implementation detail unrelated to independently needed interface | Must not be implemented |

## Input Eligibility Matrix

### Named Pipe Protocol

| Observation | Classification | Rationale |
|-------------|----------------|-----------|
| Pipe name: \\.\pipe\nesys_games | ELIGIBLE_INTERFACE_FACT | Externally observable path |
| Server creates pipe, client connects | ELIGIBLE_INTERFACE_FACT | Standard pipe roles |
| Message-based framing | ELIGIBLE_INTERFACE_FACT | Observable from binary analysis |
| 4-byte LE length prefix | ELIGIBLE_INTERFACE_FACT | Observable from binary analysis |
| 47 LCOMMAND types (game→service) | ELIGIBLE_INTERFACE_FACT | Observable from binary analysis |
| 44 SCOMMAND types (service→game) | ELIGIBLE_INTERFACE_FACT | Observable from binary analysis |
| LCOMMAND_CLIENT_START | ELIGIBLE_INTERFACE_FACT | Observable lifecycle event |
| LCOMMAND_CLIENT_END | ELIGIBLE_INTERFACE_FACT | Observable lifecycle event |
| SCOMMAND_CLIENT_START_REPLY | ELIGIBLE_INTERFACE_FACT | Observable lifecycle event |
| LCOMMAND_PING (0x66) | ELIGIBLE_INTERFACE_FACT | Observable command ID |
| SCOMMAND_PING_RESPONSE (0x67) | ELIGIBLE_INTERFACE_FACT | Observable command ID |
| Card operation structures | ELIGIBLE_INTERFACE_FACT | Observable field names |
| Command field meanings | UNKNOWN_DO_NOT_IMPLEMENT | Not evidenced |
| Command payload formats | UNKNOWN_DO_NOT_IMPLEMENT | Not evidenced |
| Checksum algorithms | UNKNOWN_DO_NOT_IMPLEMENT | Not evidenced |

### Registry Configuration

| Observation | Classification | Rationale |
|-------------|----------------|-----------|
| Registry key: HKLM\SOFTWARE\taito\typex | ELIGIBLE_INTERFACE_FACT | Observable from binary strings |
| 8 values (5 DWORD, 3 SZ) | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Value names: GameKind, EventNextTime, etc. | ELIGIBLE_INTERFACE_FACT | Observable from binary strings |
| READ_ONLY at startup | ELIGIBLE_INTERFACE_FACT | Observable from API imports |
| Default values | UNKNOWN_DO_NOT_IMPLEMENT | Not evidenced |
| Missing-value behavior | UNKNOWN_DO_NOT_IMPLEMENT | Not evidenced |
| Downstream functions | UNKNOWN_DO_NOT_IMPLEMENT | Not evidenced |

### Certificate Store

| Observation | Classification | Rationale |
|-------------|----------------|-----------|
| Store path: MY\.Default | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Search subject: nesys | ELIGIBLE_INTERFACE_FACT | Observable from binary strings |
| Store access: CertOpenStore, CertFindCertificateInStore | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Private key acquisition | RESTRICTED_SECURITY_BEHAVIOR | Security boundary |
| TLS client certificate attachment | RESTRICTED_SECURITY_BEHAVIOR | Security boundary |
| Server certificate validation | RESTRICTED_SECURITY_BEHAVIOR | Security boundary |
| cert3.nesys.jp purpose | RESTRICTED_SECURITY_BEHAVIOR | Production endpoint |
| Certificate renewal | RESTRICTED_SECURITY_BEHAVIOR | Security boundary |
| Failure: SCOMMAND_CERT_ERROR | ELIGIBLE_FAILURE_BEHAVIOR | Observable error behavior |

### Network Endpoints

| Observation | Classification | Rationale |
|-------------|----------------|-----------|
| cert3.nesys.jp:443 | RESTRICTED_SECURITY_BEHAVIOR | Production endpoint |
| data.nesys.jp:80 | RESTRICTED_SECURITY_BEHAVIOR | Production endpoint |
| nesys.taito.co.jp:80 | RESTRICTED_SECURITY_BEHAVIOR | Production endpoint |
| fjm170920zero.nesica.net:443 | RESTRICTED_SECURITY_BEHAVIOR | Production endpoint |
| WinHTTP APIs imported | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Socket APIs imported | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| URL patterns (/alive/, /server/, etc.) | ELIGIBLE_INTERFACE_FACT | Observable from binary strings |
| DNS resolution via gethostbyname | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Offline behavior: SCOMMAND_NW_ERROR | ELIGIBLE_FAILURE_BEHAVIOR | Observable error behavior |
| Recovery behavior: SCOMMAND_NWRECOVER_NOTICE | ELIGIBLE_FAILURE_BEHAVIOR | Observable recovery behavior |

### Service Lifecycle

| Observation | Classification | Rationale |
|-------------|----------------|-----------|
| Service name: NesysService | ELIGIBLE_INTERFACE_FACT | Observable from binary strings |
| Entry point: swp_service_main | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Control handler: swp_service_ctrl_handler | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| State: START_PENDING → RUNNING → STOPPED | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Stop handling: SERVICE_CONTROL_STOP | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Shutdown handling: SERVICE_CONTROL_SHUTDOWN | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| Mutex creation | PROPRIETARY_INTERNAL_DETAIL_EXCLUDED | Internal implementation |
| Worker thread creation | PROPRIETARY_INTERNAL_DETAIL_EXCLUDED | Internal implementation |
| Service registration | RESTRICTED_SECURITY_BEHAVIOR | Windows system mutation |
| Service account configuration | RESTRICTED_SECURITY_BEHAVIOR | Windows system mutation |

### Game Executables

| Observation | Classification | Rationale |
|-------------|----------------|-----------|
| AcrGame.exe creates AcrGame-Win64-Shipping.exe | ELIGIBLE_INTERFACE_FACT | Observable from binary imports |
| AcrGame.exe is UE4 bootstrap wrapper | DOCUMENTATION_ONLY | Historical understanding |
| AcrGame.exe contains zero NesysService references | ELIGIBLE_INTERFACE_FACT | Observable from string analysis |
| Game connects to named pipe | ELIGIBLE_INTERFACE_FACT | Observable from runtime logs |
| Game enters offline mode on NESYS failure | ELIGIBLE_FAILURE_BEHAVIOR | Observable from runtime logs |
| Game blocks TCP on NESYS offline | ELIGIBLE_FAILURE_BEHAVIOR | Observable from runtime logs |
| Game HTTP matching succeeds offline | ELIGIBLE_INTERFACE_FACT | Observable from runtime logs |
| Game process model | DOCUMENTATION_ONLY | Historical understanding |

### D-Drive Backup

| Observation | Classification | Rationale |
|-------------|----------------|-----------|
| 37,334 files | DOCUMENTATION_ONLY | Historical understanding |
| 3 executables | DOCUMENTATION_ONLY | Historical understanding |
| 0 scripts | DOCUMENTATION_ONLY | Historical understanding |
| OpenKey.json | ELIGIBLE_INTERFACE_FACT | Observable runtime state |
| EWF=1 | DOCUMENTATION_ONLY | Historical understanding |
| CmdFile logs | DOCUMENTATION_ONLY | Historical understanding |
