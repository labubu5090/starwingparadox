# Original Startup Model Correction

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: C

## Previously Documented "Ideal Startup Sequence"

The following sequence was previously inferred from static analysis and documented in ORIGINAL_RUNTIME_RECONSTRUCTION.md:

1. Windows boot → EWF initialization
2. CmdFile update system
3. NesysService.exe starts (Windows Service)
4. NesysService connects to cert3.nesys.jp
5. NesysService retrieves certificate
6. NesysService creates named pipe
7. AcrGame.exe launches
8. AcrGame-Win64-Shipping.exe starts
9. Game connects to named pipe
10. Command exchange begins

**This sequence is NOT confirmed and must not remain represented as confirmed.**

## Model 1: CONFIRMED OBSERVED RELATIONSHIPS

Only directly supported facts:

| Relationship | Evidence | Confidence |
|-------------|----------|------------|
| AcrGame.exe creates AcrGame-Win64-Shipping.exe | Binary imports (CreateProcessW) | CONFIRMED |
| AcrGame-Win64-Shipping.exe connects to \\.\pipe\nesys_games | Runtime logs | CONFIRMED |
| NesysService.exe is a Windows Service | Binary imports (StartServiceCtrlDispatcherA) | CONFIRMED |
| NesysService.exe creates named pipe | Binary imports (CreateNamedPipeA) | CONFIRMED |
| NesysService.exe reads registry | Binary imports (RegOpenKeyExA) | CONFIRMED |
| NesysService.exe accesses certificate store | Binary imports (CertOpenStore) | CONFIRMED |
| NesysService.exe uses WinHTTP | Binary imports (WinHttpOpen) | CONFIRMED |
| AcrGame.exe contains zero NesysService references | String analysis | CONFIRMED |
| EWF=1 indicates embedded system | File content | CONFIRMED |
| OpenKey.json exists in runtime | File content | CONFIRMED |

## Model 2: PLAUSIBLE BUT UNPROVEN ORIGINAL STARTUP MODEL

Hypotheses with explicit confidence and limitations:

| Step | Hypothesis | Confidence | Limitation |
|------|-----------|------------|------------|
| 1 | Windows boot initializes EWF | HIGH | EWF=1 confirmed, boot sequence not observed |
| 2 | Windows SCM starts NesysService | HIGH | Service registration not confirmed |
| 3 | NesysService creates named pipe | HIGH | Service context not confirmed |
| 4 | NesysService reads registry values | HIGH | Registry provisioning not confirmed |
| 5 | NesysService accesses certificate store | HIGH | Certificate installation not confirmed |
| 6 | AcrGame.exe launches AcrGame-Win64-Shipping.exe | CONFIRMED | Binary imports confirmed |
| 7 | Game connects to named pipe | CONFIRMED | Runtime logs confirmed |
| 8 | Game exchanges commands | HIGH | Protocol confirmed, semantics unknown |

## Model 3: CURRENT FAILURE MODEL

What is supported regarding the absent service, absent pipe, and observed offline result:

| Component | Status | Evidence | Impact |
|-----------|--------|----------|--------|
| NesysService registration | NOT_REGISTERED | Service Control Manager query | No service to start |
| Named pipe creation | NOT_CREATED | No pipe exists at \\.\pipe\nesys_games | Game cannot connect |
| Certificate installation | NOT_INSTALLED | Certificate store query | Cannot authenticate |
| Registry provisioning | NOT_PROVISIONED | Registry query | Service cannot configure |
| Game startup | SUCCESS | Runtime logs | Game starts offline |
| NESYS initialization | FAILURE | Runtime logs (CertError) | Game enters offline mode |
| TCP connection | BLOCKED | Runtime logs (bGameConnect) | Cannot connect to matching |
| HTTP matching | SUCCESS | Runtime logs | Game receives server list |

## Corrections Applied

| Original Claim | Correction | Reason |
|---------------|------------|--------|
| "NesysService connects to cert3.nesys.jp during every startup" | Hostname reference only | String ≠ network connection |
| "NesysService retrieves a certificate from cert3.nesys.jp" | Certificate store access only | Store API ≠ retrieval |
| "a private key is definitely required" | PROBABLY_REQUIRED | Inference, not confirmed |
| "certificate retrieval precedes named-pipe creation" | Not confirmed | No timing evidence |
| "AcrGame.exe is always the only valid launcher" | Not confirmed | Cannot determine alternatives |
| "Registry values have assumed defaults" | NOT_SHOWN | No default values found |
| "the service always runs under a particular account" | Not confirmed | No account evidence |
| "the service uses a particular automatic-start configuration" | Not confirmed | No start-type evidence |
