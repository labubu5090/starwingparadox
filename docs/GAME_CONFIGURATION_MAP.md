# Game Configuration Map

## 1. Configuration Files Overview

| File | Location | Size | Purpose |
|------|----------|------|---------|
| `DefaultInput.ini` | `WindowsNoEditor\AcrGame\Config\` | 8.3KB | Input mappings (UE4) |
| `DefaultEngine.ini` | `WindowsNoEditor\AcrGame\Config\` | 6.6KB | Engine configuration |
| `GameUserSettings.ini` | `D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Config\WindowsNoEditor\` | 1KB | Display/render settings |
| `GameUserSettingsDefault.ini` | `WindowsNoEditor\AcrGame\Config\` | 891B | Default display settings |
| `GameUserSettings2on2.ini` | `WindowsNoEditor\AcrGame\Config\` | 1KB | 2v2 mode display settings |
| `Engine.ini` | `D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Config\WindowsNoEditor\` | 239B | Runtime engine config |
| `test_mode_setting.json` | `D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Setting\` | 26.5KB | Test mode settings (YAML) |
| `StickData.json` | `D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Stick\` | 352B | Joystick calibration |
| `Game.json` | `D DRIVE CONTENTS\Saved\ACRSaved\TestMode\Game\` | 220B | Game mode settings |
| `SaveData.json` | `D DRIVE CONTENTS\Saved\ACRSaved\SaveData\` | 18KB | Player save data |
| `OpenKey.json` | `D DRIVE CONTENTS\Saved\ACRSaved\SaveData\` | 74B | Open key/version |
| `OpenKeyEvent_Galaxy.json` | `D DRIVE CONTENTS\system\DUA\event\` | 74B | Open key event |
| `tm_main.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 12.5KB | Test mode main menu |
| `tm_device.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 13.7KB | Test mode device |
| `tm_network.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 6.9KB | Test mode network |
| `tm_seat.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 12.7KB | Test mode seat |
| `tm_stick_vibration.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 3.4KB | Test mode vibration |
| `tm_switch.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 2.7KB | Test mode switch |
| `tm_touch_panel.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 742B | Test mode touch |
| `tm_nesica.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 2.4KB | Test mode NESiCA |
| `tm_version.json` | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` | 3.2KB | Test mode version |

## 2. Key Configuration Values

### Network Settings (`test_mode_setting.json`)

| Key | Value |
|-----|-------|
| GameServerIP | 127.0.0.1 |
| GameServerPort | 4001 |
| NesysServerIP | 127.0.0.1 |
| NesysServerPort | 6666 |
| WebAPIIP | 127.0.0.1 |
| WebAPIPort | 4000 |
| GameServerRetry | true |

### Display Settings (`GameUserSettings.ini`)

| Key | Value |
|-----|-------|
| ResolutionSizeX | 1920 |
| ResolutionSizeY | 1080 |
| FullscreenMode | 2 (Windowed) |
| FrameRateLimit | 0 (unlimited) |
| AudioQualityLevel | 0 |
| bUseVSync | False |

### Game Settings (`Game.json`)

| Key | Value |
|-----|-------|
| GameEnableTournament | 0 |
| GameEnableEvent | 0 |
| GameEnableMaseter | 0 |
| GameCodeSetting | 0 |
| GameMatchingNum | 0 |
| GameTeamSetting | 0 |
| GameSeatSetting | 1 |
| GameStageID | 0 |

### Save Data Structure (`SaveData.json`)

| Key | Type | Description |
|-----|------|-------------|
| MasterDataVersion | int | 109 |
| MasterDataFile | string[] | CSV data files |
| nesysId | string | NESYS system ID |
| OpenKey | string | Key version |
| PlayerProfile | object | Player data (8 fields) |
| GameData | object | Game progress |
| MissionData | object | Mission progress |
| PlayerStatus | object | Status flags |

## 3. Open Key System

From `OpenKey.json`:
```json
{
  "IsOpen": 1,
  "OpenVersion": 56299,
  "OpenDate": "2018/11/21",
  "OpenTime": "08:00:00"
}
```

This controls when the game is "open" for online play.

## 4. Configuration Sources

1. **Shipped configs** — `WindowsNoEditor\AcrGame\Config\*`
2. **Runtime configs** — `D DRIVE CONTENTS\Saved\*`
3. **Test mode configs** — `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\*`
4. **System configs** — `D DRIVE CONTENTS\system\*`
