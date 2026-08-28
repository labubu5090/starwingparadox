# Phase 2A-G15 Initial Baseline

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: IN_PROGRESS  
**Predecessor**: 2A-G14 (EXTERNAL_REGISTRATION_REQUIRED)

---

## Starting State

### G14 Final Classification

`EXTERNAL_REGISTRATION_REQUIRED`

### G14 Key Findings

1. Service does NOT contain self-installation code
2. Registration was performed externally (installer, system image, or deployment package)
3. Certificate private key acquisition NOT_SHOWN
4. cert3.nesys.jp purpose UNRESOLVED
5. Registry default values NOT_SHOWN
6. Service registration is NOT safe or complete

### G14 Recovered Evidence

| Component | Status | Confidence |
|-----------|--------|------------|
| Service name | NesysService | CONFIRMED |
| Binary path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | CONFIRMED |
| Self-installation | NOT_FOUND | CONFIRMED |
| Registration mechanism | EXTERNAL | CONFIRMED |
| Certificate store | MY\.Default | CONFIRMED |
| Certificate subject | nesys | CONFIRMED |
| Private key | PROBABLY_REQUIRED (inference) | LOW |
| cert3.nesys.jp | UNRESOLVED | UNRESOLVED |
| Registry values | 8 values (CONFIRMED) | HIGH |
| Safe to register | FALSE | CONFIRMED |

---

## G15 Objectives

1. Perform complete deployment artifact inventory
2. Inspect archives and disk images
3. Analyze Windows installer metadata
4. Inspect scripts and configurations
5. Search logs and textual residue
6. Correlate PE resources and signatures
7. Reconstruct service configuration
8. Identify non-secret registry provisioning
9. Determine startup orchestration
10. Create authorized recovery source matrix
11. Normalize G14 classification

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
| No archive mounting | CONFIRMED |
| No image booting | CONFIRMED |
| No installer execution | CONFIRMED |

---

## Evidence Standard

Every recovered item must include:
- Source path
- SHA-256
- Line, table, resource, offset or record location
- Minimum relevant excerpt or structured value
- Analyst interpretation
- Confidence
- Unresolved limitation

Confidence values:
- CONFIRMED
- HIGH
- MEDIUM
- LOW
- NOT_FOUND
- SYSTEM_DRIVE_REQUIRED
- INSTALLER_REQUIRED

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
