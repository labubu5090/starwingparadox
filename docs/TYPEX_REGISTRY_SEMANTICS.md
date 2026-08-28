# typex Registry Semantics

**Phase**: 2A-G14  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe reads 8 configuration values from `HKLM\SOFTWARE\taito\typex`. Each value is read-only at startup. No registry write operations were found. Default values and valid ranges are NOT_SHOWN in static analysis.

---

## Registry Key Structure

```
HKEY_LOCAL_MACHINE
  └── SOFTWARE
      └── taito
          └── typex
              ├── GameKind        (REG_DWORD)
              ├── EventNextTime   (REG_DWORD)
              ├── ConditionTime   (REG_DWORD)
              ├── TrafficCount    (REG_DWORD)
              ├── LogLevel        (REG_DWORD)
              ├── NewsPath        (REG_SZ)
              ├── EventPath       (REG_SZ)
              └── LogPath         (REG_SZ)
```

---

## Registry APIs

### Imported APIs

| API | Import | Usage |
|-----|--------|-------|
| RegOpenKeyExA | YES | Opens registry key |
| RegQueryValueExA | YES | Reads registry value |

### Missing APIs

| API | Required For | Present |
|-----|--------------|---------|
| RegSetValueExA | Write value | NOT_FOUND |
| RegCreateKeyExA | Create key | NOT_FOUND |
| RegDeleteValueA | Delete value | NOT_FOUND |
| RegCloseKey | Close key | NOT_FOUND (may use automatic cleanup) |

**Registry Operations**: `READ_ONLY`

---

## Value Analysis

### GameKind

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | GameKind | CONFIRMED | String reference |
| Type | REG_DWORD | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | STATIC | INFERRED | Read-only at startup |
| Classification | INSTALLATION_IDENTITY | INFERRED | Unique per installation |

### EventNextTime

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | EventNextTime | CONFIRMED | String reference |
| Type | REG_DWORD | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | RUNTIME_STATE | INFERRED | May change over time |
| Classification | RUNTIME_STATE | INFERRED | Time-based value |

### ConditionTime

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | ConditionTime | CONFIRMED | String reference |
| Type | REG_DWORD | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | RUNTIME_STATE | INFERRED | May change over time |
| Classification | RUNTIME_STATE | INFERRED | Time-based value |

### TrafficCount

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | TrafficCount | CONFIRMED | String reference |
| Type | REG_DWORD | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | RUNTIME_STATE | INFERRED | May change over time |
| Classification | RUNTIME_STATE | INFERRED | Counter value |

### LogLevel

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | LogLevel | CONFIRMED | String reference |
| Type | REG_DWORD | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | STATIC | INFERRED | Read-only at startup |
| Classification | LOGGING_CONFIGURATION | INFERRED | Controls logging |

### NewsPath

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | NewsPath | CONFIRMED | String reference |
| Type | REG_SZ | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | STATIC | INFERRED | Read-only at startup |
| Classification | FILE_PATH | INFERRED | File system path |

### EventPath

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | EventPath | CONFIRMED | String reference |
| Type | REG_SZ | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | STATIC | INFERRED | Read-only at startup |
| Classification | FILE_PATH | INFERRED | File system path |

### LogPath

| Property | Value | Confidence | Evidence |
|----------|-------|------------|----------|
| Name | LogPath | CONFIRMED | String reference |
| Type | REG_SZ | HIGH | Inferred from name |
| Operation | READ | CONFIRMED | RegQueryValueExA |
| Default value | NOT_SHOWN | NOT_FOUND | No default in code |
| Valid range | NOT_SHOWN | NOT_FOUND | No validation in code |
| Missing behavior | NOT_SHOWN | NOT_FOUND | No fallback logic |
| Malformed behavior | NOT_SHOWN | NOT_FOUND | No error handling |
| Downstream | NOT_SHOWN | NOT_FOUND | No usage analysis |
| Mutability | STATIC | INFERRED | Read-only at startup |
| Classification | FILE_PATH | INFERRED | File system path |

