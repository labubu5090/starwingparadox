# NesysService Invocation Evidence

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Summary

NesysService.exe contains comprehensive evidence of its function and invocation requirements, but no external invocation evidence was found in the operator-owned content.

---

## NesysService.exe Binary Analysis

### String References Found

| Category | Strings | Evidence Strength |
|----------|---------|-------------------|
| **Service Control** | `StartServiceCtrlDispatcherA`, `RegisterServiceCtrlHandlerA`, `SetServiceStatus` | STRONG |
| **Named Pipe** | `\\.\pipe\`, `nesys_games`, `CreateNamedPipeA`, `ConnectNamedPipe`, `DisconnectNamedPipe`, `WaitNamedPipeA`, `SetNamedPipeHandleState`, `PeekNamedPipe` | STRONG |
| **Certificate** | `CertFindCertificateInStore()`, `CertOpenStore()`, `CertFreeCertificateContext`, `CertCloseStore`, `CertGetNameStringA`, `cert3.nesys.jp`, `certify.php` | STRONG |
| **Process Creation** | `CreateProcessA`, `GenerateConsoleCtrlEvent` | STRONG |
| **Registry** | `RegOpenKeyExA` | STRONG |
| **Mutex** | `CreateMutexA`, `ReleaseMutex` | STRONG |
| **Network** | `WSACreateEvent`, `WSAEventSelect`, `WSACloseEvent`, `WSAWaitForMultipleEvents`, `WSAEnumNetworkEvents` | STRONG |
| **Service Commands** | `LCOMMAND_SERVICE_VERSION_REQUEST`, `LCOMMAND_DESTROY_MY_SERVICE`, `SCOMMAND_SERVICE_VERSION_REPLY`, `SCOMMAND_DESTROY_MY_SERVICE` | STRONG |
| **Certificate Commands** | `SCOMMAND_CERT_ERROR`, `SCOMMAND_CERT_INIT_NOTICE`, `SCOMMAND_CERT_REGULAR_NOTICE` | STRONG |
| **Event Commands** | `LCOMMAND_EVENT_DOWNLOAD_REQUEST`, `LCOMMAND_EVENT_REQUEST_REQUEST`, `LCOMMAND_ROW_EVENTDATA_LIST_REQUEST`, `SCOMMAND_ROW_EVENTDATA_LIST_REPLY` | STRONG |
| **URL Patterns** | `%s://%s/service/card/%s`, `%s://%s/service/incom/%s`, `%s://%s/service/respone/%s`, `%s://%s/service/upload/%s` | STRONG |
| **Source Paths** | `..\src\ServiceMain.cpp`, `..\src\nesys_access\NesysEvent.cpp` | STRONG |
| **PDB Path** | `C:\alienbrainWork\all_development_solution\NESYS_support\NESiCAxLive\NesysService\bin\Release(NESYS_Game_cert3)\NesysServiceCert_x64.pdb` | STRONG |
| **Error Messages** | `error: CreateMutex()    code: 0x%08X`, `comunication error: nesys_cert request`, `certification error. code: 0x%08X`, `data received from pipe is too small. size=%d`, `pipe error: code=0x%08X` | STRONG |
| **Log Format** | `NESYS Service   : %s(c)` | STRONG |

---

## Invocation Analysis

### What NesysService Expects

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| **Windows Service context** | StartServiceCtrlDispatcherA, RegisterServiceCtrlHandlerA, SetServiceStatus | CONFIRMED |
| **Named pipe server** | `\\.\pipe\nesys_games`, CreateNamedPipeA, ConnectNamedPipe | CONFIRMED |
| **Certificate store access** | CertOpenStore, CertFindCertificateInStore | CONFIRMED |
| **Network access** | WSACreateEvent, WSAEventSelect, cert3.nesys.jp | CONFIRMED |
| **Mutex for single instance** | CreateMutexA, ReleaseMutex | CONFIRMED |
| **Registry access** | RegOpenKeyExA | CONFIRMED |
| **Process creation** | CreateProcessA | CONFIRMED |

### What NesysService Does NOT Require

| Requirement | Evidence | Strength |
|-------------|----------|----------|
| Command-line arguments | No argv parsing found | STRONG |
| Parent process | No parent process check | STRONG |
| Named event | Only mutex found | STRONG |
| Shared memory | No shared memory API | STRONG |
| Cabinet IO device | No USBIO reference | STRONG |
| Cabinet network adapter | No network adapter reference | STRONG |

---

## External Invocation Evidence

### Search Results

| Search Target | Result |
|---------------|--------|
| NesysService references in .ini files | NONE |
| NesysService references in .xml files | NONE |
| NesysService references in .json files | NONE |
| NesysService references in .log files | NONE |
| NesysService references in .txt files | NONE |
| nesys_games references in text files | NONE |
| Launcher references in text files | NONE (UE4 engine config only) |
| Service installation scripts | NONE |
| Service wrapper scripts | NONE |

### AcrGame.exe Analysis

| Search Target | Result |
|---------------|--------|
| NesysService string | NONE |
| nesys_games string | NONE |
| CreateProcessW | FOUND (standard UE4 pattern) |

**AcrGame.exe does NOT contain direct NesysService references.**

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| **Overall** | `EXECUTABLE_REFERENCE_ONLY` |
| **Binary self-evidence** | STRONG (comprehensive API usage) |
| **External invocation** | NONE (no scripts, no config, no references) |
| **Command-line arguments** | NOT_REQUIRED (no argv parsing) |
| **Parent process** | NOT_REQUIRED (no parent check) |
| **Service context** | REQUIRED (Windows Service APIs) |
| **Certificate** | REQUIRED (CertOpenStore, cert3.nesys.jp) |
| **Named pipe** | REQUIRED (\\.\pipe\nesys_games) |

---

## Conclusion

NesysService.exe is a Windows Service that:
1. Registers as a Windows Service (StartServiceCtrlDispatcherA)
2. Creates a named pipe server (`\\.\pipe\nesys_games`)
3. Accesses certificate store (CertOpenStore, cert3.nesys.jp)
4. Communicates with NESYS servers (URL patterns)
5. Creates mutex for single instance
6. Can create child processes (CreateProcessA)

**No external invocation evidence was found.** The service was likely installed by a system-drive component that is not present in the operator-owned content.

**Evidence Strength**: `EXECUTABLE_REFERENCE_ONLY`

The binary contains strong self-evidence of its function, but no external invocation evidence exists in the operator-owned content.
