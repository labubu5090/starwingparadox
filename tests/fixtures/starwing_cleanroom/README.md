# Starwing Clean-room Test Fixtures

**Date**: 2026-08-28
**Phase**: 2A-G16
**Status**: COMPLETE

## Overview

This directory contains inert, synthetic, non-production test fixtures representing only confirmed interface facts for the Starwing Paradox NESYS protocol.

## Important Notices

1. **Fixtures are synthetic** — They do not contain real production data
2. **Fixtures are derived only from confirmed interface observations** — No speculation or invention
3. **Fixtures must not be treated as original production traffic** — They are test data only
4. **Fixtures contain no authentication material** — No credentials, certificates, or private keys
5. **Fixtures must not be used against external systems** — Local testing only
6. **Fixtures do not include captured credentials** — All data is synthetic
7. **Fixtures do not include certificate material** — No certificate files included
8. **Fixtures do not include private identifiers** — No personal or system identifiers
9. **Fixtures do not include production hostnames** — No network endpoints included
10. **Fixtures do not include copied proprietary traffic payloads** — All payloads are empty or synthetic

## Fixture Files

### command_catalog.json

Symbolic command catalog with confirmed and protocol-identified commands. Contains:
- Confirmed commands (3 LCOMMAND, 5 SCOMMAND)
- Protocol-identified commands (10 LCOMMAND, 10 SCOMMAND)
- Command metadata (direction, confidence, clean-room eligibility)

### lifecycle_cases.json

Connection lifecycle test cases. Contains:
- Successful connection lifecycle (CLIENT_START → CLIENT_END)
- Timeout scenarios
- Error scenarios (certificate error, network error)
- Recovery scenarios (network recovery)

### invalid_cases.json

Invalid input test cases. Contains:
- Bad frame length cases
- Unknown message type cases
- Invalid payload cases
- Ordering violations

## Usage

These fixtures are designed for:

1. **Unit testing** — Test protocol parsing and state machine
2. **Integration testing** — Test synthetic transport behavior
3. **Validation testing** — Test error handling and edge cases
4. **Regression testing** — Ensure protocol compatibility

## Restrictions

These fixtures must NOT be used for:

1. **Production testing** — No live systems
2. **Network testing** — No outbound connections
3. **Authentication testing** — No credential material
4. **Certificate testing** — No certificate material
5. **External system testing** — No third-party systems

## Evidence Source

All fixtures are derived from:

1. G12-G15 evidence documents
2. G13 protocol analysis
3. Binary import analysis
4. Runtime log analysis

No production traffic, credentials, or certificate material was used.
