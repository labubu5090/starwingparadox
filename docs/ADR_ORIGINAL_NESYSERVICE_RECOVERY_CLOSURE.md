# ADR: Original NesysService Recovery Closure

**Date**: 2026-08-28
**Phase**: 2A-G16
**Workstream**: J
**Status**: ACCEPTED

## Question

Should the project continue trying to restore the original NesysService installation from the D-drive backup?

## Decision

No, not with the currently available evidence.

## Rationale

### Evidence Limitations

| Evidence | Status | Impact |
|----------|--------|--------|
| Original C-drive | ABSENT | Cannot reconstruct service registration |
| Installer package | ABSENT | Cannot reinstall service |
| Recovery image | ABSENT | Cannot restore system |
| Service registration evidence | ABSENT | Cannot determine configuration |
| Registry provisioning | ABSENT | Cannot determine defaults |
| Certificate provisioning | ABSENT | Cannot install certificates |
| Startup orchestration | ABSENT | Cannot determine launch sequence |
| Safe registration | FALSE | Cannot safely register service |

### G15 Investigation Results

| Finding | Count | Impact |
|---------|-------|--------|
| Deployment artifacts found | 0 | No scripts, installers, or recovery images |
| Installer candidates | 0 | No installation media |
| Recovery candidates | 0 | No system images |
| Service registration evidence | 0 | No configuration data |
| Registry provisioning evidence | 0 | No default values |
| Startup orchestration evidence | 0 | No launch configuration |
| Recovery sources available | 1 | D-drive backup only (incomplete) |
| Recovery sources NOT_FOUND | 11 | All critical sources missing |

### Safety Assessment

| Criterion | Status | Risk |
|-----------|--------|------|
| Service account | UNKNOWN | HIGH - wrong account prevents start |
| Certificate identity | PARTIAL | HIGH - wrong cert prevents auth |
| Private key | NOT_SHOWN | HIGH - no key prevents auth |
| Registry defaults | NOT_SHOWN | MEDIUM - missing values may cause failure |
| Service dependencies | NOT_SHOWN | MEDIUM - missing deps may cause failure |
| Failure actions | NOT_SHOWN | MEDIUM - no recovery on failure |
| Service SID type | NOT_SHOWN | LOW - may cause isolation issues |
| Preshutdown timeout | NOT_SHOWN | LOW - may cause shutdown issues |

## Consequences

### Positive Consequences

1. **No speculative service registration** - Prevents system mutation
2. **No guessed Registry provisioning** - Prevents configuration errors
3. **No certificate reconstruction** - Prevents security issues
4. **Independently implemented compatibility may continue** - Within documented boundary
5. **Recovery branch may reopen** - When legitimate new evidence becomes available

### Negative Consequences

1. **Original runtime recovery impossible** - Cannot restore original service
2. **NESYS offline block persists** - Cannot resolve without service
3. **Card play unavailable** - Requires NESYS service
4. **Full compatibility not achievable** - Cannot match original behavior exactly

### Neutral Consequences

1. **Clean-room implementation justified** - Independent approach warranted
2. **Synthetic testing enabled** - Can test without original service
3. **Protocol abstraction possible** - Can implement compatible interface
4. **Authorization boundary established** - Clear security constraints

## Alternatives Considered

### Alternative 1: Speculative Service Registration

| Pros | Cons |
|------|------|
| Might work | HIGH risk of system mutation |
| Quick attempt | Unknown service account |
| Uses recovered evidence | Missing certificate |
| | Missing registry defaults |
| | Missing startup config |

**Rejected**: Too many unknowns, HIGH risk of system mutation.

### Alternative 2: Certificate Synthesis

| Pros | Cons |
|------|------|
| Might authenticate | FORBIDDEN - security boundary |
| Uses store path evidence | FORBIDDEN - vendor impersonation |
| | FORBIDDEN - production endpoint |
| | FORBIDDEN - credential misuse |

**Rejected**: Violates security and authorization boundary.

### Alternative 3: Registry Guessing

| Pros | Cons |
|------|------|
| Might configure service | HIGH risk of wrong values |
| Uses value names evidence | Missing defaults |
| Quick attempt | Unknown ranges |
| | Unknown behavior on wrong values |

**Rejected**: Too many unknowns, HIGH risk of configuration errors.

### Alternative 4: Clean-room Implementation (Selected)

| Pros | Cons |
|------|------|
| No system mutation | Cannot match original exactly |
| No security boundary violations | NESYS offline block persists |
| Synthetic testing possible | Card play unavailable |
| Independent implementation | Requires protocol reverse engineering |
| Recoverable when evidence available | Longer implementation time |

**Selected**: Safest approach, within authorization boundary, allows progress.

## Conditions for Reopening

The recovery branch may be reopened ONLY when:

1. **Original C-drive image** becomes available
2. **Authorized installer** becomes available
3. **Verified service configuration export** becomes available
4. **Vendor documentation** becomes available
5. **Authorized intact cabinet environment** becomes available

## Review

| Reviewer | Date | Status |
|----------|------|--------|
| Evidence matrix | 2026-08-28 | COMPLETE |
| Safety assessment | 2026-08-28 | COMPLETE |
| Boundary review | 2026-08-28 | COMPLETE |
| Decision record | 2026-08-28 | COMPLETE |
