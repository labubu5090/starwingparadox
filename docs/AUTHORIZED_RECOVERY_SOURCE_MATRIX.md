# Authorized Recovery Source Matrix

**Phase**: 2A-G15  
**Date**: 2026-08-28  
**Status**: COMPLETE  

---

## Executive Summary

The operator-owned content contains only a D-drive backup. The original C-drive, system image, installer package, and other recovery sources are NOT available. The service registration and provisioning state cannot be recovered from the available content.

---

## Recovery Source Matrix

### 1. Original C-Drive Image

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No C-drive content in operator-owned files |
| Service registration | NOT_FOUND |
| Certificate store | NOT_FOUND |
| Registry configuration | NOT_FOUND |
| Startup configuration | NOT_FOUND |
| Impact | CRITICAL - Required for complete recovery |

**Classification**: `NOT_FOUND`

### 2. Original Physical System Drive

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No physical drive access |
| Service registration | NOT_FOUND |
| Certificate store | NOT_FOUND |
| Registry configuration | NOT_FOUND |
| Startup configuration | NOT_FOUND |
| Impact | CRITICAL - Required for complete recovery |

**Classification**: `NOT_FOUND`

### 3. Operator-Created Backup

| Property | Status |
|----------|--------|
| Availability | AVAILABLE (D-drive only) |
| Evidence | X:\StarwingParadox\D DRIVE CONTENTS |
| Service registration | NOT_FOUND |
| Certificate store | NOT_FOUND |
| Registry configuration | NOT_FOUND |
| Startup configuration | NOT_FOUND |
| Impact | PARTIAL - Contains game files only |

**Classification**: `AVAILABLE_BUT_INCOMPLETE`

### 4. Arcade Distributor Recovery Image

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No recovery image found |
| Service registration | UNKNOWN |
| Certificate store | UNKNOWN |
| Registry configuration | UNKNOWN |
| Startup configuration | UNKNOWN |
| Impact | UNKNOWN - May contain required state |

**Classification**: `NOT_FOUND`

### 5. Authorized Installer Package

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No installer package found |
| Service registration | UNKNOWN |
| Certificate store | UNKNOWN |
| Registry configuration | UNKNOWN |
| Startup configuration | UNKNOWN |
| Impact | UNKNOWN - May contain registration logic |

**Classification**: `NOT_FOUND`

### 6. Vendor Deployment Media

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No deployment media found |
| Service registration | UNKNOWN |
| Certificate store | UNKNOWN |
| Registry configuration | UNKNOWN |
| Startup configuration | UNKNOWN |
| Impact | UNKNOWN - May contain deployment scripts |

**Classification**: `NOT_FOUND`

### 7. Windows System32 Service Registry Hive

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No registry hive files found |
| Service registration | NOT_FOUND |
| Certificate store | NOT_FOUND |
| Registry configuration | NOT_FOUND |
| Startup configuration | NOT_FOUND |
| Impact | CRITICAL - Contains service registration |

**Classification**: `NOT_FOUND`

### 8. Exported Service Metadata

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No exported metadata found |
| Service registration | NOT_FOUND |
| Certificate store | NOT_FOUND |
| Registry configuration | NOT_FOUND |
| Startup configuration | NOT_FOUND |
| Impact | CRITICAL - Contains service configuration |

**Classification**: `NOT_FOUND`

### 9. Old Maintenance Backup

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No maintenance backup found |
| Service registration | UNKNOWN |
| Certificate store | UNKNOWN |
| Registry configuration | UNKNOWN |
| Startup configuration | UNKNOWN |
| Impact | UNKNOWN - May contain historical state |

**Classification**: `NOT_FOUND`

### 10. Installation Log

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No installation log found |
| Service registration | NOT_FOUND |
| Certificate store | NOT_FOUND |
| Registry configuration | NOT_FOUND |
| Startup configuration | NOT_FOUND |
| Impact | CRITICAL - Contains installation history |

**Classification**: `NOT_FOUND`

### 11. Cabinet Clone

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No cabinet clone found |
| Service registration | UNKNOWN |
| Certificate store | UNKNOWN |
| Registry configuration | UNKNOWN |
| Startup configuration | UNKNOWN |
| Impact | UNKNOWN - May contain complete state |

**Classification**: `NOT_FOUND`

### 12. Legitimate Spare Cabinet Image

| Property | Status |
|----------|--------|
| Availability | NOT_FOUND |
| Evidence | No spare cabinet image found |
| Service registration | UNKNOWN |
| Certificate store | UNKNOWN |
| Registry configuration | UNKNOWN |
| Startup configuration | UNKNOWN |
| Impact | UNKNOWN - May contain complete state |

**Classification**: `NOT_FOUND`

---

## Summary

| Source | Availability | Impact |
|--------|--------------|--------|
| Original C-drive image | NOT_FOUND | CRITICAL |
| Original physical system drive | NOT_FOUND | CRITICAL |
| Operator-created backup | AVAILABLE_BUT_INCOMPLETE | PARTIAL |
| Arcade distributor recovery image | NOT_FOUND | UNKNOWN |
| Authorized installer package | NOT_FOUND | UNKNOWN |
| Vendor deployment media | NOT_FOUND | UNKNOWN |
| Windows System32 service Registry hive | NOT_FOUND | CRITICAL |
| Exported service metadata | NOT_FOUND | CRITICAL |
| Old maintenance backup | NOT_FOUND | UNKNOWN |
| Installation log | NOT_FOUND | CRITICAL |
| Cabinet clone | NOT_FOUND | UNKNOWN |
| Legitimate spare cabinet image | NOT_FOUND | UNKNOWN |

---

## Classification

**RECOVERY_SOURCE_MATRIX**: `MOST_SOURCES_NOT_AVAILABLE`

**Rationale**:
- Only operator-created backup is available (D-drive only)
- All other sources are NOT_FOUND
- Critical sources (C-drive, registry hive, service metadata, installation log) are missing
- Service registration and provisioning state cannot be recovered

---

## Conclusion

The operator-owned content contains only a D-drive backup. The original C-drive, system image, installer package, and other recovery sources are NOT available. The service registration and provisioning state cannot be recovered from the available content.

**Classification**: `RECOVERY_SOURCES_INSUFFICIENT`

The available recovery sources are insufficient to recover the service registration and provisioning state.

---

## G15 Audit Notes

This document was created in Phase 2A-G15 to create an authorized recovery source matrix. Most sources are NOT_AVAILABLE. Only the operator-created D-drive backup is available, but it is incomplete for service registration recovery.
