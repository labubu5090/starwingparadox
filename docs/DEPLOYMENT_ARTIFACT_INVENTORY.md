# Deployment Artifact Inventory

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

Complete recursive inventory of all files under project root and D-drive backup found no installer packages, deployment scripts, recovery images, or service registration artifacts. The operator-owned content contains only game executables, game configuration files, and D-drive backup data.

---

## Inventory Summary

### Project Root (C:\Users\KAHO\Pictures\Starwing)

| Category | Count | Notes |
|----------|-------|-------|
| Documentation (.md) | 100+ | Project documentation |
| Configuration (.ini) | 52 | Game configuration files |
| Data (.json) | 60+ | Game data files |
| Database (.db) | 3 | SQLite databases |
| Scripts (.ps1) | 8 | PostgreSQL tools (archived) |
| Archives (.zip, .7z, etc.) | 0 | NONE |
| Installers (.msi, .exe) | 0 | NONE (excluding venv) |
| Registry files (.reg) | 0 | NONE |
| Batch files (.bat, .cmd) | 0 | NONE |
| Service configuration | 0 | NONE |

### D-Drive Backup (X:\StarwingParadox)

| Category | Count | Notes |
|----------|-------|-------|
| Executables (.exe) | 3 | Known three executables |
| Dynamic libraries (.dll) | 10+ | UE4 runtime libraries |
| Configuration (.ini) | 20+ | Game configuration |
| Data (.json) | 60+ | Game data files |
| Data (.csv) | 100+ | Game data tables |
| Images (.jpg, .png) | 4 | News/event images |
| Logs (.log) | 1 | Update/command log |
| Text (.txt) | 2 | System files |
| Archives (.zip, .7z, etc.) | 0 | NONE |
| Installers (.msi, .exe) | 0 | NONE |
| Registry files (.reg) | 0 | NONE |
| Batch files (.bat, .cmd) | 0 | NONE |
| Scripts (.ps1, .vbs) | 0 | NONE |
| Service configuration | 0 | NONE |
| Certificate files | 0 | NONE |

---

## Executables Found

| Executable | Path | Size | SHA-256 | Classification |
|------------|------|------|---------|----------------|
| AcrGame.exe | X:\StarwingParadox\WindowsNoEditor\AcrGame.exe | 161,280 | `97800621BB91A2706FBC68AD937679C874B17AC1B2389BDDF472BE9350E62D6C` | GAME_EXECUTABLE |
| AcrGame-Win64-Shipping.exe | X:\StarwingParadox\WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe | 163,119,104 | `CE4C89054BF7C4D833EE8AF455A485AC401EEAD12A80FFC077663A768FD47DC4` | GAME_EXECUTABLE |
| NesysService.exe | X:\StarwingParadox\D DRIVE CONTENTS\system\Service\NesysService.exe | 548,352 | `3A968F29B12050DD1B3AE7A8ACFE48BF98F1E6E11B0E090D3EB4B5A05B51D76F` | SUPPORT_SERVICE |

**No other executables found.**

---

## Script Files Found

| Type | Count | Notes |
|------|-------|-------|
| .bat | 0 | NONE |
| .cmd | 0 | NONE |
| .lnk | 0 | NONE |
| .reg | 0 | NONE |
| .vbs | 0 | NONE |
| .ps1 | 8 | PostgreSQL tools (archived, not deployment-related) |

**No deployment scripts found.**

---

## Archive Files Found

| Type | Count | Notes |
|------|-------|-------|
| .msi | 0 | NONE |
| .msp | 0 | NONE |
| .mst | 0 | NONE |
| .cab | 0 | NONE |
| .zip | 0 | NONE |
| .7z | 0 | NONE |
| .rar | 0 | NONE |
| .iso | 0 | NONE |
| .wim | 0 | NONE |
| .esd | 0 | NONE |
| .swm | 0 | NONE |
| .img | 0 | NONE |
| .vhd | 0 | NONE |
| .vhdx | 0 | NONE |
| .gho | 0 | NONE |
| .tib | 0 | NONE |

**No archive or disk-image files found.**

---

## Configuration Files Found

### Project Root

