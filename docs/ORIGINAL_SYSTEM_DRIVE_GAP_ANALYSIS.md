# Original System Drive Gap Analysis

**Phase**: 2A-G12  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Summary

The operator-owned content appears to be a D-drive only backup. The original Windows system drive (C:) is NOT included. This means the original launcher, startup configuration, certificate store, registry, and Windows Service configuration are missing.

---

## Available Content

### D: Drive Backup

| Directory | Contents | Status |
|-----------|----------|--------|
| D DRIVE CONTENTS\system\Service\ | NesysService.exe | PRESENT |
| D DRIVE CONTENTS\system\CmdFile\ | Update system logs | PRESENT |
| D DRIVE CONTENTS\system\DUA\ | Event data, news, OpenKey | PRESENT |
| D DRIVE CONTENTS\system\option.txt | ScreenType, EWF, MemoryLog | PRESENT |
| D DRIVE CONTENTS\Saved\ACRSaved\ | Save data, ranking, test mode | PRESENT |
| D DRIVE CONTENTS\Saved\GalaxySaved\ | UE4 config files | PRESENT |

### Game Content

| Directory | Contents | Status |
|-----------|----------|--------|
| WindowsNoEditor\ | Game executables, configs, content | PRESENT |

---

## Missing System Drive Content

### 1. Original Launcher

| Component | Status | Impact |
|-----------|--------|--------|
| Launcher executable | MISSING | Cannot determine startup sequence |
| Launcher configuration | MISSING | Cannot determine launch parameters |
| Launcher shortcuts | MISSING | No startup folder placement |

### 2. Installed Service Configuration

| Component | Status | Impact |
|-----------|--------|--------|
| Windows Service registration | MISSING | NesysService not registered |
| Service configuration | MISSING | Cannot determine service parameters |
| Service dependencies | MISSING | Cannot determine service order |
| Service startup type | MISSING | Cannot determine automatic/manual |

### 3. Startup Shortcuts

| Component | Status | Impact |
|-----------|--------|--------|
| Start Menu shortcuts | MISSING | No user-initiated launch |
| Startup folder entries | MISSING | No automatic startup |
| Desktop shortcuts | MISSING | No quick launch |

### 4. Scheduled Tasks

| Component | Status | Impact |
|-----------|--------|--------|
| Task definitions | MISSING | No scheduled operations |
| Task triggers | MISSING | No time-based startup |
| Task actions | MISSING | No automated commands |

### 5. Registry

| Component | Status | Impact |
|-----------|--------|--------|
| Run/RunOnce keys | MISSING | No startup programs |
| Service registry entries | MISSING | No service configuration |
| Application registration | MISSING | No file associations |
| COM registration | MISSING | No COM components |

### 6. Certificate Store

| Component | Status | Impact |
|-----------|--------|--------|
| SSL/TLS certificates | MISSING | Cannot establish secure connections |
| NESYS certificates | MISSING | Cannot authenticate with NESYS servers |
| Certificate trust store | MISSING | Cannot validate certificates |

### 7. Device Drivers

| Component | Status | Impact |
|-----------|--------|--------|
| USBIO drivers | MISSING | Cannot communicate with cabinet IO |
| Cabinet-specific drivers | MISSING | Cannot access cabinet hardware |
| Network drivers | MISSING | Standard drivers assumed |

### 8. Cabinet Shell

| Component | Status | Impact |
|-----------|--------|--------|
| Shell replacement | MISSING | No cabinet-specific UI |
| Auto-login | MISSING | No automatic user login |
| Kiosk mode | MISSING | No restricted access |

### 9. Watchdog

| Component | Status | Impact |
|-----------|--------|--------|
| Watchdog configuration | MISSING | No crash recovery |
| Watchdog startup | MISSING | No automatic restart |
| Watchdog monitoring | MISSING | No health checks |

### 10. Environment Variables

| Component | Status | Impact |
|-----------|--------|--------|
| System PATH | MISSING | Cannot find executables |
| NESYS environment | MISSING | Cannot configure NESYS |
| Game environment | MISSING | Cannot configure game |

### 11. NESYS Runtime Dependencies

| Component | Status | Impact |
|-----------|--------|--------|
| NESYS DLLs | MISSING | Cannot load NESYS functions |
| NESYS configuration | MISSING | Cannot configure NESYS |
| NESYS certificates | MISSING | Cannot authenticate |

---

## Evidence from Available Content

### option.txt

```
[Option]
ScreenType=0
EWF=1
MemoryLog=0
```

**EWF=1** indicates Enhanced Write Filter is enabled, confirming this is an embedded/arcade system.

### NoHDDUnload.ini

```
[init]
WriteFileInterval=50000
```

Indicates write-back cache mechanism with 50-second intervals.

### CmdFile Log

40,728 lines of update/command operations, but no NesysService references.

---

## Classification

**SYSTEM_DRIVE_BACKUP**: `D_DRIVE_ONLY_BACKUP`

**Rationale**:
- Only D: drive content is present
- No C: drive content found
- No system drive components found
- No startup configuration found
- No registry found
- No certificate store found
- No Windows Service configuration found

---

## Impact on NesysService Launch

The missing system drive content means:

1. **No launcher** → Cannot determine how NesysService was started
2. **No service registration** → NesysService cannot be registered as a Windows Service
3. **No certificates** → NesysService cannot authenticate with NESYS servers
4. **No registry** → NesysService cannot read configuration
5. **No startup sequence** → Cannot determine startup order
6. **No watchdog** → Cannot recover from crashes

---

## Conclusion

The operator-owned content is a **D-drive only backup**. The original Windows system drive is NOT included. This means the original launcher, startup configuration, certificate store, registry, and Windows Service configuration are missing.

**Classification**: `D_DRIVE_ONLY_BACKUP`

**Recommendation**: The original system drive is required to determine the complete startup sequence and NesysService invocation context.
