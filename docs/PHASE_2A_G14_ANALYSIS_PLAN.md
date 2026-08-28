# Phase 2A-G14 Analysis Plan

**Phase**: 2A-G14  
**Date**: 2026-08-28  
**Status**: IN_PROGRESS

---

## Workstreams

### Workstream A: Service Registration Contract

**Objective**: Reconstruct expected Windows service definition from static evidence.

**Approach**:
1. PE string analysis for service-related strings
2. Import table analysis for service APIs (OpenSCManager, CreateService, ChangeServiceConfig)
3. Resource section analysis
4. Manifest analysis
5. Registry reference cross-referencing
6. Log file evidence search

**Evidence Sources**:
- NesysService.exe PE strings
- Import table (advapi32.dll service APIs)
- Event Log source references
- Registry path references

**Classification per Property**:
- CONFIRMED: Direct string/API evidence
- HIGH_CONFIDENCE: Multiple indirect evidence
- POSSIBLE: Single indirect evidence
- NOT_FOUND: No evidence found
- SYSTEM_DRIVE_REQUIRED: Requires system drive content

---

### Workstream B: Service Installer Mode

**Objective**: Determine if NesysService has self-installation capability.

**Approach**:
1. Trace argc/argv processing
2. Find GetCommandLine usage
3. Search for command-line comparisons
4. Identify CreateService/OpenSCManager calls
5. Check for DeleteService calls
6. Look for StartServiceCtrlDispatcher paths
7. Search for interactive-session detection
8. Check parent-process checks

**Do NOT**: Invoke any discovered command-line mode

**Classification**:
- CONFIRMED: Self-installation code present
- NOT_FOUND: No self-installation code

---

### Workstream C: Certificate Data Flow

**Objective**: Trace certificate-related calls via IDA static analysis.

**Approach**:
1. Locate CertOpenStore call sites
2. Identify store provider and location flags
3. Determine store name
4. Find CertFindCertificateInStore parameters
5. Trace subject matching behavior
6. Identify certificate selection loop
7. Check certificate validity checks
8. Look for EKU checks
9. Find issuer checks
10. Identify thumbprint/serial matching
11. Check CertGetCertificateContextProperty
12. Find CryptAcquireCertificatePrivateKey or NCryptAcquireCertificateKey
13. Trace client-certificate attachment to TLS
14. Check server-certificate validation
15. Identify failure codes and retry paths

**Classification**:
- CONFIRMED_REQUIRED: Direct evidence of private key usage
- PROBABLY_REQUIRED: Strong indirect evidence
- NOT_SHOWN: No evidence found
- NOT_REQUIRED: Evidence against requirement

---

### Workstream D: cert3.nesys.jp Relationship

**Objective**: Build evidence-based call graph for all references.

**Approach**:
1. Find all string references to "cert3.nesys.jp"
2. Trace function RVAs
3. Identify call chains
4. Find imported network APIs
5. Analyze surrounding strings
6. Check request construction
7. Identify protocol evidence
8. Find port encoding
9. Analyze data consumed after response
10. Determine relationship to local certificate selection

**Do NOT**:
- Resolve the hostname
- Connect to it
- Search for credentials

**Classification per Purpose**:
- CONFIRMED: Direct evidence
- UNRESOLVED: Insufficient evidence

---

### Workstream E: Registry Defaults and Configuration Semantics

**Objective**: Determine semantics for each HKLM\SOFTWARE\taito\typex value.

**Approach**:
1. Find read call sites for each value
2. Determine expected type
3. Find default values (only if explicitly in code)
4. Find valid ranges (only if explicitly validated)
5. Determine missing-value behavior
6. Determine malformed-value behavior
7. Identify downstream functions
8. Check if mutable during runtime
9. Determine if machine provisioning or runtime state

