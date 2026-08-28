# Original Runtime Artifact Inventory

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Summary

The operator-owned Starwing Paradox content on X:\StarwingParadox contains game files and a D-drive backup, but does NOT contain the original launcher, startup scripts, or system-drive components.

---

## Executables Found

| Executable | Path | Size | SHA-256 | Classification |
|------------|------|------|---------|----------------|
| AcrGame.exe | WindowsNoEditor\AcrGame.exe | 161,280 | `97800621...` | GAME_EXECUTABLE |
| AcrGame-Win64-Shipping.exe | WindowsNoEditor\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe | 163,119,104 | `CE4C8905...` | GAME_EXECUTABLE |
| NesysService.exe | D DRIVE CONTENTS\system\Service\NesysService.exe | 548,352 | `3A968F29...` | SUPPORT_SERVICE |

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
| .ps1 | 0 | NONE |

**No script files found.**

---

## Configuration Files Found

| Type | Count | Key Files |
|------|-------|-----------|
| .ini | 52 | GameUserSettings.ini, Engine.ini, Game.ini, NoHDDUnload.ini |
| .xml | 2 | PluginInfo.xml, SoundbanksInfo.xml |
| .json | 60+ | OpenKey.json, SaveData.json, RankingData.json, test mode configs |
| .log | 1 | CmdFile\log\Log.txt (40,728 lines - update/command log) |
| .txt | 2 | option.txt, CookedIniVersion.txt |
| .cfg | 0 | NONE |
| .manifest | 0 | NONE |

---

## Key Runtime Files

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
| NoHDDUnload.ini | NoHDDUnload.ini | 2 | WriteFileInterval=50000 |
| update.log | D DRIVE CONTENTS\system\update.log | 0 | Empty |

---

## NesysService Directory

| File | Path | Size |
|------|------|------|
| NesysService.exe | D DRIVE CONTENTS\system\Service\NesysService.exe | 548,352 |

**No other files in Service directory.** No DLLs, no config files, no certificates.

---

## CmdFile System

| Directory | Contents |
|-----------|----------|
| D DRIVE CONTENTS\system\CmdFile\log\ | Log.txt (40,728 lines) - update/command operations |
| D DRIVE CONTENTS\system\DUA\data\ | Empty |
| D DRIVE CONTENTS\system\DUA\decrypt\ | Empty |
| D DRIVE CONTENTS\system\DUA\download\ | Empty |
| D DRIVE CONTENTS\system\DUA\event\ | OpenKeyEvent_Galaxy.json + news images |
| D DRIVE CONTENTS\system\DUA\news\ | 3 news PNG images |
| D DRIVE CONTENTS\system\DUA\unpack\ | Empty |
| D DRIVE CONTENTS\system\DUA\work\ | Empty |

---

## GalaxySaved Directory

| Directory | Contents |
|-----------|----------|
| D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Config\ | GameUserSettings.ini, Engine.ini, etc. |
| D DRIVE CONTENTS\Saved\GalaxySaved\UnrealEngine\4.16\Saved\Config\ | Manifest.ini |

---

## TestMode Directory

| File | Path |
|------|------|
| Game.json | D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Game\Game.json |
| NesicaTime.json | D DRIVE CONTENTS\Saved\ACRSaved\TestMode\NesicaTime\NesicaTime.json |
| OnePlayFree.json | D DRIVE CONTENTS\Saved\ACRSaved\TestMode\OnePlayFree\OnePlayFree.json |
| Setting\test_mode_setting.json | D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Setting\test_mode_setting.json |
| Sound.json | D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Sound\Sound.json |
| StickData.json | D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Stick\StickData.json |
| System.json | D DRIVE CONTENTS\Saved\ACRSaved\TestMode\System\System.json |
| BookKeeping\*.json | 23 bookkeeping files |

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

---

## Classification

**ARTIFACT_INVENTORY**: D_DRIVE_ONLY_BACKUP

The operator-owned content contains:
- Game executables (AcrGame.exe, AcrGame-Win64-Shipping.exe)
- NesysService.exe (in D drive backup)
- Game configuration files
- Save data and ranking data
- OpenKey files
- Test mode configurations
- CmdFile update system logs

The operator-owned content does NOT contain:
- Original launcher
- Startup scripts
- Certificate files
- Registry configuration
- System-drive components
- Windows Service configuration
- Scheduled tasks
