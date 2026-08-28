# PHASE_2A_G20_FINAL_REPORT

## Status

**Classification:** HTTP_STARTUP_PAYLOAD_EVIDENCE_INSUFFICIENT

**Phase title (verbatim):** Phase 2A-G20: Private-Server HTTP Startup Contract Vertical Slice

## 1. Executive Summary

G20 attempted to validate and implement the existing HTTP startup routes (`app/api/version.py`,
`resource.py`, `game_data.py`, `matching.py`) against game-side behavior recovered from static
analysis of `AcrGame-Win64-Shipping.exe`.

Two decisive findings were made:

1. **The HTTP startup layer uses JSON, not protobuf.** Static analysis recovered
   `CPP_HttpJsonSerialize.cpp`, `CPP_HttpJsonDifference.cpp`, the `HttpGameDataLoadData` /
   `HttpGameDataLoadMissionData` JSON data symbols, and the 
   `http:ResponseGameDataLoad:OptionData/PlayerData/mechas success` response-section strings.
   The protobuf `message.pb.cpp` is scoped to the TCP protocol only. Protobuf field-number
   recovery does NOT apply to the HTTP startup layer; the G20 "request/response protobuf message
   type + field numbers" requirement maps to JSON key names/types and cannot be satisfied from the
   TCP protobuf descriptor.

2. **The specific URL paths, HTTP methods, and JSON payload contracts for the startup routes are
   NOT recovered from static evidence.** Only two literal route paths exist in the binary:
   `/matching/match_id/generate` and `/option/save`. The `BindHttp<Name>` binding-function names
   (Boot/Version/Resource/MatchingServer/GameDataLoad/...) encode route intent only, not the route
   path, method, or payload.

Per the G20 implementation rule (implement only routes with confirmed path + method + request type
+ response type + fields + client success condition + client state effect; fabricating is
forbidden), **no startup route meets the implementation threshold**. Every startup route is
documented as **BLOCKED_EVIDENCE**. No original route behavior was fabricated or invented, and no
existing tested route was altered (other than the non-destructive compatibility-mode setting).

Classification is therefore `HTTP_STARTUP_PAYLOAD_EVIDENCE_INSUFFICIENT`: the startup *contract*
was partially recovered, but the *payload* evidence (paths, methods, JSON keys) is insufficient to
implement without fabrication.

## 2. Primary G20 Priority (item 1)

Validate/implement existing HTTP startup routes against game-side behavior.

**Result:** The existing routes (`POST /version`, `POST /resource`, `POST /game_data/load`,
`POST /matching/*`) remain as-delivered (legacy-gated, 1056 passing baseline). They were NOT
re-derived from fresh game evidence because the game-side path/method/JSON contract is not
recoverable from static analysis. They are retained unchanged and documented as evidence-blocked
for the game-side implementation.

## 3. Evidence Recovered (G20 static analysis)

### 3.1 Serialization: HTTP is JSON, not protobuf
- `Source/NetworkModule/Private/CPP_HttpJsonSerialize.cpp`, `CPP_HttpJsonDifference.cpp`,
  `CPP_HttpRequester.cpp`, `CPP_HttpResponseParam.cpp`, `HttpUtility.cpp`
- JSON data symbols: `HttpGameDataLoadData`, `HttpGameDataLoadMissionData`
- Response-section strings: `http:ResponseGameDataLoad:OptionData/PlayerData/mechas success`,
  `http:ResponseGameDataLoad:<%s> Error`
- Field-extraction string: `ACPP_UserDataCheckMain::HttpGameDataLoad / IsSuccess[%d] / PlayerData
  Name[%s] NesysID[%s] PlayerID[%d] CharacterCustomize.Num(%d) GameMode[%s](%d) BuddyId[%s](%d)`
- `message.pb.cpp` (protobuf) is TCP-only.

### 3.2 Literal URL paths recovered
- `/matching/match_id/generate`
- `/option/save`

### 3.3 Resource path evidence
- `.resource/`, `resource.frk/`, candidate key `frkrfvbafwlbflahftsputavtcjc`

### 3.4 Startup ordering / boot gating
- Wait state `ACPP_SystemDataCheck::HttpRequestWait` with
  `Request complete.` / `WaitTimer over.` — boot progression is gated on HTTP completion.
- Boot module: `Source/OutGameModule/Private/Boot/CPP_GameModeBoot.cpp` (`ACPP_GameModeBoot`),
  `ACPP_GameModeBoot::OnReceiveMatchingServer`.

### 3.5 Binding inventory (route intent)
- Startup-relevant: Boot, Version, Resource, MatchingServer, MatchingMatchIdGenerate,
  GameDataLoad, GameDataSave, GameDataSaveData, PlayerLogin, PlayerRegister, PlayerProfileLoad,
  PlayerLogout.
