# CLEANROOM FRAME VALIDATION

**Date:** August 28, 2026  
**Phase:** 2A-G17  
**Classification:** Technical Specification

---

## Overview

Frame Validation defines the rules and procedures for validating incoming transport frames in the Starwing system, derived from G16 specification evidence.

---

## Frame Format Specification

### Standard Frame Structure

| Offset | Size | Field | Description | G16 Ref |
|---|---|---|---|---|
| 0x00 | 2 | Magic | 0x5357 ("SW") | §3.2.1 |
| 0x02 | 1 | Version | Protocol version | §3.2.2 |
| 0x03 | 1 | Type | Frame type identifier | §3.2.3 |
| 0x04 | 4 | Length | Payload length (max 1MB) | §3.2.4 |
| 0x08 | 4 | Sequence | Sequence number | §3.2.5 |
| 0x0C | 4 | Reserved | Must be zero | §3.2.6 |
| 0x10 | N | Payload | Frame payload | §3.2.7 |
| 0x10+N | 4 | Checksum | CRC32 of frame | §3.2.8 |

---

## Validation Pipeline

```
Raw Bytes
    │
    ▼
┌─────────────────────┐
│ 1. Size Validation   │
│    - Minimum: 20B    │
│    - Maximum: 1MB+20B│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 2. Magic Validation  │
│    - Check 0x5357    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. Version Check     │
│    - Support range   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 4. Type Validation   │
│    - Known type ID   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 5. Length Validation  │
│    - Bounds check    │
│    - Alignment check │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 6. Checksum Verify   │
│    - CRC32 match     │
└──────────┬──────────┘
           │
           ▼
    Valid Frame
```

---

## Validation Rules

### Rule 1: Size Validation
```
IF frame_size < MIN_FRAME_SIZE (20 bytes):
    REJECT with ERROR_TOO_SMALL
IF frame_size > MAX_FRAME_SIZE (1MB + 20 bytes):
    REJECT with ERROR_TOO_LARGE
```
**G16 Ref:** §3.3.1

### Rule 2: Magic Validation
```
IF magic_bytes != 0x5357:
    REJECT with ERROR_INVALID_MAGIC
```
**G16 Ref:** §3.3.2

### Rule 3: Version Validation
```
IF version < MIN_SUPPORTED_VERSION OR version > MAX_SUPPORTED_VERSION:
    REJECT with ERROR_UNSUPPORTED_VERSION
```
**G16 Ref:** §3.3.3

### Rule 4: Type Validation
```
IF type_id NOT IN KNOWN_TYPES:
    REJECT with ERROR_UNKNOWN_TYPE
```
**G16 Ref:** §3.3.4

### Rule 5: Length Validation
```
IF payload_length != frame_size - HEADER_SIZE - CHECKSUM_SIZE:
    REJECT with ERROR_LENGTH_MISMATCH
IF payload_length % ALIGNMENT != 0:
    REJECT with ERROR_MISALIGNED
```
**G16 Ref:** §3.3.5

### Rule 6: Checksum Validation
```
calculated_crc = CRC32(frame[0..-4])
IF calculated_crc != frame[-4..]:
    REJECT with ERROR_CHECKSUM_MISMATCH
```
**G16 Ref:** §3.3.6

---

## Error Responses

| Error Code | Name | Action |
|---|---|---|
| 0x01 | ERROR_TOO_SMALL | Reject, log warning |
| 0x02 | ERROR_TOO_LARGE | Reject, log warning |
| 0x03 | ERROR_INVALID_MAGIC | Reject silently |
| 0x04 | ERROR_UNSUPPORTED_VERSION | Reject with version info |
| 0x05 | ERROR_UNKNOWN_TYPE | Reject with type info |
| 0x06 | ERROR_LENGTH_MISMATCH | Reject, log error |
| 0x07 | ERROR_MISALIGNED | Reject, log error |
| 0x08 | ERROR_CHECKSUM_MISMATCH | Reject, log error |

---

## Validation Metrics

- **Target:** 100% malformed frame detection
- **Latency:** < 1ms per frame validation
- **Throughput:** > 10,000 frames/second

---

*Frame validation specification for Phase 2A-G17 cleanroom transport implementation.*
