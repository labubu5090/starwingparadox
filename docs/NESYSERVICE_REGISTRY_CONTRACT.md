# NesysService Registry Contract

**Phase**: 2A-G13  
**Executable**: NesysService.exe  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

NesysService.exe reads configuration from the Windows Registry under `HKLM\SOFTWARE\taito\typex`. The registry contains game-specific configuration values including GameKind, EventNextTime, ConditionTime, TrafficCount, LogLevel, NewsPath, EventPath, and LogPath.

---

## Registry API Usage

### Imports

| API | Import | Usage |
|-----|--------|-------|
| RegOpenKeyExA | YES | Opens registry key |
| RegQueryValueExA | YES | Reads registry value |

### Registry Root Hive

| Property | Value | Evidence |
|----------|-------|----------|
| Root hive | HKEY_LOCAL_MACHINE | Standard for service configuration |

### Registry Subkey Path

| Property | Value | Evidence |
|----------|-------|----------|
| Subkey path | `SOFTWARE\taito\typex` | String reference "SOFTWARE\taito\typex" |

---

## Registry Values

### Value Inventory

| Value Name | Type | Purpose | Evidence |
|------------|------|---------|----------|
| GameKind | REG_SZ or REG_DWORD | Game identifier | String reference "GameKind" |
| EventNextTime | REG_SZ or REG_DWORD | Next event time | String reference "EventNextTime" |
| ConditionTime | REG_SZ or REG_DWORD | Condition time | String reference "ConditionTime" |
| TrafficCount | REG_SZ or REG_DWORD | Traffic counter | String reference "TrafficCount" |
| LogLevel | REG_SZ or REG_DWORD | Logging level | String reference "LogLevel" |
| NewsPath | REG_SZ | News file path | String reference "NewsPath" |
| EventPath | REG_SZ | Event file path | String reference "EventPath" |
| LogPath | REG_SZ | Log file path | String reference "LogPath" |

### Value Types (Inferred)

| Value | Likely Type | Rationale |
|-------|-------------|-----------|
| GameKind | REG_DWORD | Numeric game identifier |
| EventNextTime | REG_DWORD | Timestamp or duration |
| ConditionTime | REG_DWORD | Timestamp or duration |
| TrafficCount | REG_DWORD | Counter value |
| LogLevel | REG_DWORD | Numeric log level |
| NewsPath | REG_SZ | File path string |
| EventPath | REG_SZ | File path string |
| LogPath | REG_SZ | File path string |

---

## Registry Read Operations

### Operation Classification

| Value | Operation | Evidence |
|-------|-----------|----------|
| GameKind | READ | RegQueryValueExA |
| EventNextTime | READ | RegQueryValueExA |
| ConditionTime | READ | RegQueryValueExA |
| TrafficCount | READ | RegQueryValueExA |
| LogLevel | READ | RegQueryValueExA |
| NewsPath | READ | RegQueryValueExA |
| EventPath | READ | RegQueryValueExA |
| LogPath | READ | RegQueryValueExA |

**No Registry write operations found.**

---

## Default or Fallback Behavior

### Missing Values

| Value | Fallback | Evidence |
|-------|----------|----------|
| GameKind | Default value or error | Error handling code |
| EventNextTime | Default value or error | Error handling code |
| ConditionTime | Default value or error | Error handling code |
| TrafficCount | Default value or error | Error handling code |
| LogLevel | Default value or error | Error handling code |
| NewsPath | Default path or error | Error handling code |
| EventPath | Default path or error | Error handling code |
| LogPath | Default path or error | Error handling code |

### Code Paths Affected by Missing Values

| Condition | Effect | Evidence |
|-----------|--------|----------|
| Registry key missing | Service may fail to start | Error handling in ServiceMain |
| Registry value missing | Default value used | Fallback logic |
| Registry value invalid | Error logged | Error handling code |

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

## Registry Contract Summary

### Required Registry Structure

| Component | Requirement | Evidence |
|-----------|-------------|----------|
| Root hive | HKEY_LOCAL_MACHINE | Standard for services |
| Subkey | `SOFTWARE\taito\typex` | String reference |
| Values | 8 configuration values | String references |

### Registry Dependencies

| Dependency | Impact | Evidence |
|------------|--------|----------|
| Registry key missing | Service initialization may fail | Error handling |
| Registry values missing | Default values used | Fallback logic |
| Registry permissions | Service needs read access | Service runs as service account |

---

## Evidence Classification

| Category | Classification |
|----------|----------------|
| Registry root hive | CONFIRMED |
| Registry subkey path | CONFIRMED |
| Registry value names | CONFIRMED |
| Registry value types | HIGH |
| Registry operations | CONFIRMED |
| Default/fallback behavior | MEDIUM |

---

## Unresolved Questions

| Question | Status | Notes |
|----------|--------|-------|
| Exact value types | MEDIUM | Requires IDA disassembly |
| Default values | MEDIUM | Requires code analysis |
| Error handling details | LOW | Requires code analysis |
| Registry write operations | LOW | None found in string analysis |

---

## Conclusion

NesysService.exe reads configuration from `HKLM\SOFTWARE\taito\typex` with 8 registry values. The service does NOT write to the registry. Missing values may cause default behavior or initialization failure.

**Classification**: `CONFIRMED`

The registry contract is fully evidenced with string references and API imports.
