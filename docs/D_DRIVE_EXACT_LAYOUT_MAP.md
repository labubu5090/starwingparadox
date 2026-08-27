# D Drive Exact Layout Map

## Date: 2026-08-27

## Evidence-Based Target Paths

The game binary hardcodes paths using `D:/` prefix. The exact target paths are proven by:

1. **Game log evidence**: `D:/Saved/ACRSaved/SaveData/OpenKey.json`, `D:/Saved/ACRSaved/SaveData/SaveData.json`
2. **DefaultGame.ini**: `D:\\system\\DUA\\event\\system_management_200123_byking_ver01.json`
3. **D DRIVE CONTENTS**: Source directory structure

## Source → Target Mapping

| Source Path | Target Path | Files | Size |
|-------------|-------------|-------|------|
| `D DRIVE CONTENTS\Saved\ACRSaved\SaveData\` | `D:\Saved\ACRSaved\SaveData\` | 163 | 3.0 MB |
| `D DRIVE CONTENTS\Saved\ACRSaved\Ranking\` | `D:\Saved\ACRSaved\Ranking\` | 1 | 66 KB |
| `D DRIVE CONTENTS\Saved\ACRSaved\TestMode\` | `D:\Saved\ACRSaved\TestMode\` | 15 | 254 KB |
| `D DRIVE CONTENTS\Saved\GalaxySaved\` | `D:\Saved\GalaxySaved\` | 12 | 2 KB |
| `D DRIVE CONTENTS\system\` | `D:\system\` | 7 | 1.8 MB |
| **Total** | | **217** | **7.9 MB** |

## Directory Structure

```
D:\
├── Saved\
│   ├── ACRSaved\
│   │   ├── SaveData\        (163 files - game data CSVs, OpenKey.json, SaveData.json)
│   │   ├── Ranking\         (1 file - RankingData.json)
│   │   ├── SendLog\         (empty)
│   │   └── TestMode\        (15 files - test mode configs)
│   └── GalaxySaved\         (12 files - UE4 configs, crash reports)
└── system\
    ├── option.txt           (44 bytes)
    ├── update.log           (0 bytes)
    ├── CmdFile\log\         (1 file - Log.txt 1.7MB)
    ├── DUA\                 (8 files - event/news data)
    └── Service\             (1 file - NesysService.exe 535 KB)
```

## Key Files

| File | Target | Purpose | NESYS Relevant |
|------|--------|---------|----------------|
| OpenKey.json | `D:\Saved\ACRSaved\SaveData\OpenKey.json` | Game open state | Yes (read by game) |
| SaveData.json | `D:\Saved\ACRSaved\SaveData\SaveData.json` | Master data manifest | Yes (read by game) |
| RankingData.json | `D:\Saved\ACRSaved\Ranking\RankingData.json` | Ranking data | No |
| test_mode_setting.json | `D:\Saved\ACRSaved\TestMode\Setting\test_mode_setting.json` | Test mode settings | No |
| NesysService.exe | `D:\system\Service\NesysService.exe` | NESYS service | **Yes** |
| option.txt | `D:\system\option.txt` | System options | Possibly |

## Writable at Runtime

| Directory | Writable | Evidence |
|-----------|----------|----------|
| `D:\Saved\ACRSaved\SaveData\` | Yes | Game writes OpenKey.json |
| `D:\Saved\ACRSaved\SendLog\` | Yes | Game creates log files |
| `D:\Saved\ACRSaved\Debug\` | Yes | Game writes DebugSetting.json |
| `D:\system\DUA\` | Yes | Service downloads data |
| `D:\system\DUA\event\` | Yes | Service updates events |

## Missing from Source

| Expected File | Status | Impact |
|---------------|--------|--------|
| `D:\Saved\ACRSaved\Debug\DebugSetting.json` | Missing | Load error in game log (non-blocking) |
| `D:\system\DUA\event\system_management_200123_byking_ver01.json` | Missing | Referenced in config (non-blocking) |
