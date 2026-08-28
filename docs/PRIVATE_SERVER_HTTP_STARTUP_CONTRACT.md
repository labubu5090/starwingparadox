# PRIVATE_SERVER_HTTP_STARTUP_CONTRACT

## Status

**Classification (G20):** HTTP_STARTUP_PAYLOAD_EVIDENCE_INSUFFICIENT

## Purpose

Define the minimum game-client-visible HTTP startup contract for an operator-owned private server
for Starwing Paradox, as recovered from static analysis of `AcrGame-Win64-Shipping.exe`. This is a
**contract definition and evidence record**, not an implementation claim.

## 1. Transport and Serialization

- **Transport:** HTTP (WININET/WINHTTP in the game client; libcurl strings also present).
- **Payload encoding:** **JSON, NOT protobuf.**
- Evidence: `CPP_HttpJsonSerialize.cpp`, `CPP_HttpJsonDifference.cpp`, `HttpGameDataLoadData` /
  `HttpGameDataLoadMissionData` JSON data symbols, and
  `http:ResponseGameDataLoad:OptionData/PlayerData/mechas success` response-section strings.
- Consequence: protobuf field-number recovery does NOT apply to the HTTP startup layer. JSON key
  names and types are the contract; they are only partially recovered.

## 2. Startup Ordering (boot gating)

- The game's `ACPP_SystemDataCheck` state machine includes an `HttpRequestWait` state.
- Advancement strings: `Request complete.` and `WaitTimer over.`
- Implication: boot progression is gated on startup HTTP request completion with a wait timer; an
  unanswered startup HTTP request blocks boot until timeout.

## 3. Recovered Route Evidence

| Route facet | Recovered | Evidence |
|-------------|-----------|----------|
| Route inventory (intent) | Yes (`BindHttp*`) | Boot, Version, Resource, MatchingServer, MatchingMatchIdGenerate, GameDataLoad, GameDataSave, PlayerLogin, PlayerRegister, PlayerProfileLoad, PlayerLogout |
| Literal URL paths | 2 of many | `/matching/match_id/generate`, `/option/save` |
| HTTP methods | No | none recovered |
| Request JSON keys | No | none recovered for startup routes |
| Response JSON schema | Partial | GameDataLoad sections: IsSuccess, PlayerData (Name/NesysID/PlayerID/CharacterCustomize/GameMode/BuddyId), OptionData, mechas, MissionsList |
| Client success condition | Partial | `IsSuccess[%d]`; OnHttpGameDataLoad / OnHttpGameDataLoadMission callbacks |
| Client state effect | Partial | `UPlayerProfileWork::ReceiveHttpGameDataLoadDelegate` |

## 4. Resource Layer

- Resource path evidence: `.resource/`, `resource.frk/`, candidate key
  `frkrfvbafwlbflahftsputavtcjc`.
- The resource is delivered as a `.frk` file; its HTTP contract is not fully recovered.

## 5. Implementation Status

- **No startup route meets the G20 implementation threshold** (confirmed path + method + request
  type + response type + fields + success condition + state effect).
- All startup routes are documented as `BLOCKED_EVIDENCE` (see
  `artifacts/phase_2a_g20/http_route_confirmation_matrix.json`).
- No payloads were fabricated.

## 6. Deferred Workstreams

- Matching TCP, battle, result submission: deferred (G20 does not implement).
- Result handling: `BindHttpFestResult`, `BindHttpGameDataSaveData` documented; missing
  requirements listed for a later phase (request/response JSON contract, retry, idempotency,
  persistence effect, client state advancement).
- NESYS pipe: `PIPE_NOT_REQUIRED_FOR_HTTP_STARTUP`; card-session pipe deferred.
- Error commands: G18 evidence-locked behavior retained.

## References

- `docs/PHASE_2A_G20_FINAL_REPORT.md`
- `artifacts/phase_2a_g20/http_route_confirmation_matrix.json`
- `artifacts/phase_2a_g20/http_startup_contract_evidence.json`
- `artifacts/phase_2a_g20/nesys_pipe_decision.json`
- `docs/PHASE_2A_G19_FINAL_REPORT.md`
