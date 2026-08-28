# GAME_SIDE_COMMAND_DISPATCH

## Status

**Classification:** PARTIAL_EVIDENCE (name-level protocol identification confirmed; numeric IDs/payloads open)

## HTTP Endpoints (via NetworkModule)

| Name | Purpose | Confidence |
|------|---------|------------|
| `BindHttpMatchingMatchIdGenerate` | Generate match ID | HIGH (name) |
| `BindHttpMatchingServer` | Connect to matching server | HIGH (name) |
| `BindHttpGameDataSaveData` | Save game data | HIGH (name) |
| `BindHttpFestResult` | Submit festival result | HIGH (name) |
| `BindHttpErrorCallback` | HTTP error callback | HIGH (name) |
| `TestHttpMatchingMatchIdGenerate` | Test match ID gen | HIGH (name) |
| `TestHttpMatchingServer` | Test matching server | HIGH (name) |

Fixed URLs: `https://log.starwing.jp/acr/public/` (log, production), `dev.starwing.jp/mock` (mock).

## TCP Commands (via WS2_32)

### Client -> GameServer (matching/battle)
- `[Client->Gameserver]EntryMatching`
- `[Client->Gameserver]CancelMatching`
- `[Client->Gameserver]ReMatching`
- `[Client->Gameserver]EntryBurst`
- `[Client->Gameserver]ChangeBurstMode`
- `[Client->Gameserver]CancelBurst`
- `[Client->Gameserver]BurstUpdate`
- `[Client->Gameserver]BurstRejectPlayer`
- `[Client->Gameserver]BurstSelect`

### Dedicated -> GameServer
- `[Dedicated->GameServer]UpdateDedicatedServerState`
- `[Dedicated->GameServer]MatchLeave`
- `[Dedicated->GameServer]MatchClosed`
- `[Dedicated->GameServer]MatchOpen`
- `[Dedicated->GameServer]MatchChangeState`

## NESYS Commands (pipe)

### Card operations
- `TestNesysCardRead`
- `CallbackNesysCompleteCardStatus`
- `RequestNesysCompleteCardIncert`
- `RequestNesysCompleteCardReissue`
- `RequestNesysCompleteCardStatus`

### Control / reconnect
- `CallbackNesysControlComplete`
- `RequestNesysCompetitionSupportTicket`
- `RequestNesysReconnect` / `UCPP_NesysControl::RequestNesysReconnect`

## Error Handling

- `BindHttpErrorCallback`, `WebServerError`, `NG_Timeout`
- `DelegateReconnect`, and from `CPP_GameModeDisConnect.cpp`:
  `"Disconnect GameServer. Try to Reconnect!"`

## Dispatch Patterns

- `Bind*` — HTTP endpoint binding
- `Test*` — test-mode endpoints
- `Callback*` — async callback handlers
- `Request*` — request initiators
- `[Client->Gameserver]*` / `[Dedicated->GameServer]*` — TCP command families

## Serialization

- Protobuf confirmed present (`libprotobuf` include path in binary strings).
- Framing: 4-byte uint32 LE length prefix + protobuf (prior G8/G17 confirm).

## Unknowns

- Exact HTTP request/response JSON
- TCP packet framing and payload structures (beyond length prefix)
- NESYS pipe message format
- TCP command numeric IDs
- Protobuf message definitions
- State machine transitions

## References

- `artifacts/phase_2a_g19/game_command_dispatch.json`
- `artifacts/phase_2a_g19/command_status_91.json`
