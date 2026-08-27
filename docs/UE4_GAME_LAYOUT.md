# UE4 Game Layout

## 1. Project Structure

| Item | Value |
|------|-------|
| Project Name | AcrGame |
| Engine Version | 4.16 |
| Platform | Win64 |
| Build Configuration | Shipping |
| Main Executable | `AcrGame-Win64-Shipping.exe` (163MB) |
| Launcher Executable | `AcrGame.exe` (161KB) |

## 2. Directory Layout

```
X:\StarwingParadox\WindowsNoEditor\
├── AcrGame\
│   ├── Binaries\Win64\          # Game executables
│   ├── Config\                   # Game configuration (INI)
│   │   ├── DefaultInput.ini      # Input mappings
│   │   ├── DefaultEngine.ini     # Engine config
│   │   ├── GameUserSettings.ini  # Display/render settings
│   │   └── *.ini                 # Other configs
│   └── Content\                  # Game content (cooked)
│       ├── TestMode\             # Test mode UI content
│       │   └── SettingFile\      # Test mode config files
│       └── *.uasset              # Cooked UE4 assets
├── Engine\                       # Engine content
│   ├── Binaries\Win64\           # Engine DLLs
│   ├── Content\                  # Engine content
│   └── Config\                   # Engine config
├── Redist\                       # Redistributables
└── AcrGame-Win64-Shipping.exe    # Main binary
```

## 3. Cooked Content Structure

```
WindowsNoEditor\
├── AcrGame\Content\
│   ├── TestMode\SettingFile\     # Test mode JSON configs
│   │   ├── tm_main.json          # Main menu
│   │   ├── tm_device.json        # Device test
│   │   ├── tm_stick_vibration.json # Stick vibration
│   │   ├── tm_network.json       # Network settings
│   │   ├── tm_seat.json          # Seat test
│   │   ├── tm_switch.json        # Switch test
│   │   ├── tm_touch_panel.json   # Touch panel
│   │   ├── tm_nesica.json        # NESiCA card test
│   │   └── tm_version.json       # Version info
│   └── *.uasset                  # Cooked game assets
├── Engine\Content\               # Engine content
└── *.pak                         # Pak files (packed content)
```

## 4. Pak Files

| File | Size |
|------|------|
| gamecontent.pak | 26.2 GB |
| 4 smaller paks | ~1GB total |

## 5. UE4 Plugins

From `SavedEngine.ini`:
- `NesysClient/Content` — NESYS card client
- `TestMode/Content` — Test mode system
- `Wwise/Content` — Audio middleware
- `Paper2D/Content` — 2D rendering (used for UI)
- `TrueSkyPlugin/Content` — Sky rendering

## 6. Configuration Hierarchy

```
DefaultInput.ini         # Base input config (shipped with game)
  └── User overrides    # Runtime overrides (test mode)
      └── GameUserSettings.ini  # Display settings
```