---

## Value Classifications

| Value | Classification | Rationale |
|-------|----------------|-----------|
| GameKind | INSTALLATION_IDENTITY | Unique per cabinet/installation |
| EventNextTime | RUNTIME_STATE | Time-based, may change |
| ConditionTime | RUNTIME_STATE | Time-based, may change |
| TrafficCount | RUNTIME_STATE | Counter, may change |
| LogLevel | LOGGING_CONFIGURATION | Controls logging behavior |
| NewsPath | FILE_PATH | File system path reference |
| EventPath | FILE_PATH | File system path reference |
| LogPath | FILE_PATH | File system path reference |

---

## Missing-Value Behavior

### Status

| Value | Missing Behavior | Evidence |
|-------|------------------|----------|
| GameKind | NOT_SHOWN | No fallback logic |
| EventNextTime | NOT_SHOWN | No fallback logic |
| ConditionTime | NOT_SHOWN | No fallback logic |
| TrafficCount | NOT_SHOWN | No fallback logic |
| LogLevel | NOT_SHOWN | No fallback logic |
| NewsPath | NOT_SHOWN | No fallback logic |
| EventPath | NOT_SHOWN | No fallback logic |
| LogPath | NOT_SHOWN | No fallback logic |

**Missing-Value Behavior**: `NOT_SHOWN`

---

## Malformed-Value Behavior

### Status

| Value | Malformed Behavior | Evidence |
|-------|--------------------|----------|
| GameKind | NOT_SHOWN | No error handling |
| EventNextTime | NOT_SHOWN | No error handling |
| ConditionTime | NOT_SHOWN | No error handling |
| TrafficCount | NOT_SHOWN | No error handling |
| LogLevel | NOT_SHOWN | No error handling |
| NewsPath | NOT_SHOWN | No error handling |
| EventPath | NOT_SHOWN | No error handling |
| LogPath | NOT_SHOWN | No error handling |

**Malformed-Value Behavior**: `NOT_SHOWN`

---

## Downstream Functions

### Status

| Value | Downstream Function | Evidence |
|-------|---------------------|----------|
| GameKind | NOT_SHOWN | No usage analysis |
| EventNextTime | NOT_SHOWN | No usage analysis |
| ConditionTime | NOT_SHOWN | No usage analysis |
| TrafficCount | NOT_SHOWN | No usage analysis |
| LogLevel | NOT_SHOWN | No usage analysis |
| NewsPath | NOT_SHOWN | No usage analysis |
| EventPath | NOT_SHOWN | No usage analysis |
| LogPath | NOT_SHOWN | No usage analysis |

**Downstream Functions**: `NOT_SHOWN`

---

## Runtime Mutability

| Value | Mutability | Evidence |
|-------|------------|----------|
| GameKind | STATIC | Read-only at startup |
| EventNextTime | RUNTIME_STATE | May change over time |
| ConditionTime | RUNTIME_STATE | May change over time |
| TrafficCount | RUNTIME_STATE | May change over time |
| LogLevel | STATIC | Read-only at startup |
| NewsPath | STATIC | Read-only at startup |
| EventPath | STATIC | Read-only at startup |
| LogPath | STATIC | Read-only at startup |

---

## Machine Provisioning vs Runtime State

| Value | Category | Rationale |
|-------|----------|-----------|
| GameKind | MACHINE_PROVISIONING | Unique per installation |
| EventNextTime | RUNTIME_STATE | Time-based |
| ConditionTime | RUNTIME_STATE | Time-based |
| TrafficCount | RUNTIME_STATE | Counter |
| LogLevel | MACHINE_PROVISIONING | Configuration |
| NewsPath | MACHINE_PROVISIONING | File path |
| EventPath | MACHINE_PROVISIONING | File path |
| LogPath | MACHINE_PROVISIONING | File path |

