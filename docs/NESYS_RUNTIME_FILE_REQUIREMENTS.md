# NESYS Runtime File Requirements

## File Lookups Observed

| Process | Path | Operation | Result | Found |
|---------|------|-----------|--------|-------|
| Shipping | D:/Saved/ACRSaved/SaveData/OpenKey.json | LoadJsonFile | LoadKeyFile error | NO |
| Shipping | D:/Saved/ACRSaved/Debug/DebugSetting.json | LoadJsonFile | Load error | NO |
| Shipping | D:/Saved/ACRSaved/Ranking/RankingData.json | LoadClient | LoadFileToString error | NO |
| Shipping | D:/Saved/ACRSaved/SendLog | CreateDirectory | Create error | NO |
| Shipping | D:/Saved/ACRSaved/TestMode/BookKeeping/Old | CreateDirectory | Create error | NO |

## D: Drive Paths Required

All D: drive paths are under `D:/Saved/ACRSaved/`:
- `SaveData/OpenKey.json` — NESYS key data
- `SaveData/SaveData.json` — Save data
- `Debug/DebugSetting.json` — Debug settings
- `Ranking/RankingData.json` — Ranking data
- `SendLog/` — Log upload directory
- `TestMode/BookKeeping/Old/` — Test mode data

## OpenKey Sequence

1. `CheckOpenKeyLoad` — Attempts to load OpenKey.json from D:
2. `LoadKeyFile error` — File not found
3. `CheckOpenKeyUpdate` — Attempts NESYS event check
4. `NESYS Event error` — Event check fails (IsEventCheck[0] IsEventError[0])

## Missing Runtime Files

- `D:/Saved/ACRSaved/SaveData/OpenKey.json` — Required for NESYS authentication
- `D:/Saved/ACRSaved/Debug/DebugSetting.json` — Optional debug config
- `D:/Saved/ACRSaved/Ranking/RankingData.json` — Optional ranking data

## AppData Files

13 files created under `AppData\Local\AcrGame\Saved\`:
- Config files (Engine.ini, GameUserSettings.ini)
- Logs (AcrGame.log)
- Save slot data
- Runtime configs

## Conclusion

The game requires D: drive for OpenKey.json and save data. Without D:, these operations fail but the game still boots to the title screen.
