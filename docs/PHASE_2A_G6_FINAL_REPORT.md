# Phase 2A-G6 Final Report: D-Drive Runtime Reconstruction and NesysService Retest

## 1. Phase Status

**Status**: D_LAYOUT_NO_EFFECT

The D: drive was successfully reconstructed and mounted, but NesysService still exits
immediately with code -1. The D: drive is necessary but not sufficient.

## 2. D-Drive Reconstruction

### Method Used
- **Method**: SUBST (filesystem path substitution)
- **Reason**: Hyper-V VHDX creation requires admin privileges
- **Source**: `X:\StarwingParadox\D DRIVE CONTENTS`
- **Target**: `D:\`
- **Files**: 217 files, 7.9 MB

### Verification
- D: drive mounted successfully
- All required directories created
- All required files present
- OpenKey.json present (96 bytes)
- SaveData.json present (3,771 bytes)
- NesysService.exe present (548,352 bytes)

### Tooling Created
- `tools/game/d-drive/create-starwing-test-vhd.ps1`
- `tools/game/d-drive/mount-starwing-test-vhd.ps1`
- `tools/game/d-drive/populate-starwing-test-vhd.ps1`
- `tools/game/d-drive/verify-starwing-test-vhd.ps1`
- `tools/game/d-drive/dismount-starwing-test-vhd.ps1`
- `tools/game/d-drive/remove-starwing-test-vhd.ps1`

## 3. NesysService Retest Results

### Test A: Working dir = NesysService directory
- **Exit code**: -1
- **Lifetime**: <1 second
- **Named pipes created**: None
- **Files created**: None

### Test B: Working dir = WindowsNoEditor
- **Exit code**: -1
- **Lifetime**: <1 second

### Test C: Working dir = D:\ root
- **Exit code**: -1
- **Lifetime**: <1 second

### Test D: Via cmd.exe
- **Exit code**: 1
- **Lifetime**: <1 second

### Test E: D: drive present + game launched
- **NesysService**: Still exits -1
- **Game NESYS status**: Still offline (CertError)
- **Named pipes**: None created

## 4. D-Drive Effect Analysis

| Metric | Without D: | With D: | Change |
|--------|-----------|---------|--------|
| NesysService exit code | -1 | -1 | No change |
| NesysService lifetime | <1s | <1s | No change |
| Named pipes created | None | None | No change |
| Game NESYS status | Offline | Offline | No change |
| CertError count | 27+ | 27+ | No change |
| D: file operations | None | None | No change |

**Conclusion**: D_LAYOUT_NO_EFFECT — The D: drive alone does not resolve NesysService initialization failure.

## 5. NesysService Initialization Requirements (Observed)

From binary analysis, NesysService performs these initialization steps:

1. **CreateMutex** — Prevents multiple instances
2. **GetLowerMacAddrAdapter** — Gets machine MAC address (IPHLPAPI.DLL)
3. **Event download class initialization** — Sets up event data download
4. **GetLinkState** — Checks network link state
5. **Interface watch class initialization** — Monitors network interfaces
6. **DHCP renewal** — Renews DHCP lease
7. **WINHTTP initialization** — Connects to cert3.nesys.jp
8. **Certificate verification** — Uses CRYPT32.dll
9. **Named pipe creation** — `\\.\pipe\nesys_games\%s%s`
10. **Thread creation** — `_beginthreadex()` for pipe server

**Failure point**: Unknown — NesysService exits before producing any visible output.

## 6. What Remains Unknown

| Item | Status |
|------|--------|
| Exact failure point in initialization | UNKNOWN |
| Whether mutex creation succeeds | UNKNOWN |
| Whether MAC address retrieval succeeds | UNKNOWN |
| Whether network connection to cert3.nesys.jp succeeds | UNKNOWN |
| Whether certificate verification succeeds | UNKNOWN |
| Whether named pipe creation is attempted | UNKNOWN |
| Required command-line arguments | UNKNOWN |
| Required parent process | UNKNOWN |
| Required registry keys | NOT_PROVEN |
| Required certificates | NOT_PROVEN |

## 7. Game Behavior with D: Drive

The game log shows the same sequence regardless of D: drive presence:

```
LogNesys: UCPP_NesysControl::RequestNetworkInfo OK.
LogNesys: UCPP_NesysControl::RequestNetworkInfo Error.
LogBoot: ACPP_GameModeBoot::NesysControlErrorMessage / ENesysNetworkServerMessage[CertError]
```

The `RequestNetworkInfo OK` followed by `Error` suggests the game's NESYS client plugin
can communicate with something (possibly itself or a local check), but the overall NESYS
initialization fails with CertError.

## 8. Conclusion

The D: drive reconstruction was successful but did not resolve the NesysService initialization
failure. The root cause is NOT simply a missing D: drive. NesysService requires additional
runtime context that was not provided by the D: drive alone.

**Primary blocker**: NesysService initialization failure (unknown exact cause)

**Recommended next steps**:
1. Use Process Monitor to trace NesysService file/registry/network access
2. Determine the exact failure point in initialization
3. Check if NesysService needs specific command-line arguments
4. Check if NesysService needs to be started by a specific launcher
5. Check if network access to cert3.nesys.jp is required for initialization

## 9. Safe Rollback

- D: drive dismounted successfully
- No X: files modified
- No registry changes
- No certificates installed
- No binaries patched
- VHDX not created (subst used instead)
