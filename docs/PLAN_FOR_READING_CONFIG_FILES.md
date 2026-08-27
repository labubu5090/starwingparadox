# Plan for Reading Configuration Files

## 1. Objective

Read and analyze all configuration files in the game content to understand:
- Network configuration
- Input mapping
- Display settings
- Game mode settings
- Test mode configuration

## 2. Configuration File Locations

| Category | Location |
|----------|----------|
| UE4 Engine Config | `WindowsNoEditor\Engine\Config\` |
| UE4 Game Config | `WindowsNoEditor\AcrGame\Config\` |
| Runtime Config | `D DRIVE CONTENTS\Saved\` |
| Test Mode Config | `WindowsNoEditor\AcrGame\Content\TestMode\SettingFile\` |
| System Config | `D DRIVE CONTENTS\system\` |

## 3. Key Files to Read

### Network Configuration
| File | Purpose |
|------|---------|
| `test_mode_setting.json` | Network server addresses |
| `tm_network.json` | Test mode network settings |
| `NesysNet.dll` | Network library |

### Input Configuration
| File | Purpose |
|------|---------|
| `DefaultInput.ini` | UE4 input mappings |
| `tm_switch.json` | Switch test config |
| `tm_device.json` | Device test config |
| `StickData.json` | Joystick calibration |

### Display Configuration
| File | Purpose |
|------|---------|
| `GameUserSettings.ini` | Display settings |
| `GameUserSettingsDefault.ini` | Default display |
| `GameUserSettings2on2.ini` | 2v2 mode display |

### Game Configuration
| File | Purpose |
|------|---------|
| `Game.json` | Game mode settings |
| `SaveData.json` | Player save structure |
| `OpenKey.json` | Open key/version |
| `tm_main.json` | Test mode main menu |
| `tm_version.json` | Version info |

## 4. Reading Strategy

| Step | Action | Tool |
|------|--------|------|
| 1 | Read all INI files | `Read` tool |
| 2 | Read all JSON files | `Read` tool |
| 3 | Parse YAML content | Custom script |
| 4 | Extract key values | Analysis script |
| 5 | Document findings | Markdown files |

## 5. Output

| Output | Location |
|--------|----------|
| Config contents | `docs/generated/game_configs_content.json` |
| Config analysis | `docs/GAME_CONFIGURATION_MAP.md` |
| Network analysis | `docs/GAME_NETWORK_ENDPOINT_MAP.md` |
| Input analysis | `docs/GAME_INPUT_IO_AUDIT.md` |
