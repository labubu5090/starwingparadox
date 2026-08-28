# NesysService File-Path Dependencies

**Phase**: 2A-G14  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe reads file paths from registry values (NewsPath, EventPath, LogPath). Candidate directories were found in the D-drive backup, but filename similarity alone is not confirmation. The exact file/directory requirements are NOT_SHOWN in static analysis.

---

## File-Path Registry Values

### NewsPath

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Registry value | NewsPath | CONFIRMED | String reference |
| Type | REG_SZ | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Expected type | File or directory | INFERRED | Path reference |
| Filename pattern | NOT_SHOWN | NOT_FOUND | No pattern in code |
| Startup criticality | NOT_SHOWN | NOT_FOUND | No criticality check |
| Directory creation | NOT_SHOWN | NOT_FOUND | No creation logic |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Access mode | NOT_SHOWN | NOT_FOUND | No access mode |
| Account permissions | NOT_SHOWN | NOT_FOUND | No permission check |

### EventPath

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Registry value | EventPath | CONFIRMED | String reference |
| Type | REG_SZ | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Expected type | File or directory | INFERRED | Path reference |
| Filename pattern | NOT_SHOWN | NOT_FOUND | No pattern in code |
| Startup criticality | NOT_SHOWN | NOT_FOUND | No criticality check |
| Directory creation | NOT_SHOWN | NOT_FOUND | No creation logic |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Access mode | NOT_SHOWN | NOT_FOUND | No access mode |
| Account permissions | NOT_SHOWN | NOT_FOUND | No permission check |

### LogPath

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Registry value | LogPath | CONFIRMED | String reference |
| Type | REG_SZ | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Expected type | File or directory | INFERRED | Path reference |
| Filename pattern | NOT_SHOWN | NOT_FOUND | No pattern in code |
| Startup criticality | NOT_SHOWN | NOT_FOUND | No criticality check |
| Directory creation | NOT_SHOWN | NOT_FOUND | No creation logic |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Access mode | NOT_SHOWN | NOT_FOUND | No access mode |
| Account permissions | NOT_SHOWN | NOT_FOUND | No permission check |

---

## D-Drive Candidate Directories

### NewsPath Candidates

| Candidate | Evidence | Confidence |
|-----------|----------|------------|
| `X:\StarwingParadox\D DRIVE CONTENTS\system\DUA\news` | Directory exists, contains news images | POSSIBLE |
| `X:\StarwingParadox\D DRIVE CONTENTS\system\DUA\news\*.png` | PNG files with timestamps | POSSIBLE |

**Confirmation**: `NOT_CONFIRMED` — Filename similarity alone is not confirmation.

### EventPath Candidates

| Candidate | Evidence | Confidence |
|-----------|----------|------------|
| `X:\StarwingParadox\D DRIVE CONTENTS\system\DUA\event` | Directory exists, contains event files | POSSIBLE |
| `X:\StarwingParadox\D DRIVE CONTENTS\system\DUA\event\OpenKeyEvent_Galaxy.json` | JSON event file | POSSIBLE |

**Confirmation**: `NOT_CONFIRMED` — Filename similarity alone is not confirmation.

### LogPath Candidates

| Candidate | Evidence | Confidence |
|-----------|----------|------------|
| `X:\StarwingParadox\D DRIVE CONTENTS\system\CmdFile\log` | Directory exists, contains log files | POSSIBLE |
| `X:\StarwingParadox\D DRIVE CONTENTS\system\CmdFile\log\Log.txt` | Log file present | POSSIBLE |
| `X:\StarwingParadox\D DRIVE CONTENTS\Saved\ACRSaved\SendLog` | Empty directory | POSSIBLE |
| `X:\StarwingParadox\D DRIVE CONTENTS\Saved\GalaxySaved\AcrGame\Saved\Logs` | Empty directory | POSSIBLE |

**Confirmation**: `NOT_CONFIRMED` — Filename similarity alone is not confirmation.

---

## File Types Found

### News Files

