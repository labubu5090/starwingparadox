# Phase 2A-G16 Analysis Plan

**Date**: 2026-08-28
**Phase**: 2A-G16
**Title**: Original Runtime Recovery Closure and Clean-room Compatibility Boundary

## Workstreams

### Workstream A: Recovery Branch Closure
- Create formal closure record for original Windows runtime recovery branch
- State available evidence, missing evidence, searches performed, phases completed
- Recovered runtime interfaces, unresolved registration properties
- Exact conditions required to reopen recovery branch
- Conditions must be evidence-based and limited to legitimate sources

### Workstream B: Evidence Consolidation
- Consolidate G12-G15 findings into one authoritative evidence matrix
- For every item: component, claim, classification, evidence source, confidence, permitted use, prohibited inference, remaining dependency
- Classifications: CONFIRMED, HIGH_CONFIDENCE, PARTIAL, UNRESOLVED, NOT_FOUND, SYSTEM_DRIVE_REQUIRED, AUTHORIZED_INSTALLER_REQUIRED, AUTHORIZATION_BOUNDARY

### Workstream C: Correct the Startup Model
- Review previously documented "ideal startup sequence"
- Produce three separate models:
  1. CONFIRMED OBSERVED RELATIONSHIPS
  2. PLAUSIBLE BUT UNPROVEN ORIGINAL STARTUP MODEL
  3. CURRENT FAILURE MODEL
- Do not turn chronology inferred from static references into confirmed runtime chronology

### Workstream D: Clean-room Input Eligibility
- Classify every recovered observation for Python rewrite input
- Categories:
  1. ELIGIBLE_INTERFACE_FACT
  2. ELIGIBLE_FAILURE_BEHAVIOR
  3. DOCUMENTATION_ONLY
  4. RESTRICTED_SECURITY_BEHAVIOR
  5. UNKNOWN_DO_NOT_IMPLEMENT
  6. PROPRIETARY_INTERNAL_DETAIL_EXCLUDED

### Workstream E: Protocol Confidence Matrix
- Create command-level protocol confidence matrix from G13 evidence
- For all LCOMMAND and SCOMMAND values: symbolic name, direction, frame size, known fields, confidence, source reference
- Do not invent field meanings, payload values, or authentication material

### Workstream F: Offline Test Fixtures
- Create inert, synthetic, non-production test fixtures
- Permitted: symbolic command catalog, empty payloads, parser rejection cases, state-transition tests
- Mark every fixture as synthetic
- Do not include captured credentials, certificate material, or production hostnames
- Store under tests/fixtures/starwing_cleanroom/

### Workstream G: Compatibility Specification
- Create clean-room compatibility specification
- Separate: transport abstraction, command catalog, state machine, message parsing, validation, error handling, lifecycle, application adapter
- Use abstract transport interface
- Do not bind to original production pipe

### Workstream H: Implementation Gap Analysis
- Compare specification with current Python server implementation
- For each interface behavior: already implemented, partially implemented, not implemented, intentionally excluded, blocked by insufficient evidence
- Identify minimum next implementation slice

### Workstream I: Security and Authorization Boundary
- Create explicit technical boundary document
- Python rewrite must NOT: present as NESYS service, authenticate to production, use certificates, bypass validation, impersonate vendor, reuse credentials, claim authorization
- Allowed: local development, operator-owned hardware, synthetic data, protocol abstractions, offline testing

### Workstream J: Decision Record
- Create ADR answering: Should project continue trying to restore original NesysService?
- Decision: No, not with currently available evidence
- Consequences: recovery branch closed, independently implemented compatibility may continue

### Workstream K: Roadmap Rebase
- Replace old recommendation "Phase 2A-G16: Service Registration Feasibility Assessment"
- Replace with "Phase 2A-G16: Original Runtime Recovery Closure and Clean-room Compatibility Boundary"
- Recommend subsequent phase: Phase 2A-G17: Synthetic Transport and Protocol State-Machine Foundation

## Quality Gates

- Full pytest suite: 834 passed, 1 skipped, 0 failed
- Ruff: 0 errors
- Mypy: 0 errors on 64 source files
- All SHA-256 hashes unchanged
- No original binary modified
- No Registry value created
- No Windows service created
- No certificate installed or exported
- No hosts or DNS modification
- No production connection
- No live named pipe created
- No original executable launched