- Full inventory of `BindHttp*` callbacks recovered (Fest, Gacha, Shop, Quest, Ranking, etc.),
  all documented as name-level intent only.

## 4. Per-Route Confirmation Matrix (summary)

| Route | Path confirmed | Method | JSON payload | Success | State | Status |
|-------|----------------|--------|--------------|---------|-------|--------|
| boot | No | No | No | No | No | BLOCKED_EVIDENCE |
| version | No | No | No | No | No | BLOCKED_EVIDENCE |
| resource | No | No | No | No | No | BLOCKED_EVIDENCE |
| matching/server | No | No | No | Partial | Partial | BLOCKED_EVIDENCE |
| matching/match_id/generate | Yes (`/matching/match_id/generate`) | No | No | No | No | BLOCKED_EVIDENCE |
| game_data/load | No | No | Partial (sections) | Partial | Partial | BLOCKED_EVIDENCE |
| option/save | Yes (`/option/save`) | No | No | No | No | BLOCKED_EVIDENCE |
| game_data/save | No | No | No | No | No | BLOCKED_EVIDENCE |
| player/login | No | No | No | No | No | BLOCKED_EVIDENCE |

**Fully confirmed / implementable: 0. Blocked: 9.**

Machine-readable matrix: `artifacts/phase_2a_g20/http_route_confirmation_matrix.json`.

## 5. NESYS Pipe Decision

**PIPE_NOT_REQUIRED_FOR_HTTP_STARTUP.** The startup vertical slice is HTTP-only; the named pipe
`\\.\pipe\nesys_games` is scoped to NESYS card operations and is deferred. Pipe server/client role
remains unresolved (G19) but does not affect the HTTP startup contract. No pipe adapter built in
G20; original NesysService recovery NOT revived.

See `artifacts/phase_2a_g20/nesys_pipe_decision.json`.

## 6. Compatibility Mode (disabled by default)

Added a new, distinct operator-controlled compatibility setting:

- `private_server_compatibility_mode: bool = False` in `server/app/config.py` — **disabled by
  default**.
- Enabled only explicitly (operator / G20 tests), no endpoint redirection, no machine-level config
  change, no upstream production communication, does not claim to be the official vendor service.
- The pre-existing `legacy_compatibility_mode` (G-series legacy stub mode) is intentionally left
  unchanged to avoid weakening its existing tests and behavior; it is a separate concern.

Unit tests added in `server/tests/unit/test_config.py`:
- default is `False`
- can be enabled explicitly (`True`)

## 7. Deferred (NOT done in G20)

- Live NESYS pipe adapter; original NesysService restoration; service registration; Registry
  provisioning; certificate emulation; production auth; hosts/DNS/proxy changes; binding port 80;
  launching the original game; runtime packet capture.
- TCP matching implementation; battle implementation; result submission implementation.
- Speculative handlers; fabricated protobuf fields; fabricated JSON keys.
- Result handling: NOT implemented. `BindHttpFestResult` / `BindHttpGameDataSaveData` documented as
  deferred with missing requirements (request/response JSON contract, retry, idempotency,
  persistence effect, client state advancement).
- Error commands: G18 evidence-locked behavior retained. No lifecycle semantics assigned to
  `CERT_ERROR`/`NW_ERROR`/`NWRECOVER_NOTICE` without proof. Unknown payloads remain opaque.

## 8. Quality Gates (actual)

- **Full suite:** 1058 passed, 1 skipped, 0 failed (baseline 1056 + 2 new config tests).
- **Clean-room subset:** 222 passed, 0 failed.
- **Ruff:** All checks passed.
- **Mypy:** 0 errors.
- No tests deleted/skipped/xfailed/deselected/weakened.

## 9. Integrity (actual)

All 6 SHA-256 integrity hashes remain unchanged. No original executable modified or launched; no
debugger attached; no live named pipe created; no service/registry/certificate change; no
production endpoint contacted; no DNS/hosts change; `legacy-js/` unchanged. Game content under
`X:\StarwingParadox` untouched.

## 10. Deliverables

- Artifacts (`artifacts/phase_2a_g20/`):
  - `http_route_confirmation_matrix.json`
  - `http_startup_contract_evidence.json`
  - `nesys_pipe_decision.json`
- Code:
  - `server/app/config.py` — added `private_server_compatibility_mode` (disabled by default)
  - `server/tests/unit/test_config.py` — 2 new tests
- Docs:
  - `docs/PHASE_2A_G20_FINAL_REPORT.md` (this file)
  - `docs/PRIVATE_SERVER_HTTP_STARTUP_CONTRACT.md` (startup contract definition)
  - `docs/PYTHON_PRIVATE_SERVER_CLIENT_GAP_MAP.md` (updated with HTTP-JSON finding and BLOCKED status)
- `PROGRESS.md` — G20 section appended.

## 11. Single Commit

`docs: define Starwing private-server HTTP startup contract`