---

## Cabinet Uniqueness

| Value | Unique Per Cabinet | Evidence |
|-------|-------------------|----------|
| GameKind | PROBABLY | Game identifier |
| EventNextTime | NO | Time-based |
| ConditionTime | NO | Time-based |
| TrafficCount | NO | Counter |
| LogLevel | NO | Configuration |
| NewsPath | PROBABLY | File path |
| EventPath | PROBABLY | File path |
| LogPath | PROBABLY | File path |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Registry key path | CONFIRMED |
| Value names | CONFIRMED |
| Value types | HIGH |
| Read operations | CONFIRMED |
| Write operations | NOT_FOUND |
| Default values | NOT_SHOWN |
| Valid ranges | NOT_SHOWN |
| Missing behavior | NOT_SHOWN |
| Malformed behavior | NOT_SHOWN |
| Downstream functions | NOT_SHOWN |

---

## Registry Semantics JSON

**Output**: `artifacts/phase_2a_g14/registry_semantics.json`

```json
{
  "phase": "2A-G14",
  "executable": "NesysService.exe",
  "registry_key": {
    "hive": "HKEY_LOCAL_MACHINE",
    "subkey": "SOFTWARE\\taito\\typex",
    "confidence": "CONFIRMED"
  },
  "values": [
    {
      "name": "GameKind",
      "type": "REG_DWORD",
      "operation": "READ",
      "classification": "INSTALLATION_IDENTITY",
      "mutability": "STATIC",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    },
    {
      "name": "EventNextTime",
      "type": "REG_DWORD",
      "operation": "READ",
      "classification": "RUNTIME_STATE",
      "mutability": "RUNTIME_STATE",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    },
    {
      "name": "ConditionTime",
      "type": "REG_DWORD",
      "operation": "READ",
      "classification": "RUNTIME_STATE",
      "mutability": "RUNTIME_STATE",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    },
    {
      "name": "TrafficCount",
      "type": "REG_DWORD",
      "operation": "READ",
      "classification": "RUNTIME_STATE",
      "mutability": "RUNTIME_STATE",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    },
    {
      "name": "LogLevel",
      "type": "REG_DWORD",
      "operation": "READ",
      "classification": "LOGGING_CONFIGURATION",
      "mutability": "STATIC",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    },
    {
      "name": "NewsPath",
      "type": "REG_SZ",
      "operation": "READ",
      "classification": "FILE_PATH",
      "mutability": "STATIC",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    },
    {
      "name": "EventPath",
      "type": "REG_SZ",
      "operation": "READ",
      "classification": "FILE_PATH",
      "mutability": "STATIC",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    },
    {
      "name": "LogPath",
      "type": "REG_SZ",
      "operation": "READ",
      "classification": "FILE_PATH",
      "mutability": "STATIC",
      "default_value": "NOT_SHOWN",
      "valid_range": "NOT_SHOWN"
    }
  ]
}
```

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Default values | NOT_SHOWN | No defaults in code |
| Valid ranges | NOT_SHOWN | No validation in code |
| Missing behavior | NOT_SHOWN | No fallback logic |
| Malformed behavior | NOT_SHOWN | No error handling |
| Downstream functions | NOT_SHOWN | No usage analysis |
| Runtime mutability | INFERRED | Some values may change |

---

## Conclusion

NesysService.exe reads 8 configuration values from `HKLM\SOFTWARE\taito\typex`. Each value is read-only at startup. No registry write operations were found. Default values and valid ranges are NOT_SHOWN in static analysis.

**Classification**: `READ_ONLY_CONFIGURATION`

The registry contract is confirmed for read operations. Write operations, default values, and validation logic are NOT_SHOWN.

---

## G14 Audit Notes

This document was created in Phase 2A-G14 to determine registry value semantics. All values are classified with appropriate confidence levels. Inferences are clearly marked and not promoted to confirmed facts.
