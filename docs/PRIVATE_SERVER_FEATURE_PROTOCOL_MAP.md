# PRIVATE_SERVER_FEATURE_PROTOCOL_MAP

## Status

**Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION
(see eligibility note — evidence is sufficient to *proceed*, not necessarily finalize each feature without capture)

## Feature → Protocol Mapping

### Game Startup & Configuration — HTTP
Evidence: `OpenKeyCheck.cpp`, `option.txt`, `SaveData.json`, `CreateProcessW`.
Priority: HIGH. Eligibility: ELIGIBLE_WITH_CAVEATS (validate existing HTTP routes against observed game behavior).

### Player / Card Session — NESYS pipe (local adapter)
Evidence: `CallbackNesysCompleteCardStatus`, `RequestNesysCompleteCardIncert/Reissue/Status`.
Priority: HIGH. Eligibility: BLOCKED_BY_LOCAL_ADAPTER_EVIDENCE (pipe role unresolved).

### Matching — HTTP + TCP
Evidence: `BindHttpMatchingServer`, `OnReceiveMatchingServer`, `[Client->Gameserver]EntryMatching/CancelMatching/ReMatching`, `CPP_MatchingMain.cpp`.
Priority: HIGH. Eligibility: CONDITIONAL (confirm frames via capture).

### Battle Coordination — TCP
Evidence: `EntryBurst`, `ChangeBurstMode`, `CancelBurst`, `BurstUpdate`, `BurstRejectPlayer`, `BurstSelect`, `BattleProgressRecord.cpp`.
Priority: MEDIUM. Eligibility: NOT_ELIGIBLE_UNTIL_TCP_EXCHANGE_EVIDENCE.

### Result Submission — HTTP
Evidence: `BindHttpFestResult`, `ServerSetRepScoreValueBattleResult`, `CPP_BattleRecordData.cpp`, `CPP_BattleScoreData.cpp`.
Priority: MEDIUM. Eligibility: CONDITIONAL.

### Error Handling & Reconnection — HTTP + NESYS
Evidence: `BindHttpErrorCallback`, `WebServerError`, `NG_Timeout`, `DelegateReconnect`, `RequestNesysReconnect`, `CPP_GameModeDisConnect.cpp`.
Priority: HIGH. Eligibility: CONDITIONAL.

### NESYS Communication — local pipe (adapter)
Evidence: pipe primitives + `nesys_games`, `CPP_TestNesys.cpp`.
Priority: LOW. Eligibility: sees above (blocked).

## Protocol Classification

- **HTTP:** FastAPI server. Priority HIGH (matching, game data, fest result, error callback).
- **TCP:** TCP server with protobuf + 4-byte LE length prefix. Priority MEDIUM.
- **NESYS pipe:** Local adapter. Priority LOW.

## Implementation Roadmap (proposed, gated on evidence)

1. Game startup/config (HTTP) — HIGH
2. Player/card session — HIGH
3. Matching — HIGH
4. Battle coordination — MEDIUM
5. Result submission — MEDIUM
6. Error handling/reconnection — HIGH

## Important Eligibility Distinction

The artifact `feature_protocol_map.json` labels features "SUFFICIENT_EVIDENCE_TO_IMPLEMENT".
Per strict G19 rules, matching/battle/result are NOT fully complete until all three hold from
game-side evidence: (1) confirmed client request, (2) required server response,
(3) state advancement. String-level evidence confirms intent/names but not packet contracts,
so these features are CONDITIONAL / NOT_ELIGIBLE_UNTIL_EVIDENCE rather than fully confirmed.

## References

- `artifacts/phase_2a_g19/feature_protocol_map.json`
- `artifacts/phase_2a_g19/implementation_eligibility.json`
- `artifacts/phase_2a_g19/private_server_gap_map.json`
