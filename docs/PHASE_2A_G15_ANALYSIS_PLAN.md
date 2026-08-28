# Phase 2A-G15 Analysis Plan

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: IN_PROGRESS

---

## Workstreams

### Workstream A: Complete Deployment Artifact Inventory

**Objective**: Perform recursive inventory of all files under project root and D-drive backup.

**Approach**:
1. Search by extension (.msi, .msp, .mst, .cab, .exe, .zip, .7z, .rar, .iso, .wim, .esd, .swm, .img, .vhd, .vhdx, .gho, .tib, .reg, .inf, .ini, .xml, .json, .config, .cfg, .properties, .bat, .cmd, .ps1, .vbs, .js, .wsf, .lnk, .url, .job, .manifest, .log, .txt, .md, .csv, .db, .sqlite, .sqlite3)
2. Search by filename keywords (NesysService, nesys, AcrGame, Starwing, StarwingParadox, taito, typex, service, install, installer, setup, deploy, deployment, provision, provisioning, recovery, restore, image, master, clone, startup, watchdog, launcher, bootstrap, maintenance, update, updater, patch, certificate, cert, GameKind, EventNextTime, ConditionTime, TrafficCount, LogLevel, NewsPath, EventPath, LogPath, nesys_games)
3. Record for every candidate: full path, filename, extension, file size, creation timestamp, last-write timestamp, SHA-256, file-signature, signed/unsigned status, reason selected, confidence, content inspection safety

**Evidence Sources**:
- Project root directory
- D-drive backup (X:\StarwingParadox)

---

### Workstream B: Archive and Disk-Image Inspection

**Objective**: Inspect archives and disk-image artifacts owned by the operator.

**Approach**:
1. Inspect file listings without executing content
2. Extract metadata or listings into temporary analysis directory only when supported safely
3. Preserve original artifact unchanged
4. Calculate SHA-256 before and after inspection
5. Do not mount images read-write
6. Do not boot images
7. Do not launch executables inside images
8. Do not install drivers or filesystem tools from unknown sources

**Search For**:
- NesysService.exe
- Service installation scripts
- Registry files
- Certificate files
- Startup shortcuts
- Scheduled-task exports
- Service recovery configuration
- ProgramData directories
- Windows service Registry hives
- Application configuration
- Installer logs
- Deployment manifests
- System preparation scripts

---

### Workstream C: Windows Installer Metadata

**Objective**: For any MSI, MSP, MST or installer database found, inspect metadata without installation.

**Approach**:
1. Identify ProductName, ProductCode, UpgradeCode, Manufacturer, ProductVersion, InstallLocation
2. Inspect ServiceInstall table entries
3. Inspect ServiceControl table entries
4. Inspect Registry table entries
5. Inspect Environment table entries
6. Inspect Shortcut table entries
7. Inspect CustomAction entries
8. Inspect InstallExecuteSequence relationships
9. Identify component file paths
10. Identify certificate-related custom actions
11. Identify service recovery configuration
12. Identify uninstall behavior

**Do NOT**: Execute custom actions or invoke msiexec operations

---

### Workstream D: Script and Configuration Inspection

**Objective**: For every candidate script or configuration file, inspect as text only.

**Approach**:
1. Determine encoding
2. Record SHA-256
3. Identify references to: NesysService, SCM, sc.exe, CreateService, service account, start type, dependencies, failure actions, HKLM\SOFTWARE\taito\typex, GameKind, paths, certificates, named pipes, AcrGame, startup order
4. Redact passwords, private keys, authentication tokens, certificate private material, unique secret values

**Do NOT**: Execute or import any discovered file

---

### Workstream E: Log and Textual Residue

**Objective**: Inspect operator-owned logs and textual records for evidence of service installation, startup, and operation.

**Approach**:
1. Search for service installation evidence
2. Search for successful service startup
3. Search for failed service startup
4. Search for service-control error numbers
5. Search for configured binary path
6. Search for installer product name
7. Search for deployment version
8. Search for service account
9. Search for Registry provisioning
10. Search for NewsPath, EventPath, LogPath
11. Search for certificate-store lookup
12. Search for missing certificate
13. Search for client connection to named pipe
14. Search for LCOMMAND_CLIENT_START
15. Search for SCOMMAND_CLIENT_START_REPLY
16. Search for startup or shutdown order

---

### Workstream F: PE Resource and Signature Correlation

**Objective**: For installer-like executables and service-related binaries, inspect without execution.

**Approach**:
1. Inspect VERSIONINFO
2. Identify ProductName, FileDescription, CompanyName, OriginalFilename, InternalName, ProductVersion, FileVersion
3. Inspect manifest
4. Inspect resources
5. Inspect Authenticode signer information where available
6. Identify embedded CAB or installer signatures
7. Identify imported installation-related APIs
8. Classify as: installer, bootstrapper, updater, watchdog, launcher, service host, game executable, unknown

