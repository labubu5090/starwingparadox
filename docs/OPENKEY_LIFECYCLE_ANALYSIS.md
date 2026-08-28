# OpenKey Lifecycle Analysis

**Date:** 2026-08-28

## Component Behavior Summary

| Component | Read | Write | Create | Update | Delete | Validate | Unknown |
|-----------|------|-------|--------|--------|--------|----------|---------|
| AcrGame-Win64-Shipping.exe | ✓ | — | — | — | — | — | — |
| NesysService.exe | — | — | — | — | — | — | ✓ |
| populate-starwing-test-vhd.ps1 | — | — | ✓ (copy) | — | — | — | — |
| verify-starwing-test-vhd.ps1 | ✓ (check) | — | — | — | — | — | — |

## Evidence Analysis

### AcrGame-Win64-Shipping.exe (READ)

**Evidence:**
- Game log line 8448: `LoadJsonFile / path[D:/Saved/ACRSaved/SaveData/OpenKey.json]`
- Game log line 108153: `LoadJsonFile / path[D:/Saved/ACRSaved/SaveData/OpenKey.json]`
- Game log line 108155: `CheckOpenKey / LoadKeyFile error.`

**Classification:** EXPLICIT_READ
**Strength:** STRONG — direct runtime evidence from game log
**Behavior:** Game attempts to read OpenKey.json at boot and during SystemDataCheck. File not found → error.

### NesysService.exe (UNKNOWN)

**Evidence:**
- Binary contains `FindFirstFileA` (file enumeration, not creation)
- Binary contains `GetModuleFileNameA` (self-path, not OpenKey)
- Binary contains `RegOpenKeyExA`, `RegQueryValueExA` (registry, not file)
- No `CreateFileA` or `WriteFile` evidence for OpenKey path
- NesysService exits immediately (code -1) before any file access

**Classification:** PRODUCER_UNKNOWN
**Strength:** WEAK — binary analysis shows file operations but no direct OpenKey creation evidence
**Behavior:** Cannot determine if NesysService creates or reads OpenKey. Exits before access.

### D DRIVE CONTENTS (STATIC SOURCE)

**Evidence:**
- File exists at `X:\StarwingParadox\D DRIVE CONTENTS\Saved\ACRSaved\SaveData\OpenKey.json`
- 96 bytes, SHA-256: `B166054FD8CFAC828A9BF72F97663A311F7C5B9A4A23AEE3189B959241D64AE2`
- Last-write time: 2018-11-21 (original game content date)

**Classification:** OPERATOR_OWNED_RUNTIME_SOURCE
**Strength:** STRONG — file exists in authorized game content
**Behavior:** Static file, part of game deployment package.

### populate-starwing-test-vhd.ps1 (CREATE/COPY)

**Evidence:**
- Script copies OpenKey.json from D DRIVE CONTENTS to VHD
- Line 86: `"D:\Saved\ACRSaved\SaveData\OpenKey.json"`

**Classification:** EXPLICIT_CREATE (copy operation)
**Strength:** STRONG — script evidence
**Behavior:** Copies OpenKey.json to D: drive during VHD population.

## Lifecycle Sequence (Inferred)

```
1. Factory/Deployment
   → OpenKey.json created by unknown process
   → Included in game deployment package (D DRIVE CONTENTS)

2. Cabinet Setup
   → populate-starwing-test-vhd.ps1 copies to D: drive
   → File available at D:\Saved\ACRSaved\SaveData\OpenKey.json

3. Game Boot
   → AcrGame-Win64-Shipping.exe attempts LoadJsonFile
   → File not found (D: not mounted or file missing)
   → LoadKeyFile error

4. SystemDataCheck
   → CheckOpenKeyLoad attempts LoadJsonFile
   → File not found → error
   → CheckOpenKeyUpdate attempts NESYS event check
   → NESYS Event error (NESYS offline)
   → DispError displayed
```

## Unknown Behaviors

| Question | Status |
|----------|--------|
| Who creates OpenKey.json originally? | UNKNOWN |
| Does NesysService read OpenKey.json? | UNKNOWN |
| Does NesysService update OpenKey.json? | UNKNOWN |
| Does game write OpenKey.json at runtime? | UNKNOWN |
| Is OpenKey.json required for NESYS online? | UNKNOWN |
| Does OpenKey.json contain authentication material? | UNKNOWN_AND_SENSITIVE |

## Conclusion

OPENKEY_LIFECYCLE: READ_BY_GAME_ONLY_WITH_UNKNOWN_PRODUCER
