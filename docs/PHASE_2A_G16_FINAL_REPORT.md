# Phase 2A-G16 Final Report

**Date**: 2026-08-28
**Phase**: 2A-G16
**Title**: Original Runtime Recovery Closure and Clean-room Compatibility Boundary
**Status**: COMPLETE
**Classification**: CLEANROOM_COMPATIBILITY_SCOPE_DEFINED

## Executive Summary

Phase 2A-G16 formally closed the speculative original runtime recovery branch and established a clean-room compatibility boundary for the Python rewrite. The in-scope original-runtime recovery investigation reached its evidence limit. No safe reconstruction is possible from the available backup.

## Primary Decision

The project will NOT continue trying to restore the original NesysService installation from the D-drive backup. The original runtime recovery branch is formally closed.

## Key Findings

### Evidence Consolidation

| Category | Confirmed | Unresolved | Not Found |
|----------|-----------|------------|-----------|
| Executables | 3 | 0 | 0 |
| Named pipe protocol | 12 | 35 | 0 |
| Registry configuration | 9 | 8 | 0 |
| Certificate store | 3 | 5 | 0 |
| Network endpoints | 8 | 4 | 0 |
| Service lifecycle | 8 | 4 | 0 |
| D-drive backup | 12 | 0 | 0 |
| **Total** | **55** | **56** | **0** |

### Startup Model Correction

| Model | Status | Confidence |
|-------|--------|------------|
| CONFIRMED OBSERVED RELATIONSHIPS | 10 items | HIGH |
| PLAUSIBLE BUT UNPROVEN | 8 items | MEDIUM |
| CURRENT FAILURE MODEL | 8 items | CONFIRMED |

### Clean-room Input Eligibility

| Category | Count | Permitted Use |
|----------|-------|---------------|
| ELIGIBLE_INTERFACE_FACT | 35 | Protocol specification |
| ELIGIBLE_FAILURE_BEHAVIOR | 6 | Error testing |
| DOCUMENTATION_ONLY | 12 | Historical understanding |
| RESTRICTED_SECURITY_BEHAVIOR | 12 | Excluded |
| UNKNOWN_DO_NOT_IMPLEMENT | 8 | Not implemented |
| PROPRIETARY_INTERNAL_DETAIL_EXCLUDED | 3 | Excluded |

### Protocol Confidence Matrix

| Command Type | Total | Confirmed | Protocol-Identified | Unknown |
|--------------|-------|-----------|---------------------|---------|
| LCOMMAND | 47 | 3 | 10 | 34 |
| SCOMMAND | 44 | 5 | 10 | 29 |
| **Total** | **91** | **8** | **20** | **63** |

### Implementation Gap Analysis

| Component | Implemented | Partial | Not Implemented | Excluded |
|-----------|-------------|---------|-----------------|----------|
| Transport layer | 4 | 0 | 2 | 0 |
| Session state | 1 | 0 | 2 | 0 |
| Command decoder | 5 | 1 | 0 | 0 |
| Command encoder | 2 | 0 | 2 | 0 |
| Request dispatcher | 4 | 0 | 0 | 0 |
| Compatibility adapter | 1 | 0 | 15 | 4 |
| Command catalog | 2 | 1 | 10 | 0 |
| State machine | 0 | 0 | 3 | 0 |
| Validation rules | 3 | 1 | 3 | 0 |
| Error handling | 3 | 1 | 4 | 0 |
| **Total** | **25** | **3** | **41** | **4** |

## Documents Created

| Document | Workstream | Purpose |
|----------|------------|---------|
| PHASE_2A_G16_INITIAL_BASELINE.md | -- | Initial baseline |
| PHASE_2A_G16_ANALYSIS_PLAN.md | -- | Analysis plan |
| ORIGINAL_RUNTIME_RECOVERY_CLOSURE.md | A | Recovery closure record |
| G12_G15_CONSOLIDATED_EVIDENCE_MATRIX.md | B | Evidence consolidation |
| ORIGINAL_STARTUP_MODEL_CORRECTION.md | C | Startup model correction |
| CLEANROOM_INPUT_ELIGIBILITY.md | D | Input eligibility |
| NESYS_PROTOCOL_CONFIDENCE_MATRIX.md | E | Protocol confidence |
| CLEANROOM_COMPATIBILITY_SPECIFICATION.md | G | Compatibility specification |
| CURRENT_IMPLEMENTATION_GAP_ANALYSIS.md | H | Gap analysis |
| SECURITY_AND_AUTHORIZATION_BOUNDARY.md | I | Security boundary |
| ADR_ORIGINAL_NESYSERVICE_RECOVERY_CLOSURE.md | J | Decision record |
| PHASE_2A_G16_FINAL_REPORT.md | -- | Final report |

