# OpenKey Claim Correction

**Date:** 2026-08-28

## Purpose

Correct overreaching claims about OpenKey.json provenance and causality in prior documentation. All corrections are evidence-safe — no OpenKey data is created, modified, or exposed.

## Claims Requiring Correction

### Claim: "NesysService generates OpenKey.json"

**Status:** NOT_PROVEN
**Evidence:** No direct evidence that NesysService.exe creates OpenKey.json. The binary contains `FindFirstFileA` and `GetModuleFileNameA` but no explicit file-creation evidence for OpenKey. NesysService exits before it could access OpenKey.
**Correction:** OPENKEY_PRODUCER: UNKNOWN

### Claim: "Missing OpenKey is the confirmed root cause"

**Status:** OVERSTATED
**Evidence:** Game log shows `LoadKeyFile error` adjacent to `DispError`, but correlation is not causation. SystemDataCheck checks multiple conditions (IsOnline, OpenKey, NESYS Event).
**Correction:** OPENKEY_ROLE: REQUIRED_CANDIDATE (one of multiple SystemDataCheck requirements)

### Claim: "OpenKey is a certificate"

**Status:** INCORRECT
**Evidence:** GAME_CONFIGURATION_MAP.md shows OpenKey.json contains `{"IsOpen":1,"OpenVersion":56299,"OpenDate":"2018/11/21","OpenTime":"08:00:00"}`. This is game-state data, not a certificate.
**Correction:** OpenKey is a game-state file containing open/version/date fields, not a certificate.

### Claim: "OpenKey alone makes NESYS online"

**Status:** OVERSTATED
**Evidence:** NESYS offline is caused by named pipe connection failure (NesysService not running). OpenKey is checked by game-level SystemDataCheck, not by NESYS service.
**Correction:** NESYS online requires NesysService running + named pipe + certificates. OpenKey is a game-level dependency.

### Claim: "OpenKey can be reconstructed from known fields"

**Status:** UNSAFE
**Evidence:** The file exists in D DRIVE CONTENTS (96 bytes). Content is sensitive game-state data. Reconstruction would require understanding the exact format and valid values.
**Correction:** DO NOT reconstruct. Original file exists in authorized game content.

## Corrected Classifications

| Field | Previous | Corrected |
|-------|----------|-----------|
| OPENKEY_FILE_STATUS | MISSING | MISSING_AT_EXPECTED_RUNTIME_PATH |
| OPENKEY_ROLE | ROOT_CAUSE | REQUIRED_CANDIDATE |
| OPENKEY_PRODUCER | NesysService | UNKNOWN |
| NESYSSERVICE_GENERATION_ROLE | Confirmed | NOT_PROVEN |
| OPENKEY_CONTENT_REQUIREMENTS | Known | UNKNOWN_AND_SENSITIVE |

## Historical Report Preservation

Prior documents (G9_POST_HTTP_GATING_ANALYSIS.md, STARWING_BOOT_DEPENDENCY_GRAPH.md, etc.) are NOT rewritten. Dated correction notes are added where claims appear.
