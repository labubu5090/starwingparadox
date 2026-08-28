# G12-G15 Consolidated Evidence Matrix

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: B

## Evidence Classification Legend

| Classification | Definition |
|----------------|------------|
| CONFIRMED | Directly observed or statically verified |
| HIGH_CONFIDENCE | Strong evidence with minor uncertainty |
| PARTIAL | Partially observed or inferred from strong evidence |
| UNRESOLVED | Insufficient evidence to determine |
| NOT_FOUND | Searched but not found |
| SYSTEM_DRIVE_REQUIRED | Requires original C-drive to verify |
| AUTHORIZED_INSTALLER_REQUIRED | Requires authorized installer |
| AUTHORIZATION_BOUNDARY | Requires authorization to access |

## Evidence Matrix

### Executables

| Component | Claim | Classification | Evidence Source | Confidence | Permitted Use | Prohibited Inference | Remaining Dependency |
|-----------|-------|----------------|-----------------|------------|---------------|---------------------|---------------------|
| NesysService.exe | Service name: NesysService | CONFIRMED | Binary strings | HIGH | Interface spec | Cannot start without SCM | Service registration |
| NesysService.exe | Entry point: swp_service_main | CONFIRMED | Binary imports | HIGH | Interface spec | Cannot call directly | Service context |
| NesysService.exe | Control handler: swp_service_ctrl_handler | CONFIRMED | Binary imports | HIGH | Interface spec | Cannot invoke directly | Service context |
| NesysService.exe | Self-installation capability: NOT_FOUND | CONFIRMED | API import analysis | HIGH | Architecture decision | Cannot register service | External installer |
| NesysService.exe | Command-line modes: SERVICE_MODE_ONLY | CONFIRMED | Binary analysis | HIGH | Interface spec | Cannot run interactively | Service context |
| AcrGame.exe | Role: UE4 bootstrap wrapper | CONFIRMED | Binary analysis | HIGH | Interface spec | Cannot determine launcher requirements | Original context |
| AcrGame.exe | Creates AcrGame-Win64-Shipping.exe | CONFIRMED | Binary imports | HIGH | Process model | Cannot determine wait behavior | Original context |
| AcrGame.exe | Zero NesysService references | CONFIRMED | String analysis | HIGH | Architecture decision | Cannot determine service dependency | Original context |
| AcrGame-Win64-Shipping.exe | Role: Main game binary | CONFIRMED | Binary size | HIGH | Interface spec | Cannot determine initialization | Original context |
| AcrGame-Win64-Shipping.exe | Connects to named pipe | CONFIRMED | Runtime logs | HIGH | Protocol spec | Cannot determine connection behavior | Service running |

### Named Pipe Protocol

| Component | Claim | Classification | Evidence Source | Confidence | Permitted Use | Prohibited Inference | Remaining Dependency |
|-----------|-------|----------------|-----------------|------------|---------------|---------------------|---------------------|
| Pipe path | \\.\pipe\nesys_games | CONFIRMED | Binary imports | HIGH | Interface spec | Cannot create without service | Service running |
| Pipe direction | Bidirectional | CONFIRMED | Binary analysis | HIGH | Protocol spec | Cannot determine semantics | Protocol analysis |
| Pipe mode | Message-based | CONFIRMED | Binary analysis | HIGH | Protocol spec | Cannot determine framing | Protocol analysis |
| Command count (LCOMMAND) | 47 | CONFIRMED | Binary analysis | MEDIUM | Protocol spec | Cannot determine field meanings | Static analysis |
| Command count (SCOMMAND) | 44 | CONFIRMED | Binary analysis | MEDIUM | Protocol spec | Cannot determine field meanings | Static analysis |
| Client start command | LCOMMAND_CLIENT_START | CONFIRMED | Binary analysis | HIGH | Lifecycle spec | Cannot determine payload | Protocol analysis |
| Client end command | LCOMMAND_CLIENT_END | CONFIRMED | Binary analysis | HIGH | Lifecycle spec | Cannot determine payload | Protocol analysis |
| Ping command | LCOMMAND_PING (0x66) | CONFIRMED | Binary analysis | HIGH | Protocol spec | Cannot determine response timing | Protocol analysis |
| Ping response | SCOMMAND_PING_RESPONSE (0x67) | CONFIRMED | Binary analysis | HIGH | Protocol spec | Cannot determine payload | Protocol analysis |
| Card operations | tenpo_id, card_no, mac_addr, type, cmd_str, data, trid | CONFIRMED | Binary analysis | MEDIUM | Interface spec | Cannot determine semantics | Original context |

### Registry Configuration

| Component | Claim | Classification | Evidence Source | Confidence | Permitted Use | Prohibited Inference | Remaining Dependency |
|-----------|-------|----------------|-----------------|------------|---------------|---------------------|---------------------|
| Registry key | HKLM\SOFTWARE\taito\typex | CONFIRMED | Binary strings | HIGH | Configuration spec | Cannot create without admin | Original context |
| Value count | 8 | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine defaults | Original context |
| GameKind | REG_DWORD | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| EventNextTime | REG_DWORD | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| ConditionTime | REG_DWORD | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| TrafficCount | REG_DWORD | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| LogLevel | REG_DWORD | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| NewsPath | REG_SZ | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| EventPath | REG_SZ | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| LogPath | REG_SZ | CONFIRMED | Binary imports | HIGH | Configuration spec | Cannot determine default | Original context |
| Mutability | READ_ONLY at startup | CONFIRMED | API import analysis | HIGH | Architecture decision | Cannot determine write behavior | Original context |

