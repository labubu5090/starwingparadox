# PHASE_2A_G19_FINAL_REPORT

## Status

**Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

## 1. Executive Summary

G19 mapped the game-client-visible contracts required for an operator-owned private server,
using the game client (Starwing Paradox executables and DLLs) as the primary source of truth.
Static PE analysis confirmed multiple independent network transports (HTTP, TCP, and local
named pipe), the module structure, the command families, and the absence of any supported
game-side endpoint override.

## 2. Objective

Determine the minimum game-client-visible contracts for startup, mandatory local IPC,
private-server connection, player/card sessions, matching, battle coordination, result
submission, and timeout/disconnect/error handling — using the game client as source of truth.

## 3. Contracts Determined

### Startup
- Launcher (AcrGame.exe) uses `CreateProcessW` to spawn the Shipping build; contributes no network.
- Shipping exe reads OpenKey + master data locally before contacting any server.
- HTTP layer (WININET/WINHTTP) + game session in NetworkModule. Startup-critical: ResidentModule (OpenKeyCheck, ErrorObserver).

### Mandatory Local IPC
- Named pipe `\\.\pipe\nesys_games` for NESYS card operations.
- Pipe role (server vs client) UNRESOLVED (game imports both ConnectNamedPipe and WaitNamedPipeA). Local adapter deferred pending control-flow.
- GALAXYIO.dll uses WinHTTP + USB for card trust, NOT the pipe.

### Private-Server Connection
- Multi-transport: HTTP (WININET), TCP (WS2_32), local pipe.
- Endpoint override: **NO_SUPPORTED_ENDPOINT_OVERRIDE_FOUND**. Hardcoded `http://dev.starwing.jp/mock` (port 80). Only operator-level hosts-file/DNS redirect works.

### Player / Card Session
- NESYS pipe path (card read/insert/reissue/status). Blocked on pipe-role resolution.

### Matching
- HTTP: `BindHttpMatchingServer`, `BindHttpMatchingMatchIdGenerate`.
- TCP: `EntryMatching`, `CancelMatching`, `ReMatching`.

### Battle Coordination
- TCP: `EntryBurst`, `ChangeBurstMode`, `CancelBurst`, `BurstUpdate`, `BurstRejectPlayer`, `BurstSelect`, plus `[Dedicated->GameServer]Match*` family.

### Result Submission
- HTTP: `BindHttpFestResult`, `BindHttpGameDataSaveData`.

### Timeout / Disconnect / Error
- HTTP: `BindHttpErrorCallback`, `WebServerError`, `NG_Timeout`, `DelegateReconnect`.
- `CPP_GameModeDisConnect.cpp`: "Disconnect GameServer. Try to Reconnect!".

## 4. Protocol and Framing

- TCP framing: 4-byte uint32 LE length prefix + protobuf (G8/G17). 1 MiB = IMPLEMENTATION_SAFETY_LIMIT. No stream decoder (no frame-boundary proof).

## 5. Command Registry (91 preserved)

- 8 confirmed/high, 20 protocol-identified/medium, 63 unknown = 91.
- G19 string analysis enumerated 29 command names (name-level identification) within the 20 protocol-identified tier; no commands promoted to confirmed; no unknowns discarded.

## 6. Quality Gates (actual)

- **Full suite:** 1056 passed, 1 skipped, 0 failed.
- **Clean-room subset:** 222 passed, 0 failed.
- **Ruff:** All checks passed (after removing 2 unused imports from G18 test files — narrow correction).
- **Mypy:** 0 errors, 80 source files.

## 7. Integrity (actual)

All 6 integrity hashes MATCH (unchanged). No original executable modified or launched; no debugger attached; no live named pipe created (`\\.\pipe\nesys_*` absent); no service/registry/certificate change; no production endpoint contacted; no DNS/hosts change beyond existing entry; `legacy-js/` unchanged.

## 8. Architecture Recommendation

**Option A** — Two-tier: transport boundary (hosts-file redirect + local HTTP proxy :80 + local TCP listener :6666) + Python private server (HTTP :4001, TCP :6666, SQLite). Local NESYS pipe adapter deferred pending pipe-role evidence.

## 9. G20 Coding Scope (proposed)

1. Validate existing HTTP startup routes against observed game behavior (HIGH).
2. Resolve pipe role; build minimal local adapter only if game requires local IPC (HIGH).
3. Capture real TCP matching/battle exchanges; finalize matching HTTP/TCP with confirmed IDs (MEDIUM).
4. Confirm result-handling HTTP contract + idempotency (MEDIUM).
5. Align synthetic error handler to confirmed semantics (MEDIUM).

## 10. Deliverables

- Artifacts (11): module_map, startup_dependency_graph, game_pipe_contract, game_command_dispatch, command_status_91, feature_protocol_map, network_endpoint_classification, private_server_gap_map, service_requirement_matrix, implementation_eligibility, test_reconciliation.
- Docs (15): IDA analysis plan, executable module map, startup dependency graph, pipe protocol, command dispatch, NESYS min-necessity, feature protocol map, endpoint classification, endpoint configuration, python server gap map, minimum architecture, service requirement matrix, implementation eligibility, initial baseline, this final report.
- Tools: pe_analysis.py + helpers + outputs in `tools/ida/`.

## 11. Interruption Recovery Note

Prior run stopped on `[404] No allowed providers` (provider-policy issue, not repo/Python/IDA/test failure). Recovery re-verified the working tree, confirmed existing G19 files (baseline doc + 6 artifacts + tools), corrected `command_status_91.json` to preserve the 8/20/63 split, created the remaining 5 artifacts and 9 docs, and completed quality + integrity gates.

## 12. Single Commit

`docs: map Starwing game client contracts for private server`