| File | Path | Size | Notes |
|------|------|------|-------|
| GameUserSettings.ini | config/rendering-tests/ | Various | Test configurations |
| Engine.ini | config/rendering-tests/ | Various | Test configurations |
| Game.ini | config/rendering-tests/ | Various | Test configurations |

### D-Drive Backup

| File | Path | Size | Notes |
|------|------|------|-------|
| GameUserSettings.ini | D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Config\WindowsNoEditor\ | Various | Game settings |
| Engine.ini | D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Config\WindowsNoEditor\ | Various | Engine settings |
| Game.ini | D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Config\WindowsNoEditor\ | Various | Game settings |
| DefaultEngine.ini | WindowsNoEditor\AcrGame\Config\ | Various | Default engine config |
| DefaultGame.ini | WindowsNoEditor\AcrGame\Config\ | Various | Default game config |
| DefaultInput.ini | WindowsNoEditor\AcrGame\Config\ | Various | Default input config |

---

## Data Files Found

### OpenKey Files

| File | Path | Size | Content |
|------|------|------|---------|
| OpenKey.json | D DRIVE CONTENTS\Saved\ACRSaved\SaveData\OpenKey.json | 96 | `{"IsOpen":1,"OpenVersion":56299,"OpenDate":"2018/11/21","OpenTime":"08:00:00"}` |
| OpenKeyEvent_Galaxy.json | D DRIVE CONTENTS\system\DUA\event\OpenKeyEvent_Galaxy.json | 80 | `{"OpenVersion":56299,"OpenDate":"2018/11/21","OpenTime":"08:00:00"}` |

### Save Data

| File | Path | Size |
|------|------|------|
| SaveData.json | D DRIVE CONTENTS\Saved\ACRSaved\SaveData\SaveData.json | 3,771 |
| RankingData.json | D DRIVE CONTENTS\Saved\ACRSaved\Ranking\RankingData.json | 67,903 |

### System Files

| File | Path | Size | Notes |
|------|------|------|-------|
| option.txt | D DRIVE CONTENTS\system\option.txt | 44 | ScreenType=0, EWF=1, MemoryLog=0 |
| Log.txt | D DRIVE CONTENTS\system\CmdFile\log\Log.txt | 1,725,914 | Update/command operations |
| update.log | D DRIVE CONTENTS\system\update.log | 0 | Empty |

---

## Missing Artifacts

| Artifact | Status | Impact |
|----------|--------|--------|
| Launcher executable | NOT_FOUND | Cannot determine startup sequence |
| .lnk shortcuts | NOT_FOUND | No startup folder placement |
| .bat/.cmd scripts | NOT_FOUND | No batch launch procedures |
| .reg files | NOT_FOUND | No registry configuration |
| .manifest files | NOT_FOUND | No application manifest |
| .vbs/.ps1 scripts | NOT_FOUND | No automation scripts |
| Certificate files | NOT_FOUND | No SSL/TLS certificates |
| Service wrapper | NOT_FOUND | No Windows Service configuration |
| Scheduled tasks | NOT_FOUND | No task scheduler entries |
| Registry entries | NOT_FOUND | No registry configuration |
| Installer packages | NOT_FOUND | No installation media |
| Recovery images | NOT_FOUND | No backup images |
| Deployment scripts | NOT_FOUND | No provisioning scripts |

---

## Classification

**ARTIFACT_INVENTORY**: `NO_DEPLOYMENT_ARTIFACTS_FOUND`

The operator-owned content contains:
- Game executables (AcrGame.exe, AcrGame-Win64-Shipping.exe)
- NesysService.exe (in D drive backup)
- Game configuration files
- Save data and ranking data
- OpenKey files
- Test mode configurations
- CmdFile update system logs

The operator-owned content does NOT contain:
- Installer packages
- Deployment scripts
- Recovery images
- Service registration artifacts
- Certificate files
- Registry configuration
- Startup shortcuts
- Scheduled tasks
- Any deployment-related artifacts

---

## G15 Audit Notes

This document was created in Phase 2A-G15 to provide a complete deployment artifact inventory. No deployment artifacts were found in the operator-owned content. The search covered all file extensions and filename keywords specified in the workstream requirements.
