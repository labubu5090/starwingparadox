# Phase 2A-G13 IDA Analysis Plan

**Phase**: 2A-G13  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Analysis Strategy

### Objective

Use IDA Pro 9.3 to perform evidence-based static analysis of three executables to reconstruct the missing runtime contract between the game, Windows Service Control Manager, Registry, certificate store, and the named pipe.

### Safety Boundaries

- Static analysis only
- No patching or rewriting original executables
- No bypassing authentication or integrity checks
- No suppressing certificate validation
- No forging or installing certificates
- No extracting private keys
- No contacting production NESYS hosts
- No emulating production infrastructure
- No creating fake named pipes for the game
- No registering NesysService yet
- No creating Registry values yet
- No executing binaries through IDA debugger
- No altering Windows services, scheduled tasks or startup entries
- No recording secrets or key material

---

## Analysis Target A: NesysService.exe

### A.1 Windows Service Identity

| Objective | Method |
|-----------|--------|
| ServiceMain entry point | Locate string "ServiceMain" and cross-references |
| Service name | Locate string "NesysService" and trace to StartServiceCtrlDispatcher |
| RegisterServiceCtrlHandler usage | Locate import and cross-references |
| Service control handler | Trace RegisterServiceCtrlHandler return value usage |
| Accepted service controls | Analyze service control handler switch cases |
| Startup state transitions | Trace SetServiceStatus calls with SERVICE_RUNNING, etc. |
| Stop and shutdown handling | Analyze service control handler for SERVICE_STOP, SERVICE_SHUTDOWN |
| Dependency or parent-process validation | Search for parent process checks or dependency strings |
| Command-line argument handling | Analyze main entry point for argc/argv usage |

### A.2 Registry Contract

| Objective | Method |
|-----------|--------|
| Registry API calls | Locate RegOpenKeyExA, RegQueryValueExA imports and cross-references |
| Root hive | Identify HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER constants |
| Subkey path | Extract string arguments to RegOpenKeyExA |
| Value name | Extract string arguments to RegQueryValueExA |
| Expected value type | Analyze Registry API call patterns |
| Read/write/delete operation | Classify Registry operations |
| Default or fallback behavior | Analyze code paths when Registry values are missing |
| Code paths affected | Trace Registry read results to control flow |

### A.3 Named-Pipe Contract

| Objective | Method |
|-----------|--------|
| Pipe name references | Locate string "\\.\pipe\" and "nesys_games" |
| Server/client role | Analyze CreateNamedPipeA vs CreateFile usage |
| CreateNamedPipe call sites | Locate import and cross-references |
| Pipe mode | Analyze dwOpenMode and dwPipeMode parameters |
| Buffer sizes | Analyze nInBufferSize, nOutBufferSize parameters |
| Timeout values | Analyze nDefaultTimeOut parameter |
| Connection sequence | Trace ConnectNamedPipe, WaitNamedPipe usage |
| Message framing | Analyze ReadFile, WriteFile usage patterns |
| Operation identifiers | Locate LCOMMAND/SCOMMAND string references |
| Request/response structures | Analyze message buffer handling |
| Handshake state machine | Trace pipe communication flow |
| Validation checks | Analyze error handling in pipe operations |
| Error paths | Trace pipe error handling code |
| Identity/PID/session/token validation | Search for impersonation or validation APIs |

### A.4 Certificate Contract

| Objective | Method |
|-----------|--------|
| CertOpenStore call sites | Locate import and cross-references |
| Certificate store provider | Analyze dwCertStoreType parameter |
| Store name | Analyze lpszProvName parameter |
| Store location or flags | Analyze dwFlags parameter |
| Certificate search criteria | Trace CertFindCertificateInStore usage |
| Subject, issuer, thumbprint references | Extract string arguments |
| Private key requirement | Search for CryptAcquireContext or CryptSign |
| TLS/client-auth usage | Analyze WinHTTP credential usage |
| Behavior when lookup fails | Trace CertOpenStore return value handling |
| cert3.nesys.jp references | Locate string and trace network usage |

### A.5 Network Contract

| Objective | Method |
|-----------|--------|
| Hostname references | Locate cert3.nesys.jp, data.nesys.jp, nesys.taito.co.jp strings |
| Port identification | Analyze WinHttpConnect parameters |
| Protocol/library usage | Identify WinHTTP vs Winsock usage |
| URL/endpoint construction | Analyze format string patterns |
| DNS resolution | Trace gethostbyname usage |
| TLS initialization | Trace WinHttpOpen, WinHttpSetCredentials |
| Timeout and retry logic | Analyze WinHttpSetTimeouts and retry loops |
| Offline and failure behavior | Trace network error handling |

