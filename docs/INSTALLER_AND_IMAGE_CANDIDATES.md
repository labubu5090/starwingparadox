# Installer and Image Candidates

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

No installer packages, disk images, or recovery images were found in the operator-owned content. The only candidate file with an installer-like extension is AcrGame.inf, which is a binary file that does not contain installer metadata.

---

## Archive and Disk-Image Inspection

### Archives Found

| Type | Count | Notes |
|------|-------|-------|
| .zip | 0 | NONE |
| .7z | 0 | NONE |
| .rar | 0 | NONE |
| .tar | 0 | NONE |
| .gz | 0 | NONE |

**No archive files found.**

### Disk Images Found

| Type | Count | Notes |
|------|-------|-------|
| .iso | 0 | NONE |
| .wim | 0 | NONE |
| .esd | 0 | NONE |
| .swm | 0 | NONE |
| .img | 0 | NONE |
| .vhd | 0 | NONE |
| .vhdx | 0 | NONE |
| .gho | 0 | NONE |
| .tib | 0 | NONE |

**No disk image files found.**

---

## Windows Installer Metadata

### MSI Files Found

| Type | Count | Notes |
|------|-------|-------|
| .msi | 0 | NONE |
| .msp | 0 | NONE |
| .mst | 0 | NONE |

**No Windows Installer packages found.**

### Installer Databases Found

| Type | Count | Notes |
|------|-------|-------|
| setup.exe | 0 | NONE |
| install.exe | 0 | NONE |
| msiexec.exe | 0 | NONE |

**No installer databases found.**

---

## Candidate File Analysis

### AcrGame.inf

| Property | Value |
|----------|-------|
| Path | X:\StarwingParadox\WindowsNoEditor\AcrGame.inf |
| Size | 267 bytes |
| Extension | .inf |
| File signature | Binary (not text) |
| First bytes | A6 AF 64 8B E0 36 75 29 23 BE 84 E1 6C D6 AE 52 |
| Text encoding | NOT_TEXT |
| Installer metadata | NOT_FOUND |
| Service registration | NOT_FOUND |
| Registry entries | NOT_FOUND |
| Confidence | LOW |
| Classification | UNKNOWN_BINARY |

**Analysis**: The AcrGame.inf file is a binary file that does not contain standard INF (Setup Information) file content. It does not contain installer metadata, service registration, or registry entries. The file may be encrypted, compressed, or a different file type masquerading with an .inf extension.

---

## PE Resource and Signature Correlation

### NesysService.exe

| Property | Value |
|----------|-------|
| Path | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe |
| Size | 548,352 bytes |
| SHA-256 | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` |
| Architecture | PE32+ (64-bit) |
| Product name | NesysService |
| Company | Taito |
| PE subsystem | Console |
| Signature | None verifiable |
| Classification | SUPPORT_SERVICE |

**Analysis**: NesysService.exe is a Windows Service binary, not an installer. It contains service control APIs but no installation logic.

### AcrGame.exe

| Property | Value |
|----------|-------|
| Path | X:\StarwingParadox\WindowsNoEditor\AcrGame.exe |
| Size | 161,280 bytes |
| SHA-256 | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` |
| Architecture | PE32+ (64-bit) |
| Product name | AcrGame |
| Company | Taito |
| PE subsystem | GUI |
| Signature | None verifiable |
| Classification | GAME_EXECUTABLE |

**Analysis**: AcrGame.exe is a game launcher executable, not an installer. It contains CreateProcessW for launching AcrGame-Win64-Shipping.exe but no installation logic.

### AcrGame-Win64-Shipping.exe

| Property | Value |
|----------|-------|
| Path | X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe |
| Size | 163,119,104 bytes |
| SHA-256 | `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4` |
| Architecture | PE32+ (64-bit) |
| Product name | AcrGame |
| Company | Taito |
| PE subsystem | Windows subsystem |
| Signature | None verifiable |
| Classification | GAME_EXECUTABLE |

**Analysis**: AcrGame-Win64-Shipping.exe is the main game binary, not an installer. It is the UE4 shipping build of the game.

---

## Classification

**INSTALLER_CANDIDATES**: `NOT_FOUND`

**DISK_IMAGE_CANDIDATES**: `NOT_FOUND`

**RECOVERY_IMAGE_CANDIDATES**: `NOT_FOUND`

**Rationale**:
- No installer packages found
- No disk images found
- No recovery images found
- AcrGame.inf is a binary file without installer metadata
- All executables are game or service binaries, not installers

---

## Conclusion

No installer packages, disk images, or recovery images were found in the operator-owned content. The only candidate file with an installer-like extension is AcrGame.inf, which is a binary file that does not contain installer metadata.

**Classification**: `NO_INSTALLER_OR_IMAGE_CANDIDATES`

The operator-owned content does not contain any deployment artifacts that could register or provision NesysService.

---

## G15 Audit Notes

This document was created in Phase 2A-G15 to identify installer and image candidates. No installer packages, disk images, or recovery images were found. The AcrGame.inf file was analyzed and determined to be a binary file without installer metadata.