## Artifacts Created

| Artifact | Workstream | Purpose |
|----------|------------|---------|
| consolidated_evidence.json | B | Machine-readable evidence |
| cleanroom_input_eligibility.json | D | Machine-readable eligibility |
| protocol_confidence_matrix.json | E | Machine-readable protocol |
| implementation_gap_analysis.json | H | Machine-readable gap analysis |
| recovery_closure.json | A | Machine-readable closure |

## Synthetic Fixtures Created

| Fixture | Purpose |
|---------|---------|
| tests/fixtures/starwing_cleanroom/README.md | Fixture documentation |
| tests/fixtures/starwing_cleanroom/command_catalog.json | Symbolic command catalog |
| tests/fixtures/starwing_cleanroom/lifecycle_cases.json | Lifecycle test cases |
| tests/fixtures/starwing_cleanroom/invalid_cases.json | Invalid input test cases |

## Final Classification

**CLEANROOM_COMPATIBILITY_SCOPE_DEFINED**

The original runtime recovery branch has reached its evidence limit. The protocol matrix, lifecycle, and transport boundary contain enough confirmed evidence to define a meaningful synthetic G17 implementation.

## Quality Gates

| Gate | Baseline | Result | Status |
|------|----------|--------|--------|
| pytest | 834 passed | 834 passed | PASS |
| skipped | 1 | 1 | PASS |
| failed | 0 | 0 | PASS |
| Ruff | 0 errors | 0 errors | PASS |
| Mypy | 0 errors | 0 errors | PASS |

## Integrity Gates

| Gate | Expected | Result | Status |
|------|----------|--------|--------|
| NesysService.exe SHA-256 | 3A968F29... | 3A968F29... | PASS |
| AcrGame.exe SHA-256 | 97800621... | 97800621... | PASS |
| AcrGame-Win64-Shipping.exe SHA-256 | CE4C8905... | CE4C8905... | PASS |
| No original binary modified | None | None | PASS |
| No Registry value created | None | None | PASS |
| No Windows service created | None | None | PASS |
| No certificate installed or exported | None | None | PASS |
| No hosts or DNS modification | None | None | PASS |
| No production connection | None | None | PASS |
| No live named pipe created | None | None | PASS |
| No original executable launched | None | None | PASS |

## Confirmed Runtime Facts Consolidated

1. Service name: NesysService (CONFIRMED)
2. Entry point: swp_service_main (CONFIRMED)
3. Control handler: swp_service_ctrl_handler (CONFIRMED)
4. Named pipe: \\.\pipe\nesys_games (CONFIRMED)
5. Registry key: HKLM\SOFTWARE\taito\typex (CONFIRMED)
6. Certificate store: MY\.Default (CONFIRMED)
7. Certificate subject: nesys (CONFIRMED)
8. Network endpoints: 4 hostnames (CONFIRMED)
9. Command types: 47 LCOMMAND, 44 SCOMMAND (CONFIRMED)
10. Self-installation: NOT_FOUND (CONFIRMED)

## Corrected or Downgraded Historical Claims

| Phase | Original Claim | Correction | Reason |
|-------|---------------|------------|--------|
| G13 | "connects to cert3.nesys.jp" | Hostname reference only | String ≠ network connection |
| G13 | "retrieves certificate" | Certificate store access only | Store API ≠ retrieval |
| G13 | "NesysClient plugin initializes" | Removed | Not evidenced in static analysis |
| G13 | "Card operations available" | Removed | Not evidenced in static analysis |
| G13 | service.display_name = "NesysService" | NOT_FOUND | No direct evidence |
| G13 | service.description = "NESYS communication..." | NOT_FOUND | No evidence |
| G13 | certificates[0].private_key_required = true | PROBABLY_REQUIRED | Inference, not confirmed |
| G13 | certificates[0].purpose = "Client authentication..." | UNRESOLVED | Hostname ref ≠ operation |
| G13 | network[*].purpose = specific operations | UNRESOLVED | Hostname refs ≠ operations |

## Interface Facts Eligible for Clean-room Use

1. Pipe name: \\.\pipe\nesys_games
2. Server creates pipe, client connects
3. Message-based framing
4. 4-byte LE length prefix
5. 47 LCOMMAND types (game→service)
6. 44 SCOMMAND types (service→game)
7. LCOMMAND_CLIENT_START / CLIENT_END
8. LCOMMAND_PING (0x66) / SCOMMAND_PING_RESPONSE (0x67)
9. Registry key and 8 value names
10. Certificate store path and subject
11. Network hostnames (for documentation only)
12. Service lifecycle states
13. Error behaviors (CERT_ERROR, NW_ERROR, NWRECOVER_NOTICE)

