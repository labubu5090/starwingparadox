# Security and Authorization Boundary

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: I

## Overview

This document establishes an explicit technical boundary for the Python rewrite. The implementation must not cross these boundaries under any circumstances.

## Prohibited Actions

### NESYS Service Impersonation

| Action | Prohibition | Rationale |
|--------|-------------|-----------|
| Present as NESYS service | FORBIDDEN | Vendor impersonation |
| Use NESYS service name | FORBIDDEN | Trademark infringement |
| Claim NESYS authorization | FORBIDDEN | False authorization |
| Replicate NESYS authentication | FORBIDDEN | Security bypass |
| Emulate NESYS endpoints | FORBIDDEN | Infrastructure impersonation |

### Production Certificate Operations

| Action | Prohibition | Rationale |
|--------|-------------|-----------|
| Use original certificates | FORBIDDEN | Unauthorized use |
| Request certificates from cert3.nesys.jp | FORBIDDEN | Unauthorized access |
| Install certificates to store | FORBIDDEN | System mutation |
| Use private keys | FORBIDDEN | Unauthorized use |
| Bypass certificate validation | FORBIDDEN | Security bypass |
| Export certificate material | FORBIDDEN | Data exfiltration |

### Production Network Operations

| Action | Prohibition | Rationale |
|--------|-------------|-----------|
| Connect to cert3.nesys.jp | FORBIDDEN | Unauthorized access |
| Connect to data.nesys.jp | FORBIDDEN | Unauthorized access |
| Connect to nesys.taito.co.jp | FORBIDDEN | Unauthorized access |
| Connect to fjm170920zero.nesica.net | FORBIDDEN | Unauthorized access |
| Resolve production hostnames | FORBIDDEN | Infrastructure probing |
| Replay captured traffic | FORBIDDEN | Traffic replay |
| Use production credentials | FORBIDDEN | Credential misuse |

### Windows System Mutation

| Action | Prohibition | Rationale |
|--------|-------------|-----------|
| Register Windows service | FORBIDDEN | System mutation |
| Create HKLM Registry values | FORBIDDEN | System mutation |
| Install certificates | FORBIDDEN | System mutation |
| Modify service configuration | FORBIDDEN | System mutation |
| Change service account | FORBIDDEN | Security mutation |
| Add service dependencies | FORBIDDEN | System mutation |

### Original Binary Operations

| Action | Prohibition | Rationale |
|--------|-------------|-----------|
| Execute original binaries | FORBIDDEN | Unauthorized execution |
| Patch original binaries | FORBIDDEN | Modification |
| Modify original game content | FORBIDDEN | Modification |
| Copy original binaries | FORBIDDEN | Unauthorized copying |
| Reverse engineer for implementation | FORBIDDEN | IP violation |

### Data Operations

| Action | Prohibition | Rationale |
|--------|-------------|-----------|
| Process real customer data | FORBIDDEN | Privacy violation |
| Process payment data | FORBIDDEN | PCI violation |
| Store production credentials | FORBIDDEN | Security risk |
| Log sensitive data | FORBIDDEN | Data exposure |
| Export user data | FORBIDDEN | Privacy violation |

## Allowed Development Scope

### Local Development

| Action | Permitted | Conditions |
|--------|-----------|------------|
| Local isolated development | YES | No outbound network |
| Operator-owned hardware | YES | Explicit authorization |
| Synthetic test data | YES | No production data |
| Protocol abstractions | YES | Independent implementation |
| Offline unit testing | YES | No live systems |
| Offline integration testing | YES | No live systems |
| Explicit operator-controlled configuration | YES | Documented configuration |

### Protocol Implementation

| Action | Permitted | Conditions |
|--------|-----------|------------|
| Independent protocol implementation | YES | Clean-room design |
| Synthetic transport | YES | No production pipes |
| Mock services | YES | No production endpoints |
| Test fixtures | YES | Synthetic data only |
| Command catalog | YES | Observable interfaces only |
| State machines | YES | Observable behavior only |

### Testing

| Action | Permitted | Conditions |
|--------|-----------|------------|
| Unit tests | YES | Isolated, synthetic |
| Integration tests | YES | Synthetic transport |
| Protocol tests | YES | Known command catalog |
| State transition tests | YES | Observable behavior |
| Error handling tests | YES | Observable errors |
| Timeout tests | YES | Configurable timeouts |

## Existing Implementation Boundary Review

### Current Implementation

| Component | Boundary Status | Action Required |
|-----------|----------------|-----------------|
| TCP server core | COMPLIANT | None |
| Frame codec | COMPLIANT | None |
| Protobuf codegen | COMPLIANT | None |
| Message registry | COMPLIANT | None |
| Handler dispatch | COMPLIANT | None |
| Ping/PingResponse | COMPLIANT | None |
| Test suite | COMPLIANT | None |

### No Boundary Violations Found

The current Python implementation contains no security or authorization boundary violations. All existing code operates within the allowed development scope.

## Containment Recommendations

No containment actions are required. The current implementation is fully compliant with the security and authorization boundary.

## Monitoring

| Monitor | Frequency | Action |
|---------|-----------|--------|
| Code review | Every commit | Check boundary compliance |
| Security scan | Weekly | Check for violations |
| Dependency audit | Monthly | Check for vulnerable dependencies |
| Boundary review | Quarterly | Update boundary as needed |
