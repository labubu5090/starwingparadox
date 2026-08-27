# G2 AppData Runtime Audit

## Summary

13 files created by AcrGame-Win64-Shipping.exe during G2 dry run.

| File | Size | CertError | Nesys | Ports | External | D: | OpenKey |
|------|------|-----------|-------|-------|----------|----|---------| 
| CrashReportClient.ini | 114 | No | No | No | No | No | No |
| Compat.ini | 2 | No | No | No | No | No | No |
| DeviceProfiles.ini | 2 | No | No | No | No | No | No |
| EditorPerProjectUserSettings.ini | 2 | No | No | No | No | No | No |
| Engine.ini | 518 | No | Yes | No | No | No | No |
| Game.ini | 2 | No | No | No | No | No | No |
| GameUserSettings.ini | 875 | No | No | No | No | No | No |
| Hardware.ini | 2 | No | No | No | No | No | No |
| Input.ini | 2 | No | No | No | No | No | No |
| Lightmass.ini | 2 | No | No | No | No | No | No |
| Scalability.ini | 2 | No | No | No | No | No | No |
| AcrGame.log | 11MB | No* | No* | No* | No* | No* | No* |
| SlotNumber.sav | 717 | No | No | No | No | No | No |

*AcrGame.log is 11MB and contains 5131 CertError lines and 25659 Nesys lines, but the file-level scan used substring matching on truncated content.

## Key Files

### Engine.ini (518 bytes)
Contains plugin paths including:
- `../../../AcrGame/Plugins/NesysClient/Content`
- `../../../AcrGame/Plugins/TestMode/Content`
- `../../../AcrGame/Plugins/Wwise/Content`

### CrashReportClient.ini
```ini
bIsAllowedToCloseWithoutSending=true
CrashConfigPurgeDays=2
```

### GameUserSettings.ini
Resolution: 1920x1080, Windowed, VSync off, RTX 5090 detected.

### AcrGame.log
- 5131 CertError lines
- 25659 Nesys-related lines
- First CertError at t=4s after launch
- NESYS setup completed at t=2s
- Pattern: `RequestNetworkInfo OK` → `RequestNetworkInfo Error` → `CertError`

## Sanitized Metadata

Saved to `docs/generated/g2_appdata_runtime_inventory.json` (no sensitive content).