## Restricted or Excluded Behaviors

1. Private key acquisition
2. TLS client certificate attachment
3. Server certificate validation
4. cert3.nesys.jp operations
5. Production network connections
6. Certificate installation
7. Registry provisioning
8. Service registration
9. Original binary execution
10. Production credential usage

## Protocol Commands Classified

| Category | LCOMMAND | SCOMMAND |
|----------|----------|----------|
| Confirmed | 3 | 5 |
| Protocol-identified | 10 | 10 |
| Unknown | 34 | 29 |
| **Total** | **47** | **44** |

## Synthetic Fixtures Created

1. **command_catalog.json**: Symbolic command catalog with confirmed and protocol-identified commands
2. **lifecycle_cases.json**: Connection lifecycle test cases (CLIENT_START, CLIENT_END, timeout, error)
3. **invalid_cases.json**: Invalid input test cases (bad frame, unknown type, invalid payload)
4. **README.md**: Documentation explaining synthetic nature and usage

## Current Implementation Gaps

| Gap | Priority | Phase |
|-----|----------|-------|
| Abstract transport interface | HIGH | G17 |
| Synthetic test transport | HIGH | G17 |
| Session state machine | HIGH | G17 |
| CLIENT_START/CLIENT_END handlers | HIGH | G17 |
| Timeout handling | MEDIUM | G17 |
| Error reporting | HIGH | G17 |
| CARD_READ/WRITE/CHECK handlers | MEDIUM | G18 |
| NEWS_REQUEST/EVENT_REQUEST handlers | MEDIUM | G18 |
| LOG_UPLOAD handler | MEDIUM | G18 |
| Payload validation | MEDIUM | G18 |
| Ordering validation | MEDIUM | G18 |

## Security and Authorization Boundary

### Prohibited

- Present as NESYS service
- Authenticate to production NESYS
- Use original certificates or private keys
- Bypass certificate validation
- Impersonate vendor endpoints
- Reuse production credentials
- Claim vendor authorization
- Communicate with third-party infrastructure
- Modify Windows services or HKLM Registry
- Install as replacement for original service
- Process real customer or payment data

### Allowed

- Local isolated development
- Operator-owned hardware
- Synthetic test data
- Independently implemented protocol abstractions
- Offline unit and integration testing
- Explicit operator-controlled configuration
- No production trust relationship

## Conditions Required to Reopen Original Recovery

1. Original C-drive image becomes available
2. Authorized installer becomes available
3. Verified service configuration export becomes available
4. Vendor documentation becomes available
5. Authorized intact cabinet environment becomes available

## Whether G17 Is Justified by Confirmed Evidence

**YES**. The protocol matrix, lifecycle, and transport boundary contain enough confirmed evidence to define a meaningful synthetic G17 implementation:

- 8 confirmed commands with observable behavior
- 20 protocol-identified commands with known IDs
- Clear connection lifecycle (CLIENT_START → CLIENT_END)
- Observable error behaviors (CERT_ERROR, NW_ERROR, NWRECOVER_NOTICE)
- Abstract transport interface design
- Comprehensive test fixture definitions

## Exact Recommended G17 Scope

**Phase 2A-G17: Synthetic Transport and Protocol State-Machine Foundation**

G17 must remain:

- Offline
- Synthetic
- Test-first
- Transport-abstracted
- Non-production
- Free of certificate emulation
- Free of vendor endpoint impersonation
- Unable to contact production NESYS by default
- Unable to modify Windows services or HKLM

G17 must implement:

1. Abstract Transport interface
2. SyntheticTestTransport
3. SessionState with state machine
4. CLIENT_START/CLIENT_END handlers
5. Timeout handling
6. Error reporting (CERT_ERROR, NW_ERROR, NWRECOVER_NOTICE)
7. Comprehensive test suite

G17 must NOT implement:

1. Certificate operations
2. Network operations
3. Registry operations
4. Service operations
5. MATCH_REQUEST/CANCEL (guarded)
6. BURST_GROUP_JOIN/LEAVE (guarded)

## Confirmation of No Boundary Violations

- No service registered
- No Registry value created
- No certificate installed or exported
- No hosts or DNS modification
- No production connection
- No live named pipe created
- No original executable launched
- No original binary modified