---

### Workstream G: Service Configuration Reconstruction

**Objective**: Using only recovered evidence, update the declarative registration manifest.

**Approach**:
1. Recover service name
2. Recover display name
3. Recover binary path
4. Recover command-line arguments
5. Recover service type
6. Recover start type
7. Recover delayed auto-start
8. Recover error control
9. Recover service account
10. Recover dependencies
11. Recover description
12. Recover working directory
13. Recover required environment variables
14. Recover failure actions
15. Recover restart delays
16. Recover required privileges
17. Recover service SID type
18. Recover preshutdown timeout
19. Recover event-log source
20. Recover installation source
21. Recover uninstall source

**Do NOT**: Generate runnable commands

---

### Workstream H: Non-Secret Registry Provisioning

**Objective**: Determine whether any recovered artifact explicitly defines values for HKLM\SOFTWARE\taito\typex.

**Approach**:
1. Search for registry value definitions in artifacts
2. For each known value, record: source artifact, declared data type, declared value (non-secret only), whether static installation configuration or runtime-generated state, cabinet-specific status, confidence

**Do NOT**: Publish or reproduce credential values, create .reg reconstruction, or import into live Registry

---

### Workstream I: Startup Orchestration

**Objective**: Search for evidence of the component responsible for the original boot or launch sequence.

**Approach**:
1. Search for Windows automatic service start
2. Search for delayed automatic service start
3. Search for startup-folder shortcut
4. Search for scheduled task
5. Search for launcher executable
6. Search for watchdog
7. Search for shell replacement
8. Search for kiosk startup mechanism
9. Search for external cabinet-management process
10. Search for installer-configured service start
11. Search for recovery-image startup script

**Do NOT**: Configure any startup mechanism

---

### Workstream J: Authorized Recovery Source Matrix

**Objective**: Create a matrix of possible recovery sources with evidence status.

**Sources**:
- Original C-drive image
- Original physical system drive
- Operator-created backup
- Arcade distributor recovery image
- Authorized installer package
- Vendor deployment media
- Windows System32 service Registry hive
- Exported service metadata
- Old maintenance backup
- Installation log
- Cabinet clone
- Legitimate spare cabinet image

**Do NOT**: Search external systems or the internet for proprietary recovery images

---

### Workstream K: G14 Classification Normalization

**Objective**: Document that EXTERNAL_REGISTRATION_REQUIRED is a project-specific refinement most closely corresponding to SYSTEM_IMAGE_OR_INSTALLER_REQUIRED.

**Do NOT**: Rewrite historical evidence merely to force the old enum

---

### Workstream L: Stop Conditions

**Objective**: Immediately stop a line of investigation if it requires:
- Running an unknown installer
- Booting an unknown image
- Private-key extraction
- Credential recovery
- Certificate substitution
- Authentication bypass
- Production-service access
- Proprietary software download
- Unauthorized third-party system access
- Modification of original artifacts

**Record**: The boundary reached and continue only with other safe, independent workstreams

---

## Document Creation Plan

| Document | Workstream |
|----------|------------|
| PHASE_2A_G15_INITIAL_BASELINE.md | Pre-analysis |
| PHASE_2A_G15_ANALYSIS_PLAN.md | Pre-analysis |
| DEPLOYMENT_ARTIFACT_INVENTORY.md | A |
| INSTALLER_AND_IMAGE_CANDIDATES.md | B, C |
| EXTERNAL_SERVICE_REGISTRATION_EVIDENCE.md | D, E, F |
| NESYSERVICE_DEPLOYMENT_RESIDUE.md | D, E |
| NESYSERVICE_STARTUP_ORCHESTRATION.md | I |
| TYPEX_PROVISIONING_EVIDENCE.md | H |
| AUTHORIZED_RECOVERY_SOURCE_MATRIX.md | J |
| G14_CLASSIFICATION_MAPPING.md | K |
| PHASE_2A_G15_FINAL_REPORT.md | Summary |

---

## Artifact Creation Plan

| Artifact | Workstream |
|----------|------------|
| deployment_artifact_inventory.json | A |
| external_registration_evidence.json | D, E, F |
| startup_orchestration.json | I |
| recovery_source_matrix.json | J |

---

## Execution Order

1. Workstream A: Complete deployment artifact inventory
2. Workstream B: Archive and disk-image inspection
3. Workstream C: Windows installer metadata
4. Workstream D: Script and configuration inspection
5. Workstream E: Log and textual residue
6. Workstream F: PE resource and signature correlation
7. Workstream G: Service configuration reconstruction
8. Workstream H: Non-secret registry provisioning
9. Workstream I: Startup orchestration
10. Workstream J: Authorized recovery source matrix
11. Workstream K: G14 classification normalization
12. Workstream L: Stop conditions (continuous)
13. Final Report
14. Quality Gates
15. Commit
