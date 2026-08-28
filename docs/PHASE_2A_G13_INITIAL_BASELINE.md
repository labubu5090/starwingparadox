# Phase 2A-G13 Initial Baseline

**Phase**: 2A-G13  
**Date**: 2026-08-28  
**Status**: VERIFIED  

---

## Git State

| Metric | Value |
|--------|-------|
| Current HEAD | `2c53469` |
| Branch | master |
| Working tree | clean (no staged changes) |

### Commit Verification

| Commit | Message | Verified |
|--------|---------|----------|
| `2c53469` | docs: identify Starwing original runtime gaps | YES |
| `58e9934` | docs: update PROGRESS.md with G11 upstream audit results | YES |
| `99f55ed` | docs: complete upstream repository launch instructions audit | YES |
| `5388190` | docs: establish Starwing OpenKey provenance boundary | YES |
| `d8b7c6c` | fix: load generated protobuf for Starwing TCP runtime | YES |

---

## IDA Pro Verification

| Metric | Value |
|--------|-------|
| IDA Pro path | `C:\Program Files\IDA Professional 9.3\ida.exe` |
| Installed | YES |

---

## Executable Verification

| Executable | Path | Size | SHA-256 |
|------------|------|------|---------|
| NesysService.exe | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | 548,352 | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` |
| AcrGame.exe | X:\StarwingParadox\WindowsNoEditor\AcrGame.exe | 161,280 | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` |
| AcrGame-Win64-Shipping.exe | X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe | 163,119,104 | `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4` |

---

## G12 Documents Verification

| Document | Path | Exists |
|----------|------|--------|
| G12 Initial Baseline | docs/PHASE_2A_G12_INITIAL_BASELINE.md | YES |
| G12 Final Report | docs/PHASE_2A_G12_FINAL_REPORT.md | YES |
| Original Runtime Artifact Inventory | docs/ORIGINAL_RUNTIME_ARTIFACT_INVENTORY.md | YES |
| Original Launcher Candidates | docs/ORIGINAL_LAUNCHER_CANDIDATES.md | YES |
| Original Startup Sequence | docs/ORIGINAL_STARTUP_SEQUENCE.md | YES |
| NesysService Invocation Evidence | docs/NESYSERVICE_INVOCATION_EVIDENCE.md | YES |
| Original System Drive Gap Analysis | docs/ORIGINAL_SYSTEM_DRIVE_GAP_ANALYSIS.md | YES |
| NesysService Standalone Capability | docs/NESYSERVICE_STANDALONE_CAPABILITY.md | YES |

---

## Test Baseline

| Metric | Value |
|--------|-------|
| Tests collected | 835 |
| Tests passed | 834 |
| Tests skipped | 1 |
| Tests failed | 0 |
| Warnings | 197 (aiosqlite event loop cleanup) |

---

## Static Analysis

| Tool | Version | Result |
|------|---------|--------|
| Ruff | - | 0 errors |
| Mypy | 2.3.1 | 0 errors on 64 source files |

---

## Conclusion

All baseline checks pass. Ready for G13 IDA static analysis.