| File | Type | Size | Evidence |
|------|------|------|----------|
| `galaxy_news_2on2_20200930.jpg` | JPEG image | Unknown | String reference |
| `galaxy_news_gamewith_20201001.jpg` | JPEG image | Unknown | String reference |
| `galaxy_news_logo.jpg` | JPEG image | Unknown | String reference |
| `galaxy_small_gamewith_20201001.jpg` | JPEG image | Unknown | String reference |
| `1542263994.png` | PNG image | Unknown | Filename |
| `1542624440.png` | PNG image | Unknown | Filename |
| `1554282579.png` | PNG image | Unknown | Filename |

### Event Files

| File | Type | Size | Evidence |
|------|------|------|----------|
| `OpenKeyEvent_Galaxy.json` | JSON file | 80 bytes | String reference |

### Log Files

| File | Type | Size | Evidence |
|------|------|------|----------|
| `Log.txt` | Text file | Unknown | Filename |

---

## Startup Criticality

### Status

| Value | Criticality | Evidence |
|-------|-------------|----------|
| NewsPath | NOT_SHOWN | No criticality check |
| EventPath | NOT_SHOWN | No criticality check |
| LogPath | NOT_SHOWN | No criticality check |

**Startup Criticality**: `NOT_SHOWN`

---

## Directory Creation Behavior

### Status

| Value | Create Directory | Evidence |
|-------|------------------|----------|
| NewsPath | NOT_SHOWN | No creation logic |
| EventPath | NOT_SHOWN | No creation logic |
| LogPath | NOT_SHOWN | No creation logic |

**Directory Creation**: `NOT_SHOWN`

---

## Missing Path Behavior

### Status

| Value | Missing Behavior | Evidence |
|-------|------------------|----------|
| NewsPath | NOT_SHOWN | No fallback logic |
| EventPath | NOT_SHOWN | No fallback logic |
| LogPath | NOT_SHOWN | No fallback logic |

**Missing Path Behavior**: `NOT_SHOWN`

---

## Access Mode

### Status

| Value | Access Mode | Evidence |
|-------|-------------|----------|
| NewsPath | NOT_SHOWN | No access mode |
| EventPath | NOT_SHOWN | No access mode |
| LogPath | NOT_SHOWN | No access mode |

**Access Mode**: `NOT_SHOWN`

---

## Account Permissions

### Status

| Value | Required Permissions | Evidence |
|-------|---------------------|----------|
| NewsPath | NOT_SHOWN | No permission check |
| EventPath | NOT_SHOWN | No permission check |
| LogPath | NOT_SHOWN | No permission check |

**Account Permissions**: `NOT_SHOWN`

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Registry value names | CONFIRMED |
| Registry value types | HIGH |
| Read operations | CONFIRMED |
| Candidate directories | POSSIBLE |
| File types | CONFIRMED |
| Startup criticality | NOT_SHOWN |
| Directory creation | NOT_SHOWN |
| Missing behavior | NOT_SHOWN |
| Access mode | NOT_SHOWN |
| Account permissions | NOT_SHOWN |

---

## Do NOT

| Action | Status |
|--------|--------|
| Modify candidate files | CONFIRMED NOT DONE |
| Treat filename similarity as confirmation | CONFIRMED NOT DONE |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact file or directory type | NOT_SHOWN | No type check in code |
| Filename patterns | NOT_SHOWN | No pattern in code |
| Startup criticality | NOT_SHOWN | No criticality check |
| Directory creation behavior | NOT_SHOWN | No creation logic |
| Missing path behavior | NOT_SHOWN | No fallback logic |
| Access mode | NOT_SHOWN | No access mode |
| Account permissions | NOT_SHOWN | No permission check |

---

## Conclusion

NesysService.exe reads file paths from registry values (NewsPath, EventPath, LogPath). Candidate directories were found in the D-drive backup, but filename similarity alone is not confirmation. The exact file/directory requirements are NOT_SHOWN in static analysis.

**Classification**: `CANDIDATE_DIRECTORIES_FOUND`

Candidate directories exist in the D-drive backup, but exact requirements are NOT_SHOWN.

---

## G14 Audit Notes

This document was created in Phase 2A-G14 to identify file-path dependencies. Candidate directories were found in the D-drive backup, but filename similarity alone is not confirmation. Exact requirements are NOT_SHOWN in static analysis.
