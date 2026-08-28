# typex Provisioning Evidence

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

No evidence of typex registry provisioning was found in the operator-owned content. No artifacts contain explicit definitions for HKLM\SOFTWARE\taito\typex values. The registry values remain UNKNOWN.

---

## Registry Values Investigated

### Known Values (from G13/G14)

| Value | Type | Classification |
|-------|------|----------------|
| GameKind | REG_DWORD | INSTALLATION_IDENTITY |
| EventNextTime | REG_DWORD | RUNTIME_STATE |
| ConditionTime | REG_DWORD | RUNTIME_STATE |
| TrafficCount | REG_DWORD | RUNTIME_STATE |
| LogLevel | REG_DWORD | LOGGING_CONFIGURATION |
| NewsPath | REG_SZ | FILE_PATH |
| EventPath | REG_SZ | FILE_PATH |
| LogPath | REG_SZ | FILE_PATH |

---

## Artifact Search Results

### Configuration Files

| File | Path | typex References | Provisioning Evidence |
|------|------|------------------|----------------------|
| DefaultEngine.ini | WindowsNoEditor\AcrGame\Config\ | NONE | NONE |
| DefaultGame.ini | WindowsNoEditor\AcrGame\Config\ | NONE | NONE |
| DefaultInput.ini | WindowsNoEditor\AcrGame\Config\ | NONE | NONE |
| GameUserSettings.ini | D DRIVE CONTENTS\Saved\GalaxySaved\ | NONE | NONE |
| Engine.ini | D DRIVE CONTENTS\Saved\GalaxySaved\ | NONE | NONE |
| option.txt | D DRIVE CONTENTS\system\option.txt | NONE | NONE |

**No typex references found in configuration files.**

### Data Files

| File | Path | typex References | Provisioning Evidence |
|------|------|------------------|----------------------|
| OpenKey.json | D DRIVE CONTENTS\Saved\ACRSaved\SaveData\ | NONE | NONE |
| SaveData.json | D DRIVE CONTENTS\Saved\ACRSaved\SaveData\ | NONE | NONE |
| RankingData.json | D DRIVE CONTENTS\Saved\ACRSaved\Ranking\ | NONE | NONE |

**No typex references found in data files.**

### Log Files

| File | Path | typex References | Provisioning Evidence |
|------|------|------------------|----------------------|
| Log.txt | D DRIVE CONTENTS\system\CmdFile\log\Log.txt | NONE | NONE |
| update.log | D DRIVE CONTENTS\system\update.log | NONE | NONE |

**No typex references found in log files.**

### Scripts

| File | Path | typex References | Provisioning Evidence |
|------|------|------------------|----------------------|
| *.ps1 | archive\postgresql\tools\ | NONE | NONE |

**No typex references found in scripts.**

---

## Registry Value Status

### GameKind

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | INSTALLATION_IDENTITY | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

### EventNextTime

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | RUNTIME_STATE | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

### ConditionTime

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | RUNTIME_STATE | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

### TrafficCount

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | RUNTIME_STATE | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

### LogLevel

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | LOGGING_CONFIGURATION | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

### NewsPath

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | FILE_PATH | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

### EventPath

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | FILE_PATH | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

### LogPath

| Property | Status | Evidence |
|----------|--------|----------|
| Source artifact | NOT_FOUND | No artifact defines value |
| Declared data type | NOT_FOUND | No artifact defines type |
| Declared value | NOT_FOUND | No artifact defines value |
| Classification | FILE_PATH | From G14 |
| Cabinet-specific | UNKNOWN | No evidence |
| Confidence | NOT_FOUND | No evidence |

---

## Classification

**TYPEX_PROVISIONING_EVIDENCE**: `NOT_FOUND`

**Rationale**:
- No artifacts contain typex registry references
- No configuration files define registry values
- No scripts define registry values
- No logs contain registry provisioning evidence
- Registry values remain UNKNOWN

---

## Conclusion

No evidence of typex registry provisioning was found in the operator-owned content. No artifacts contain explicit definitions for HKLM\SOFTWARE\taito\typex values. The registry values remain UNKNOWN.

**Classification**: `NO_TYPEX_PROVISIONING_EVIDENCE`

The operator-owned content does not contain any registry provisioning data for HKLM\SOFTWARE\taito\typex.

---

## G15 Audit Notes

This document was created in Phase 2A-G15 to identify typex provisioning evidence. No evidence was found. The registry values remain UNKNOWN.
