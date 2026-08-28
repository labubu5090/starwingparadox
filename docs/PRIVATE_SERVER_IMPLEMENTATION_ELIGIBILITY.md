# PRIVATE_SERVER_IMPLEMENTATION_ELIGIBILITY

## Status

**Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

## Eligibility Rule

A feature is ELIGIBLE only when all three hold from game-side evidence:
(1) confirmed client request contract, (2) required server response contract,
(3) state advancement/completion behavior.

## Per-Feature Eligibility

| Feature | Client req | Server resp | State adv | Eligibility |
|---------|-----------|-------------|-----------|-------------|
| Game Startup & Config | PARTIAL | PARTIAL | PARTIAL | ELIGIBLE_WITH_CAVEATS |
| Player / Card Session | PARTIAL (pipe) | NOT_CONFIRMED | NOT_CONFIRMED | BLOCKED_BY_LOCAL_ADAPTER_EVIDENCE |
| Matching | PARTIAL | NOT_CONFIRMED | NOT_CONFIRMED | CONDITIONAL |
| Battle Coordination | PARTIAL | NOT_CONFIRMED | NOT_CONFIRMED | NOT_ELIGIBLE_UNTIL_TCP_EVIDENCE |
| Result Submission | PARTIAL | NOT_CONFIRMED | NOT_CONFIRMED | CONDITIONAL |
| Error Handling & Reconnect | PARTIAL | NOT_CONFIRMED | NOT_CONFIRMED | CONDITIONAL |
| NESYS / Card Trust | NOT_ELIGIBLE | NOT_ELIGIBLE | NOT_ELIGIBLE | EXCLUDED |

## Architecture

**Option A — Two-tier** (proxy/adapter + Python HTTP/TCP server), with a local NESYS pipe
adapter added only after pipe-role resolution. (See PRIVATE_SERVER_MINIMUM_ARCHITECTURE.md.)

Rejected: Option D (monolithic single-port — incompatible with multi-transport game client);
proxy on non-80 port; any game-executable modification.

## G20 Coding Scope (proposed)

1. Validate existing HTTP startup routes against observed game behavior (HIGH).
2. Resolve pipe role; only then build a minimal local adapter (HIGH).
3. Capture real TCP matching/battle exchanges; finalize matching HTTP/TCP (MEDIUM).
4. Confirm result-handling HTTP contract + idempotency (MEDIUM).
5. Align synthetic error handler to confirmed semantics (MEDIUM).

## Constraints (G19)

- No binary modification / endpoint redirection / certificate behavior / service registration /
  speculative protocol handlers. `legacy-js/` unchanged.

## References

- `artifacts/phase_2a_g19/implementation_eligibility.json`
- `artifacts/phase_2a_g19/private_server_gap_map.json`
