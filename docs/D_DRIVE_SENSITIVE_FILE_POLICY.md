# D: Drive Sensitive File Policy

## Date: 2026-08-27

## Sensitive Files

### OpenKey.json
- **Location**: `D:\Saved\ACRSaved\SaveData\OpenKey.json`
- **Contents**: `{ "IsOpen": 1, "OpenVersion": 56299, "OpenDate": "2018/11/21", "OpenTime": "08:00:00" }`
- **Classification**: Sensitive (contains game state data)

#### Policy
- **Copy**: Only as part of operator-owned local runtime reconstruction
- **Print**: NEVER — values are never displayed in logs or output
- **Parse for secrets**: NEVER
- **Commit**: NEVER — excluded from git via .gitignore
- **Modify**: NEVER — copied exactly as-is from source
- **Replace**: NEVER
- **Regenerate**: NEVER
- **Transmit**: NEVER
- **Hash**: SHA-256 recorded for integrity verification only
- **Log content**: NEVER — only metadata logged (size, hash)
- **Protection**: `.gitignore` entry prevents accidental inclusion

### SaveData.json
- **Classification**: Game data (contains master data version and file list)
- **Policy**: Copied as-is, not committed, not modified

### RankingData.json
- **Classification**: Game data (ranking information)
- **Policy**: Copied as-is, not committed, not modified

### test_mode_setting.json
- **Classification**: Configuration data
- **Policy**: Copied as-is, not committed, not modified

### BookKeeping*.json
- **Classification**: Historical operational data
- **Policy**: Copied as-is, not committed, not modified

## Git Exclusions

The following patterns must be in `.gitignore`:
```
data/*.vhdx
data/starwing-test-d*
```

OpenKey.json content is NEVER committed regardless of location.

## Verification

Before any commit, verify:
1. No OpenKey.json values appear in git diff
2. No VHDX files are staged
3. No D: drive runtime data is committed
4. Only tooling, documentation, and tests are committed
