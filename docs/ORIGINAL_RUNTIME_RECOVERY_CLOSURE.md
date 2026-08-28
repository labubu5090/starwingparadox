# Original Runtime Recovery Closure

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: A
**Classification**: RECOVERY_BRANCH_CLOSED

## Closure Statement

The in-scope original-runtime recovery investigation has reached its evidence limit. No safe reconstruction is possible from the available backup. The original runtime recovery branch is formally closed.

## Available Evidence

| Evidence | Source | Confidence | Limitation |
|----------|--------|------------|------------|
| NesysService.exe binary | D-drive backup | CONFIRMED | No registration context |
| AcrGame.exe binary | D-drive backup | CONFIRMED | Bootstrap wrapper only |
| AcrGame-Win64-Shipping.exe binary | D-drive backup | CONFIRMED | 163MB game binary |
| Service name | Binary strings | CONFIRMED | Cannot start without SCM |
| Named pipe path | Binary imports | CONFIRMED | Cannot create without service |
| Registry key path | Binary imports | CONFIRMED | Cannot provision without C-drive |
| Network hostnames | Binary strings | CONFIRMED | Cannot connect without service |
| Certificate store path | Binary imports | CONFIRMED | Cannot install without provisioning |
| 47+44 pipe commands | Binary analysis | CONFIRMED | Field meanings unknown |
| 8 registry values | Binary imports | CONFIRMED | Defaults unknown |
| OpenKey.json | D-drive data | CONFIRMED | Runtime state file |
| CmdFile logs | D-drive data | CONFIRMED | No NesysService references |

## Missing Evidence

| Evidence | Source Required | Status | Impact |
|----------|----------------|--------|--------|
| Service registration | C-drive | NOT_FOUND | Cannot start service |
| Certificate installation | C-drive | NOT_FOUND | Cannot authenticate |
| Registry provisioning | C-drive | NOT_FOUND | Cannot configure service |
| Startup orchestration | C-drive | NOT_FOUND | Cannot launch service |
| Service dependencies | C-drive | NOT_FOUND | Cannot configure recovery |
| Service account | C-drive | NOT_FOUND | Cannot configure security |
| Display name, description | C-drive | NOT_FOUND | Cannot identify service |
| Installation source | Installer | NOT_FOUND | Cannot reinstall |
| Recovery media | Vendor | NOT_FOUND | Cannot restore |
| System image | Backup | NOT_FOUND | Cannot reconstruct |

## Searches Performed

| Phase | Search Scope | Result |
|-------|-------------|--------|
| G12 | D-drive backup: 37,334 files | 3 executables, 0 scripts, 0 configs |
| G13 | NesysService.exe: 548KB binary | Static runtime contract recovered |
| G14 | NesysService.exe: API imports | No self-installation, external registration required |
| G15 | D-drive + project root: 47,000+ files | 0 deployment artifacts, 0 installers, 0 recovery images |

## Recovered Runtime Interfaces

| Interface | Status | Evidence |
|-----------|--------|----------|
| Named pipe protocol | CONFIRMED | 47+44 command types, framing |
| Registry configuration | CONFIRMED | 8 values, READ_ONLY |
| Certificate store access | CONFIRMED | MY\.Default, subject nesys |
| Network endpoints | CONFIRMED | 4 hostnames, WinHTTP APIs |
| Service lifecycle | CONFIRMED | START_PENDING → RUNNING → STOPPED |

## Unresolved Registration Properties

| Property | Status | Impact |
|----------|--------|--------|
| Display name | NOT_FOUND | Cannot identify in SCM |
| Description | NOT_FOUND | Cannot document |
| Account | NOT_FOUND | Cannot configure security |
| Start type | NOT_FOUND | Cannot configure startup |
| Dependencies | NOT_FOUND | Cannot configure ordering |
| Failure actions | NOT_FOUND | Cannot configure recovery |
| SID type | NOT_FOUND | Cannot configure isolation |
| Preshutdown timeout | NOT_FOUND | Cannot configure shutdown |

## Unresolved Certificate Behavior

| Behavior | Status | Impact |
|----------|--------|--------|
| Private key acquisition | NOT_SHOWN | Cannot authenticate |
| TLS attachment | NOT_SHOWN | Cannot establish connection |
| Server validation | NOT_SHOWN | Cannot verify identity |
| cert3.nesys.jp purpose | UNRESOLVED | Cannot determine operation |
| Certificate renewal | NOT_SHOWN | Cannot maintain validity |

## Unresolved Registry Values

| Value | Status | Impact |
|-------|--------|--------|
| GameKind default | NOT_SHOWN | Cannot determine installation identity |
| EventNextTime default | NOT_SHOWN | Cannot determine runtime state |
| ConditionTime default | NOT_SHOWN | Cannot determine runtime state |
| TrafficCount default | NOT_SHOWN | Cannot determine runtime state |
| LogLevel default | NOT_SHOWN | Cannot configure logging |
| NewsPath default | NOT_SHOWN | Cannot locate news content |
| EventPath default | NOT_SHOWN | Cannot locate event content |
| LogPath default | NOT_SHOWN | Cannot locate log files |

## Unavailable Recovery Sources

| Source | Status | Reason |
|--------|--------|--------|
| Original C-drive image | NOT_AVAILABLE | Not provided by operator |
| Physical system drive | NOT_AVAILABLE | Not provided by operator |
| Authorized installer | NOT_FOUND | No installer artifacts found |
| Recovery media | NOT_FOUND | No recovery artifacts found |
| Service configuration export | NOT_FOUND | No registry/config artifacts found |
| Vendor documentation | NOT_FOUND | No documentation found |
| Certificate material | NOT_FOUND | No certificate files found |
| Deployment scripts | NOT_FOUND | No scripts found |

## Safe Registration Cannot Be Established

Safe registration cannot be established because:

1. **Service registration** requires Windows Service Control Manager context, which is absent
2. **Certificate installation** requires certificate store access and private key, which are absent
3. **Registry provisioning** requires HKLM write access and default values, which are absent
4. **Startup orchestration** requires service configuration and dependencies, which are absent
5. **Service account** requires security configuration, which is absent
6. **Recovery configuration** requires failure actions and restart behavior, which are absent

## Conditions Required to Reopen Recovery Branch

The recovery branch may be reopened ONLY when legitimate new evidence becomes available:

1. **Original C-drive image** — Complete Windows system drive backup
2. **Original physical system drive** — Physical hardware with intact installation
3. **Authorized installer** — Verified installer package from vendor or distributor
4. **Authorized recovery media** — Recovery disc or USB from vendor or distributor
5. **Verified service configuration export** — Registry hive export or service configuration file
6. **Vendor or distributor documentation** — Official deployment or recovery procedures
7. **Non-secret deployment records** — Installation logs, configuration files, deployment scripts
8. **Authorized intact cabinet environment** — Complete working cabinet with all components

## Reopening Must NOT Occur

The recovery branch must NOT be reopened merely because:

- Another speculative command can be imagined
- Another default value can be guessed
- Another service configuration can be hypothesized
- Another certificate behavior can be inferred
- Another network operation can be theorized
- Another registry value can be assumed
- Another startup sequence can be constructed
- Another deployment mechanism can be proposed
