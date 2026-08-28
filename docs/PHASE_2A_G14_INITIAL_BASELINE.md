# Phase 2A-G14 Initial Baseline

**Phase**: 2A-G14  
**Date**: 2026-08-28  
**Status**: IN_PROGRESS  
**Predecessor**: 2A-G13 (PARTIAL_STATIC_RUNTIME_CONTRACT)

---

## Starting State

### G13 Final Classification

`PARTIAL_STATIC_RUNTIME_CONTRACT`

### G13 Recovered Evidence

| Component | Status | Confidence |
|-----------|--------|------------|
| Service name | NesysService | CONFIRMED |
| Named pipe | `\\.\pipe\nesys_games` | CONFIRMED |
| Certificate store | MY\.Default | CONFIRMED |
| Registry path | `HKLM\SOFTWARE\taito\typex` | CONFIRMED |
| Network endpoints | 4 hostnames | CONFIRMED |
| Pipe protocol | 46 LCOMMAND, 44 SCOMMAND | CONFIRMED |
| Process launch | AcrGame.exe → AcrGame-Win64-Shipping.exe | CONFIRMED |

### G13 Missing Components

| Component | Status |
|-----------|--------|
| Service registration | MISSING |
| Certificate installation | MISSING |
| Registry configuration | MISSING |
| Startup sequence | MISSING |
| Service recovery | MISSING |

### G13 Overstated Claims Requiring Correction

| Document | Claim | Correction Required |
|----------|-------|---------------------|
| PHASE_2A_G13_FINAL_REPORT.md | "NesysService connects to cert3.nesys.jp" | Hostname reference ≠ connection |
| PHASE_2A_G13_FINAL_REPORT.md | "NesysService retrieves certificate" | Store API ≠ retrieval |
| NESYSERVICE_CERTIFICATE_CONTRACT.md | "retrieve NESYS certificates for authentication with cert3.nesys.jp" | Overstates evidence |
| NESYSERVICE_CERTIFICATE_CONTRACT.md | "Private key: (required for client auth)" | Inference, not confirmed |
| NESYSERVICE_NETWORK_CONTRACT.md | "connects to cert3.nesys.jp for certificate operations" | Hostname reference ≠ operations |

---

## G14 Objectives

1. Reconstruct Windows service registration contract from static evidence
2. Determine if NesysService has self-installation capability
3. Trace certificate data flow through IDA static analysis
4. Classify cert3.nesys.jp purpose without connecting
5. Determine registry value semantics
6. Identify file-path dependencies
7. Create offline registration manifest
8. Assess safe-to-register status

---

## Safety Boundaries

| Boundary | Status |
|----------|--------|
| No service registration | CONFIRMED |
| No certificate installation | CONFIRMED |
| No registry modification | CONFIRMED |
| No binary execution | CONFIRMED |
| No production network access | CONFIRMED |
| No fake named pipes | CONFIRMED |
| No certificate/key export | CONFIRMED |

---

## Evidence Standard

Every recovered item must include:
- Executable reference
- RVA or function address
- Import, string, or structure referenced
- Cross-reference
- Control-flow explanation
- Confidence level
- Unresolved limitation

Confidence values:
- CONFIRMED
- HIGH
- MEDIUM
- LOW
- NOT_FOUND

---

## Baseline SHA-256

| Executable | SHA-256 | Status |
|------------|---------|--------|
| NesysService.exe | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` | UNCHANGED |
| AcrGame.exe | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` | UNCHANGED |
| AcrGame-Win64-Shipping.exe | `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4` | UNCHANGED |

---

## Quality Gates Baseline

| Gate | Expected |
|------|----------|
| pytest | 834 passed, 1 skipped, 0 failed |
| Ruff | 0 errors |
| Mypy | 0 errors on 64 source files |
