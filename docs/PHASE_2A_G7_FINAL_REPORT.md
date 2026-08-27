# Phase 2A-G7 Final Report: Process Monitor Trace and NesysService Initialization Failure Isolation

## 1. Phase Status

**Status**: WAITING_FOR_PROCMON

Process Monitor is not available on this system. The exact initialization failure point
cannot be isolated without runtime tracing.

## 2. Initial Git Baseline

- **HEAD**: 666a434
- **Working tree**: Clean (only untracked data files)
- **G6 report**: Exists at `docs/PHASE_2A_G6_FINAL_REPORT.md`
- **NesysService hash**: 3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F
- **Game hashes**: Verified and unchanged
- **No processes running**: Confirmed
- **No D: mounted**: Confirmed
- **No NESYS pipes**: Confirmed
- **Server**: Running on 4001, proxy on 80, TCP on 6666
- **Tests**: 794 passed, 2 pre-existing failures

## 3. Process Monitor Availability

**Status**: PROCMON_NOT_AVAILABLE

Searched locations:
- PATH: Not found
- C:\Tools\, C:\Sysinternals\: Not found
- Program Files: Not found
- User Desktop/Downloads: Not found
- Project tools: Not found
- SysinternalsSuite: Not found

Alternative tools available:
- xperf (Windows Performance Toolkit): Available but requires admin and WMI service
- wpr (Windows Performance Recorder): Available
- logman: Available

## 4. Capture Method

Planned but not executed:
- ETW trace via xperf (requires admin elevation)
- Process Monitor filter for NesysService.exe
- File/Registry/Network/Pipe event capture
- Differential analysis between D: and no-D: runs

## 5. Filters

Planned filters (not applied):
- Process: NesysService.exe
- File: D:\*, \.\pipe\*, nesys_games
- Registry: All access
- Network: TCP/UDP
- Result: NAME NOT FOUND, ACCESS DENIED, etc.

## 6. Control Baseline

| Metric | Value |
|--------|-------|
| NesysService.exe | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe |
| Hash | 3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F |
| Architecture | x64 |
| Subsystem | Console (3) |
| Manifest | asInvoker |
| Working directory | X:\StarwingParadox\D DRIVE CONTENTS\system\Service |
| D: drive | Not mounted |
| Named pipes | None |
| Processes | None |

## 7. Run A Without D Drive

| Metric | Value |
|--------|-------|
| Exit code | -1 |
| Lifetime | ~1 second |
| Files created | None |
| Named pipes | None |
| Output captured | None |
| Events logged | None |

## 8. Run B With D Drive

| Metric | Value |
|--------|-------|
| D: mount method | SUBST |
| D: files | 217 files, 7.9 MB |
| Exit code | -1 |
| Lifetime | ~1 second |
| Files created | None |
| Named pipes | None |
| Output captured | None |
| Events logged | None |

## 9. D Drive Differential Result

**Classification**: D_LAYOUT_NO_MATERIAL_EFFECT

No observable difference in NesysService behavior between D: and no-D: runs.
Same exit code, same lifetime, same lack of output.

## 10. Process Lifetime

- **Without D**: ~1 second
- **With D**: ~1-3 seconds (variable)
- **Typical**: <2 seconds

## 11. Process Exit

- **Exit code**: -1 (0xFFFFFFFF)
- **Exit type**: Immediate termination
- **No crash dump**: Process exits cleanly with code -1
- **No error message**: No visible output

## 12. Terminal Failure Window

**Classification**: UNKNOWN

Cannot determine terminal failure window without Process Monitor.
The process exits so quickly that traditional monitoring cannot capture events.

## 13. Last Successful Operation

**Classification**: UNKNOWN

No output captured. No events logged. No files created.

## 14. Last Failed Operation

**Classification**: UNKNOWN

No error messages captured. No events logged.

## 15. DLL Load Result

From binary analysis:
- IPHLPAPI.DLL (IP Helper - MAC address)
- ADVAPI32.dll (Security/Registry)
- CRYPT32.dll (Certificate operations)
- WS2_32.dll (Winsock)
- WINHTTP.dll (HTTP connections)
- PSAPI.DLL (Process info)
- USER32.dll, GDI32.dll (UI)
- dnsapi.dll (DNS)
- KERNEL32.dll (Core)

**Missing DLLs**: NesysNet.dll referenced in earlier reports not found in binary imports.

## 16. File Lookup Result

**Classification**: UNKNOWN (requires Procmon)