### Certificate Store

| Component | Claim | Classification | Evidence Source | Confidence | Permitted Use | Prohibited Inference | Remaining Dependency |
|-----------|-------|----------------|-----------------|------------|---------------|---------------------|---------------------|
| Store path | MY\.Default | CONFIRMED | Binary imports | HIGH | Interface spec | Cannot install without provisioning | Certificate installation |
| Search subject | nesys | CONFIRMED | Binary strings | HIGH | Interface spec | Cannot determine other criteria | Original context |
| Private key requirement | PROBABLY_REQUIRED | PARTIAL | Inference from client-auth pattern | MEDIUM | Architecture decision | Cannot confirm without evidence | Private key acquisition |
| Private key acquisition | NOT_SHOWN | NOT_FOUND | API import analysis | HIGH | Security boundary | Cannot determine mechanism | Original context |
| TLS attachment | NOT_SHOWN | NOT_FOUND | API import analysis | HIGH | Security boundary | Cannot determine mechanism | Original context |
| Server validation | NOT_SHOWN | NOT_FOUND | API import analysis | HIGH | Security boundary | Cannot determine mechanism | Original context |
| Failure behavior | SCOMMAND_CERT_ERROR | CONFIRMED | Binary analysis | HIGH | Error handling | Cannot determine recovery | Original context |

### Network Endpoints

| Component | Claim | Classification | Evidence Source | Confidence | Permitted Use | Prohibited Inference | Remaining Dependency |
|-----------|-------|----------------|-----------------|------------|---------------|---------------------|---------------------|
| cert3.nesys.jp:443 | Hostname reference | CONFIRMED | Binary strings | HIGH | Interface spec | Cannot determine operation | Original context |
| data.nesys.jp:80 | Hostname reference | CONFIRMED | Binary strings | HIGH | Interface spec | Cannot determine operation | Original context |
| nesys.taito.co.jp:80 | Hostname reference | CONFIRMED | Binary strings | HIGH | Interface spec | Cannot determine operation | Original context |
| fjm170920zero.nesica.net:443 | Hostname reference | CONFIRMED | Binary strings | HIGH | Interface spec | Cannot determine operation | Original context |
| WinHTTP APIs | 13 APIs imported | CONFIRMED | Binary imports | HIGH | Protocol spec | Cannot determine usage | Original context |
| Socket APIs | 5 WSAXXX APIs imported | CONFIRMED | Binary imports | HIGH | Protocol spec | Cannot determine usage | Original context |
| URL patterns | /alive/, /server/, /service/card/, etc. | CONFIRMED | Binary strings | HIGH | Interface spec | Cannot determine semantics | Original context |
| Offline behavior | SCOMMAND_NW_ERROR | CONFIRMED | Binary analysis | HIGH | Error handling | Cannot determine recovery | Original context |

### Service Lifecycle

| Component | Claim | Classification | Evidence Source | Confidence | Permitted Use | Prohibited Inference | Remaining Dependency |
|-----------|-------|----------------|-----------------|------------|---------------|---------------------|---------------------|
| Startup state | START_PENDING → RUNNING | CONFIRMED | Binary imports | HIGH | State machine | Cannot determine timing | Service context |
| Shutdown state | STOP_PENDING → STOPPED | CONFIRMED | Binary imports | HIGH | State machine | Cannot determine timing | Service context |
| Stop handling | SERVICE_CONTROL_STOP | CONFIRMED | Binary imports | HIGH | State machine | Cannot determine behavior | Service context |
| Shutdown handling | SERVICE_CONTROL_SHUTDOWN | CONFIRMED | Binary imports | HIGH | State machine | Cannot determine behavior | Service context |
| Interrogate handling | Default case | CONFIRMED | Binary imports | HIGH | State machine | Cannot determine behavior | Service context |
| Mutex creation | CreateMutexA | CONFIRMED | Binary imports | MEDIUM | Concurrency | Cannot determine purpose | Original context |
| WSAStartup | WSAStartup | CONFIRMED | Binary imports | MEDIUM | Network init | Cannot determine version | Original context |
| Worker threads | CreateThread | CONFIRMED | Binary imports | MEDIUM | Concurrency | Cannot determine count | Original context |

### D-Drive Backup

| Component | Claim | Classification | Evidence Source | Confidence | Permitted Use | Prohibited Inference | Remaining Dependency |
|-----------|-------|----------------|-----------------|------------|---------------|---------------------|---------------------|
| Scope | Game content only | CONFIRMED | File inventory | HIGH | Architecture decision | Cannot reconstruct C-drive | Original C-drive |
| Files | 37,334 files | CONFIRMED | File inventory | HIGH | Inventory | Cannot determine completeness | Original context |
| Executables | 3 | CONFIRMED | File inventory | HIGH | Inventory | Cannot determine functionality | Original context |
| Scripts | 0 | CONFIRMED | File inventory | HIGH | Architecture decision | Cannot determine deployment | Original context |
| Configs | 52 .ini, 60+ .json | CONFIRMED | File inventory | HIGH | Inventory | Cannot determine purpose | Original context |
| Logs | 1 .log (40,728 lines) | CONFIRMED | File inventory | HIGH | Forensics | Cannot determine service references | Original context |
| OpenKey.json | IsOpen:1, OpenVersion:56299 | CONFIRMED | File content | HIGH | Runtime state | Cannot determine provisioning | Original context |
| EWF=1 | Embedded arcade system | CONFIRMED | File content | HIGH | Architecture | Cannot determine configuration | Original context |