### A.6 Configuration and Environment

| Objective | Method |
|-----------|--------|
| Environment variable reads | Locate GetEnvironmentVariable calls |
| INI/XML/JSON config paths | Extract file path strings |
| ProgramData/AppData paths | Search for known Windows paths |
| Working-directory assumptions | Analyze GetCurrentDirectory usage |
| Command-line arguments | Analyze main entry point |
| Mutexes | Trace CreateMutexA usage |
| Events | Trace CreateEventA usage |
| Shared memory | Search for CreateFileMapping |
| Named kernel objects | Locate all named object references |
| Expected Windows user/service account | Analyze impersonation or account references |

---

## Analysis Target B: AcrGame.exe

| Objective | Method |
|-----------|--------|
| Launcher/bootstrapper/game executable | Analyze PE subsystem and imports |
| Child processes | Trace CreateProcessW usage |
| Command-line construction | Analyze lpCommandLine parameter |
| Working-directory setup | Analyze lpCurrentDirectory parameter |
| Environment variables | Trace GetEnvironmentVariable calls |
| Registry reads | Trace RegOpenKeyExA usage |
| Service-control API usage | Search for Service-related imports |
| Named-pipe references | Search for pipe string references |
| References to NesysService.exe | Search for string references |
| Wait/retry logic for NESYS readiness | Analyze WaitForSingleObject usage |
| Exit-code handling | Trace ExitProcess calls |
| Whether it starts AcrGame-Win64-Shipping.exe | Analyze CreateProcessW target |
| Whether it is a wrapper | Analyze function structure |

---

## Analysis Target C: AcrGame-Win64-Shipping.exe

| Objective | Method |
|-----------|--------|
| References to \\.\pipe\nesys_games | Search for pipe string references |
| CreateFile or pipe client initialization | Locate CreateFileA/W usage |
| Service or process checks | Search for service-related API usage |
| Registry/configuration reads | Trace Registry API usage |
| Command-line parsing | Analyze main entry point |
| Environment-variable reads | Trace GetEnvironmentVariable calls |
| Expected parent process | Search for parent process validation |
| Startup state machine | Analyze initialization sequence |
| NESYS initialization failure path | Trace error handling |
| Retry and timeout behavior | Analyze retry loops and timeouts |
| Error strings | Extract error message strings |

---

## IDA Workflow

### For Each Executable

1. Calculate and record:
   - File size
   - SHA-256
   - PE timestamp
   - Architecture
   - Image base
   - Entry point
   - Imported DLLs
   - Relevant imported functions

2. Create a separate IDA database

3. Allow initial auto-analysis to finish

4. Review:
   - Imports
   - Strings
   - Names
   - Functions
   - Cross references
   - Entry point
   - TLS callbacks if present
   - Exception/unwind metadata where useful

5. Rename only positively identified functions and variables

6. Prefix analyst-created names consistently:
   - swp_service_
   - swp_pipe_
   - swp_cert_
   - swp_registry_
   - swp_network_
   - swp_launch_

7. Add repeatable comments containing:
   - Evidence
   - Confidence
   - Unresolved assumptions

8. Export evidence without modifying the original executable

---

## Evidence Standard

Every conclusion must include:

- Executable name
- Function address or RVA
- Referenced import/string
- Relevant cross-reference
- Concise pseudocode or control-flow explanation
- Confidence:
  - CONFIRMED
  - HIGH
  - MEDIUM
  - LOW
- Unresolved question, if any

Do not report guessed Registry paths, service names, certificate identifiers, commands or protocol structures as facts.

Separate:
- Directly observed evidence
- Analyst interpretation
- Unresolved hypothesis

---

## Output Documents

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

## Classification Rules

Choose exactly one final classification:

1. **STATIC_RUNTIME_CONTRACT_RECOVERED**
   Service identity, Registry/configuration requirements and game/service pipe startup contract are sufficiently evidenced.

2. **PARTIAL_STATIC_RUNTIME_CONTRACT**
   Some runtime dependencies are recovered but one or more critical startup elements remain unresolved.

3. **SYSTEM_DRIVE_ARTIFACTS_STILL_REQUIRED**
   Static analysis confirms that critical service/configuration material cannot be reconstructed from the D-drive binaries.

4. **UNSAFE_BYPASS_REQUIRED**
   Progress would require authentication bypass, binary patching, certificate forgery, production impersonation or another prohibited action. Stop without implementing it.

---

## Conclusion

The analysis plan covers comprehensive static analysis of all three executables with focus on service control, registry, named pipe, certificate, network, and configuration contracts.