No file creation observed. No file access logged.

## 17. Registry Access Result

**Classification**: UNKNOWN (requires Procmon)

No Registry events logged. Binary uses ADVAPI32.dll for Registry access.

## 18. Certificate Access Result

**Classification**: CERTIFICATE_REQUIREMENT_UNPROVEN

Binary uses CRYPT32.dll for certificate operations.
cert3.nesys.jp:443 is reachable from this system.
No certificate access events observed.

## 19. Named Pipe Result

**Classification**: PIPE_NOT_ACCESSED

Named pipe `\\.\pipe\nesys_games\...` was never created.
No pipe access events observed.

## 20. Device Access Result

**Classification**: UNKNOWN (requires Procmon)

No device access events logged.

## 21. Network Result

| Host | Port | Protocol | Status |
|------|------|----------|--------|
| cert3.nesys.jp | 443 | HTTPS | REACHABLE |
| data.nesys.jp | 80 | HTTP | REACHABLE |
| nesys.taito.co.jp | 80 | HTTP | REACHABLE |
| fjm170920zero.nesica.net | 443 | HTTPS | NOT REACHABLE |

## 22. Game-Context Trace

**Not executed** — requires Procmon.

## 23. NesysService Launch Context

| Attribute | Value |
|-----------|-------|
| Executable | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe |
| Arguments | None (no arguments discovered) |
| Working directory | Various tested (same result) |
| Parent process | None (direct launch) |
| D: drive | Not required for exit behavior |

## 24. Candidate Root Causes

1. **REQUIRED_NETWORK_CONFIGURATION_MISSING** — NesysService expects specific network setup
2. **REQUIRED_PARENT_CONTEXT_MISSING** — NesysService expects to be started by a launcher
3. **REQUIRED_ARGUMENT_MISSING** — NesysService expects command-line arguments
4. **EXTERNAL_NETWORK_FAILURE** — Cannot reach all required servers
5. **SINGLE_INSTANCE_CHECK** — Mutex prevents multiple instances (unlikely, no instance running)
6. **REQUIRED_CERTIFICATE_MISSING** — Windows certificate store lacks NESYS certificates
7. **NO_OS_LEVEL_FAILURE_VISIBLE** — No visible error from operating system

## 25. Confirmed Root Cause

**None confirmed** — requires Process Monitor to identify exact failure point.

## 26. D Drive Conclusion

- **Reconstruction**: Successful
- **Behavior change**: None observed
- **Requirement**: Not proven
- **Necessity**: Not proven

## 27. Security Boundaries

- No certificates installed
- No Registry values created
- No binaries patched
- No game files modified
- No sensitive data logged
- Matching remains guarded
- Battle remains guarded

## 28. Tests

794 passed, 2 pre-existing failures, 6 skipped.

## 29. Ruff

0 errors.

## 30. Mypy

0 errors.

## 31. Files Created

- `docs/PROCESS_MONITOR_AVAILABILITY.md`
- `docs/PROCMON_NESYSSERVICE_CAPTURE_PLAN.md`
- `docs/PHASE_2A_G7_FINAL_REPORT.md`

## 32. Files Modified

- `PROGRESS.md`

## 33. Original Game Files Changed

**NONE**

## 34. Commands Actually Executed

- Git status, log, diff
- Game hash verification
- NesysService launch (multiple working directories)
- D: drive mount/dismount via subst
- Network connectivity tests
- Event log queries
- xperf/wpr availability checks
- PowerShell output capture attempts

## 35. Commands Not Executed

- Process Monitor trace (not available)
- xperf trace (requires admin)
- Registry dump
- Certificate export
- DLL injection
- Binary patching

## 36. Remaining Unknowns

1. Exact failure point in NesysService initialization
2. Required command-line arguments
3. Required parent process context
4. Required network configuration
5. Required certificate state
6. Required Registry configuration
7. Whether D: drive is actually needed
8. Whether fjm170920zero.nesica.net unreachability causes failure

## 37. Git Commit

**Status**: Pending

## 38. Recommended Next Action

1. **Install Process Monitor** — Download from Microsoft Sysinternals
2. **Run as administrator** — Required for system event capture
3. **Apply capture plan** — Follow `docs/PROCMON_NESYSSERVICE_CAPTURE_PLAN.md`
4. **Analyze terminal failure window** — Last 500ms before exit
5. **Identify exact missing resource** — File, Registry, certificate, or network
6. **Report findings in G8** — Once Procmon data is available