**Classification per Value**:
- STATIC_CONFIGURATION: Fixed per installation
- INSTALLATION_IDENTITY: Unique per cabinet/installation
- RUNTIME_STATE: Changes during execution
- FILE_PATH: File system path reference
- LOGGING_CONFIGURATION: Logging behavior
- UNKNOWN: Insufficient evidence

---

### Workstream F: File-Path Dependencies

**Objective**: Recover file/directory requirements for NewsPath, EventPath, LogPath.

**Approach**:
1. Find read/write behavior for each path
2. Determine expected file or directory type
3. Find filename patterns
4. Determine startup criticality
5. Check directory creation behavior
6. Determine missing path behavior
7. Identify access mode
8. Check expected account permissions
9. Search D-drive backup for candidates

**Do NOT**: Modify candidate files

**Confirmation Standard**: Filename similarity alone is not confirmation.

---

### Workstream G: Offline Registration Manifest

**Objective**: Create non-executable, declarative registration manifest.

**Output**: `artifacts/phase_2a_g14/nesys_service_registration_manifest.json`

**Fields**: service_name, display_name, binary_path, arguments, service_type, start_type, error_control, account, dependencies, failure_actions, required_privileges, working_directory, environment, registry_dependencies, certificate_dependencies, file_dependencies, unresolved, safe_to_register

**Do NOT Create**: .reg files, .bat files, .cmd files, PowerShell scripts, sc.exe commands, installer packages

---

### Workstream H: Safe-to-Register Decision

**Objective**: Evaluate if future service registration could be considered safe and complete.

**Decision must remain false if ANY critical item unresolved**:
- Service account
- Command-line arguments
- Required certificate identity
- Private-key dependency
- Installation-specific Registry identity
- Production-network behavior
- Service dependencies
- Executable authorization
- Working-directory requirements

**Note**: "SCM can technically register an executable" ≠ "service registration is safe or correct"

---

## Document Creation Plan

| Document | Workstream |
|----------|------------|
| PHASE_2A_G14_INITIAL_BASELINE.md | Pre-analysis |
| PHASE_2A_G14_ANALYSIS_PLAN.md | Pre-analysis |
| NESYSERVICE_REGISTRATION_CONTRACT.md | A |
| NESYSERVICE_COMMAND_LINE_MODES.md | B |
| NESYSERVICE_CERTIFICATE_DATA_FLOW.md | C |
| CERT3_NESYS_JP_RELATIONSHIP.md | D |
| TYPEX_REGISTRY_SEMANTICS.md | E |
| NESYSERVICE_FILE_PATH_DEPENDENCIES.md | F |
| NESYSERVICE_SAFE_REGISTRATION_ASSESSMENT.md | H |
| PHASE_2A_G14_FINAL_REPORT.md | Summary |

---

## Artifact Creation Plan

| Artifact | Workstream |
|----------|------------|
| nesys_service_registration_manifest.json | G |
| certificate_dependency.json | C |
| registry_semantics.json | E |

---

## G13 Correction Plan

| Document | Correction |
|----------|------------|
| PHASE_2A_G13_FINAL_REPORT.md | Remove "connects to cert3.nesys.jp" and "retrieves certificate" |
| NESYSERVICE_CERTIFICATE_CONTRACT.md | Correct "retrieve NESYS certificates" and "Private key required" |
| NESYSERVICE_NETWORK_CONTRACT.md | Correct "connects to cert3.nesys.jp for certificate operations" |
| artifacts/phase_2a_g13/runtime_contract.json | Update if any JSON claims overstated |

---

## Execution Order

1. G13 corrections (first, before any new analysis)
2. Workstream A: Service Registration Contract
3. Workstream B: Service Installer Mode
4. Workstream C: Certificate Data Flow
5. Workstream D: cert3.nesys.jp Relationship
6. Workstream E: Registry Defaults
7. Workstream F: File-Path Dependencies
8. Workstream G: Offline Registration Manifest
9. Workstream H: Safe-to-Register Decision
10. Final Report
11. Quality Gates
12. Commit
