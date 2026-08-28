# PYTHON_PRIVATE_SERVER_CLIENT_GAP_MAP

## Status

**Classification:** PARTIAL_GAME_CLIENT_CONTRACT

**G20 update (Phase 2A-G20):** HTTP startup payload contract is confirmed to be **JSON, not
protobuf** (see `HTTP_STARTUP_PAYLOAD_EVIDENCE_INSUFFICIENT`). Startup routes remain
`BLOCKED_EVIDENCE` because URL paths, HTTP methods, and JSON key contracts are not recovered from
static analysis. See `artifacts/phase_2a_g20/http_route_confirmation_matrix.json`.

## Current Server Surface

- **HTTP app:** FastAPI, `127.0.0.1:4001`, routes: battle, credit, game_data, health, matching,
  mission, player, ranking, resource, tutorial, version.
- **HTTP proxy:** `127.0.0.1:80`, strips `/mock/` prefix.
- **TCP listener:** `127.0.0.1:6666`, 4-byte LE length prefix + protobuf, 1 MiB max frame.
- **Database:** SQLite-only.
- **Cleanroom:** synthetic foundation (15 modules); no production adapter.

## Feature Gaps

### Game Startup
- OpenKey validation: NOT_IMPLEMENTED (game reads OpenKey locally; server not involved).
- Master data delivery: PARTIALLY implemented (resource.py/game_data.py exist, contract unconfirmed).
- Version handshake: IMPLEMENTED_SYNTHETIC_ONLY.

### Player / Card Session
- Local pipe adapter: LOCAL_ADAPTER_REQUIRED (blocked on pipe-role evidence).
- Player session HTTP: PARTIALLY implemented (payload contract unconfirmed).

### Matching
- HTTP matching server: PARTIALLY implemented (payload unknown).
- TCP matching entry/cancel: WRONG_SEMANTICS_POTENTIAL (dispatch from synthetic evidence, not confirmed game IDs).
- Match ID generation: NOT_IMPLEMENTED.

### Battle Coordination
- Battle TCP commands: NOT_IMPLEMENTED (payload semantics unproven).
- Proto definitions: BLOCKED_PAYLOAD_UNKNOWN.

### Result Submission
- HTTP result endpoint: NOT_IMPLEMENTED (no confirmed FestResult/game-data-save contract).
- Idempotency: NOT_IMPLEMENTED.

### Error Handling & Reconnection
- HTTP error callback: PARTIALLY implemented (synthetic only).
- NESYS reconnection: NOT_IMPLEMENTED.

## Core Finding

The current server exposes listeners/handlers, but **none are confirmed to match the game's
actual contracts**. Existence of an endpoint does not equal compliance. Matching, battle, and
result are not complete merely because listeners exist.

## Required Evidence Before Completion

| Feature | Client request | Server response | State advancement |
|---------|----------------|-----------------|-------------------|
| Matching | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED |
| Battle | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED |
| Result | UNCONFIRMED | UNCONFIRMED | UNCONFIRMED |

## References

- `artifacts/phase_2a_g19/private_server_gap_map.json`
- `artifacts/phase_2a_g19/test_reconciliation.json`
