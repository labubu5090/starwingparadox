# Original Startup Sequence

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: NOT_DOCUMENTED  

---

## Summary

No startup sequence artifacts were found in the operator-owned content. The original startup sequence is unknown.

---

## Shortcut Analysis

### .lnk Files Found

| Count | Result |
|-------|--------|
| Total .lnk files | 0 |

**No shortcuts found.** No startup folder placement evidence.

---

## Startup Artifacts Search

| Artifact Type | Count | Notes |
|---------------|-------|-------|
| .lnk files | 0 | No shortcuts |
| .bat files | 0 | No batch files |
| .cmd files | 0 | No command files |
| .vbs files | 0 | No VBScript files |
| .ps1 files | 0 | No PowerShell scripts |
| .reg files | 0 | No registry imports |
| .manifest files | 0 | No application manifests |

---

## Windows Service Evidence

| Evidence | Status |
|----------|--------|
| Service wrapper | NOT_FOUND |
| Service installation script | NOT_FOUND |
| Service configuration | NOT_FOUND |

---

## Scheduled Task Evidence

| Evidence | Status |
|----------|--------|
| Task definitions | NOT_FOUND |
| Task scheduler entries | NOT_FOUND |

---

## Registry Evidence

| Evidence | Status |
|----------|--------|
| Run/RunOnce keys | NOT_FOUND |
| Service registry entries | NOT_FOUND |
| Application registration | NOT_FOUND |

---

## Shell Replacement Evidence

| Evidence | Status |
|----------|--------|
| Cabinet shell | NOT_FOUND |
| Auto-login startup | NOT_FOUND |
| Shell replacement | NOT_FOUND |

---

## Galaxy Startup Evidence

| Evidence | Status |
|----------|--------|
| Galaxy client startup | NOT_FOUND |
| Galaxy integration | NOT_FOUND |

---

## Watchdog Startup Evidence

| Evidence | Status |
|----------|--------|
| Watchdog configuration | NOT_FOUND |
| Watchdog startup | NOT_FOUND |

---

## CmdFile System

The only operational log found is the CmdFile system:

| File | Path | Content |
|------|------|---------|
| Log.txt | D DRIVE CONTENTS\system\CmdFile\log\Log.txt | 40,728 lines of update/command operations |

The CmdFile system appears to be an update/content management system that:
- Performs update checks (`Do update Check`)
- Performs command checks (`Do Command Check`)
- Creates directories (`MKDIR`)
- Copies files (`ZIPCOPY`)
- Handles network errors (`Network Function ERROR`)

**No NesysService references found in CmdFile logs.**

---

## option.txt

| File | Path | Content |
|------|------|---------|
| option.txt | D DRIVE CONTENTS\system\option.txt | `[Option]\nScreenType=0\nEWF=1\nMemoryLog=0` |

**EWF=1** suggests Enhanced Write Filter is enabled (common in embedded/arcade systems).

---

## NoHDDUnload.ini

| File | Path | Content |
|------|------|---------|
| NoHDDUnload.ini | NoHDDUnload.ini | `[init]\nWriteFileInterval=50000` |

This suggests a write-back cache mechanism with 50-second intervals.

---

## Inferred Startup Sequence (NOT CONFIRMED)

Based on evidence, the likely startup sequence was:

1. **Windows boots** → EWF (Enhanced Write Filter) active
2. **CmdFile system starts** → Performs update/command checks
3. **NesysService.exe starts** → Registers as Windows Service
4. **AcrGame.exe launches** → Standard UE4 game executable
5. **AcrGame-Win64-Shipping.exe runs** → Main game binary

**This sequence is NOT confirmed.** It is inferred from:
- EWF presence (embedded system)
- NesysService Windows Service APIs
- AcrGame.exe as standard UE4 launcher

---

## Classification

**STARTUP_SEQUENCE**: NOT_DOCUMENTED

**Rationale**:
- No .lnk shortcuts found
- No .bat/.cmd scripts found
- No startup folder placement
- No scheduled tasks
- No registry entries
- No shell replacement
- No watchdog configuration
- No Galaxy startup
- Only CmdFile update log found

**Conclusion**: The original startup sequence is unknown. The operator-owned content does not contain the startup configuration.
