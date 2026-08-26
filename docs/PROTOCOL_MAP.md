# Starwing Paradox - Protocol Buffer Message Map

> Source: `legacy-js/js/starwingMessage.proto` (390 lines)

## Envelope: PbMessage

```protobuf
message PbMessage {
    int64 packetId = 1;
    int64 messageType = 2;
    optional int64 sessionId = 3;
    oneof Message { ... }
}
```

All messages are wrapped in `PbMessage`. The `messageType` field determines which sub-message is present. The `oneof Message` field maps `messageType` values to specific message types.

## Wire Format

```
[4 bytes: uint32 LE length of protobuf payload][protobuf-encoded PbMessage]
```

Implemented in `PbSendPayload()` (`starwing.js:62-78`).

---

## oneof Message Mapping

| messageType (dec) | messageType (hex) | Message Name | Direction | Status |
|-------------------|-------------------|--------------|-----------|--------|
| 101 | 0x65 | NotifyPushMessage | Server->Client | Defined but unused |
| 102 | 0x66 | Ping | Bidirectional | Implemented |
| 103 | 0x67 | Ping (response) | Server->Client | Implemented |
| 200 | 0xC8 | RequestEntryMatching | Client->Server | Implemented |
| 201 | 0xC9 | ResponseEntryMatching | Server->Client | Implemented |
| 202 | 0xCA | RequestCancelMatching | Client->Server | Mapped to NotifyMatchBegin (misuse) |
| 204 | 0xCC | NotifyMatchFailure | Server->Client | Defined, unused |
| 205 | 0xCD | ResponseEntryReMatching | Server->Client | Mapped to ResponseEntryMatching |
| 206 | 0xCE | RequestJoinMatching | Client->Server | Mapped to NotifyMatchEscape (misuse) |
| 208 | 0xD0 | RequestEntryBurstGroup | Client->Server | Implemented |
| 209 | 0xD1 | ResponseEntryBurstGroup | Server->Client | Implemented |
| 210 | 0xD2 | RequestChangeBurstGroupMode | Client->Server | Implemented |
| 211 | 0xD3 | ResponseChangeBurstGroupMode | Server->Client | Implemented |
| 214 | 0xD6 | RequestUpdateBurstGroup | Client->Server | Implemented |
| 215 | 0xD7 | ResponseUpdateBurstGroup | Server->Client | Implemented |
| 216 | 0xD8 | RequestBurstGroupSelect | Client->Server | Implemented |
| 217 | 0xD9 | ResponseBurstGroupSelect | Server->Client | Implemented |
| 302 | 0x12E | NotifyMatchMade | Server->Client | Implemented |
| 304 | 0x130 | NotifyMatchBegin | Server->Client | Implemented |
| 307 | 0x133 | NotifyBurstGroupUpdated | Server->Client | Implemented |
| 308 | 0x134 | NotifyBurstGroupApply | Server->Client | Implemented |
| 310 | 0x136 | NotifyBurstMade | Server->Client | Implemented (commented out in main switch) |
| 311 | 0x137 | NotifyBurstMeets | Server->Client | Implemented (in burstMode.js) |
| 601 | 0x259 | NotifyMatchOpen | Server->Client | Defined, unused |

---

## Message Definitions

### Ping (0x66)
- **Direction**: Bidirectional
- **Trigger**: Keep-alive from cabinet
- **Handler**: `starwing.js:118-123`
- **Fields**:
  - `int64 unixTimestamp = 1`
- **Response**: messageType 0x67, echoes current server timestamp

### RequestEntryMatching (200)
- **Direction**: Client->Server
- **Trigger**: Cabinet requests to join a match (100-yen mode)
- **Handler**: `starwing.js:222-294`
- **Fields**:
  - `int64 UserId = 1`
  - `int64 MacAddress = 2`
  - `int64 CardId = 3`
  - `string GameVersion = 4`
  - `uint32 LocationId = 5`
  - `string LocationName = 6`
  - `optional int32 PlayMode = 7`
  - `optional uint32 Difficulty = 8`
  - `optional int64 CoopModeIndex = 9`
  - `optional int64 OfficialType = 10`
  - `optional int32 MatchMode = 11`
  - `optional bool NotIntrude = 12`
  - `optional bool Tournament = 13`
  - `optional bool Event = 14`
  - `optional int32 EventGroupId = 15`
  - `optional uint32 EventGroupTeam = 16`
  - `optional uint32 EventGroupSeat = 17`
  - `optional uint32 StageId = 18`
  - `optional bool EventManager = 19`
  - `optional int32 EventPlayerNum = 20`
  - `optional int64 BurstGroupId = 21`
  - `optional uint32 BurstNum = 22`
  - `optional int32 StageMode = 23`
  - `optional uint32 EventRuleId = 24`
  - `optional int32 GameMode = 25`
- **Response sequence**: ResponseEntryMatching (201) -> NotifyMatchMade (302) -> NotifyMatchBegin (304)
- **Note**: Returns hardcoded fake match with VsCPU=true

### ResponseEntryMatching (201)
- **Direction**: Server->Client
- **Fields**:
  - `int64 messageId = 1`
  - `int64 timeout = 2`

### NotifyMatchMade (302)
- **Direction**: Server->Client
- **Fields**:
  - `Match Match = 1`
  - `DedicatedServer ds = 2`
  - `optional int32 MatchType = 3`
  - `optional int32 GameMode = 4`
  - `optional uint32 StageId = 5`
- **Note**: Contains hardcoded fake match data with two test players

### NotifyMatchBegin (304)
- **Direction**: Server->Client
- **Fields**:
  - `int64 MatchId = 1`

### RequestEntryBurstGroup (208)
- **Direction**: Client->Server
- **Trigger**: Cabinet registers for co-op (burst) mode
- **Handler**: `burstMode.js:158-209`
- **Fields**:
  - `optional int64 PlayerId = 1`
  - `optional int64 MacAddress = 2`
  - `optional int64 CardId = 3`
  - `optional string Version = 4`
  - `optional uint32 LocationId = 5`
  - `optional string LocationName = 6`
  - `optional int32 PlayMode = 7`
  - `optional int32 Mode = 8`
  - `optional string PlayerName = 9`
  - `optional uint32 PlayerRank = 10`
  - `optional int64 TitleId = 11`
  - `optional Emblem Emblem = 12`
  - `optional int32 BurstMode = 13`
  - `optional uint32 Rank2on2 = 14`
  - `optional int64 TitleId2on2 = 15`
  - `optional Emblem Emblem2on2 = 16`
  - `optional int32 GameMode = 17`

### ResponseEntryBurstGroup (209)
- **Direction**: Server->Client
- **Fields**:
  - `optional int64 MessageId = 1`
  - `optional int64 Timeout = 2`
  - `optional uint32 BurstNumMax = 3`

### RequestChangeBurstGroupMode (210)
- **Direction**: Client->Server
- **Trigger**: Cabinet creates a new co-op room
- **Handler**: `burstMode.js:110-157`
- **Fields**:
  - `optional int64 PlayerId = 1`
  - `optional int64 Mode = 2`
  - `optional uint32 StageId = 3`

### ResponseChangeBurstGroupMode (211)
- **Direction**: Server->Client
- **Fields**:
  - `optional int64 MessageId = 1`
  - `optional int32 Result = 2`
  - `repeated BurstPlayer Player = 3`
  - `optional uint32 StageId = 4`

### RequestUpdateBurstGroup (214)
- **Direction**: Client->Server
- **Trigger**: Cabinet requests list of co-op rooms
- **Handler**: `burstMode.js:94-108`
- **Fields**: (uses `NotifyMatchBreak` type in proto definition - likely a proto definition error)

### ResponseUpdateBurstGroup (215)
- **Direction**: Server->Client
- **Fields**:
  - `repeated BurstPlayer Player = 1`
  - `optional uint32 StageId = 2`

### RequestBurstGroupSelect (216)
- **Direction**: Client->Server
- **Trigger**: Cabinet selects/joins a co-op room from list
- **Handler**: `burstMode.js:28-92`
- **Fields**:
  - `int64 PlayerId = 1`
  - `optional int32 Mode = 2` (1=Wait)
  - `repeated int64 MateId = 3`

### ResponseBurstGroupSelect (217)
- **Direction**: Server->Client
- **Fields**:
  - `optional int64 MessageId = 1`
  - `optional int32 Result = 2`
  - `optional int64 Timeout = 3`
- **Note**: Response commented out in main switch; instead sends NotifyBurstGroupApply + NotifyBurstGroupUpdated

### NotifyBurstGroupUpdated (307)
- **Direction**: Server->Client
- **Fields**:
  - `repeated BurstPlayer Player = 1`
  - `optional uint32 StageId = 2`
- **Note**: Same as 215 but unsolicited (sent to all room members)

### NotifyBurstGroupApply (308)
- **Direction**: Server->Client
- **Fields**:
  - `repeated BurstPlayer Player = 1`

### NotifyBurstMade (310)
- **Direction**: Server->Client
- **Fields**:
  - `int64 BurstGroupId = 1`
  - `optional uint32 BurstNum = 2`
  - `repeated BurstPlayer Player = 3`
  - `optional uint32 StageId = 4`

### NotifyBurstMeets (311)
- **Direction**: Server->Client
- **Fields**:
  - `optional int32 State = 1`
  - `optional int64 BurstGroupId = 2`
  - `optional uint32 BurstNum = 3`
  - `repeated Player Player = 4`

---

## Sub-messages

### Match
- **Fields**:
  - `optional int64 MatchId = 1`
  - `optional int32 State = 2`
  - `optional int32 PlayMode = 3`
  - `optional uint32 Difficulty = 4`
  - `optional int64 CoopModeIndex = 5`
  - `optional uint32 MatchGroup = 6`
  - `repeated Team Team = 7`
  - `optional uint32 StageId = 8`
  - `optional string Version = 9`
  - `optional int32 MatchMode = 10`
  - `optional bool Tournament = 11`
  - `optional bool Event = 12`
  - `optional bool VsCPU = 13`
  - `optional int64 EndTime = 14`
  - `optional int64 StageMode = 15`
  - `optional int64 PlayZone = 16`
  - `optional int64 RuleId = 17`
  - `optional int64 GameMode = 18`

### DedicatedServer
- **Fields**:
  - `optional uint32 ServerId = 1`
  - `optional int32 State = 2`
  - `string address = 3`
  - `string version = 4`
  - `optional int64 startuptime = 5`
  - `optional string language = 6`

### Team
- **Fields**:
  - `optional uint32 PlayerCount = 1`
  - `repeated Player Player = 2`
  - `optional uint32 PinchLevel = 3`
  - `optional uint32 Force = 4`

### Player
- **Fields**:
  - `optional int64 PlayerId = 1`
  - `optional int64 MacAddress = 2`
  - `optional int64 CardId = 3`
  - `optional string PlayerName = 4`
  - `optional uint32 PlayerRank = 5`
  - `optional uint32 BuddyId = 6`
  - `optional uint32 LocationId = 7`
  - `optional string LocationName = 8`
  - `optional bool Intrude = 9`
  - `optional int64 OfficialType = 10`
  - `optional int64 BurstGroupId = 11`
  - `optional uint32 BurstNum = 12`
  - `optional uint32 Rank2on2 = 13`

### BurstPlayer
- **Fields**:
  - `optional int64 PlayerId = 1`
  - `optional int64 MacAddress = 2`
  - `optional int64 CardId = 3`
  - `optional uint32 Playmode = 4`
  - `optional uint32 Mode = 5`
  - `optional int64 Number = 6`
  - `optional string PlayerName = 7`
  - `optional uint32 PlayerRank = 8`
  - `optional int64 TitleId = 9`
  - `optional uint32 LocationId = 10`
  - `optional string LocationName = 11`
  - `optional Emblem Emblem = 12`
  - `optional uint32 MateNum = 13`
  - `optional uint32 StageId = 14`
  - `optional uint32 Rank2on2 = 15`
  - `optional int64 TitleId2on2 = 16`
  - `optional Emblem Emblem2on2 = 17`

### Emblem
- **Fields**:
  - `EmblemPart pBg = 1`
  - `EmblemPart pMa = 2`
  - `EmblemPart pSb = 3`

### EmblemPart
- **Fields**:
  - `int64 PartId = 1`
  - `Vec2 Offset = 2`
  - `Vec2 Scale = 3`
  - `double Angle = 4`

### Vec2
- **Fields**:
  - `double x = 1`
  - `double y = 2`

### NotifyPushMessage
- **Fields**:
  - `int32 Type = 1`
  - `int64 Number = 2`
  - `string Message = 3`

### IntrudePlayer
- **Fields**:
  - `uint32 TeamIndex = 1`
  - `Player Player = 2`

### Response (generic)
- **Fields**:
  - `int64 MessageId = 1`
  - `int32 Code = 2`
  - `string Message = 3`

---

## Unused/Orphan Messages

These messages are defined in the proto file but not referenced in any handler code:

| Message | Purpose (inferred) | Status |
|---------|-------------------|--------|
| RequestRegisterDedicatedServer | Dedicated server registration | Unused |
| ResponseRegisterDedicatedServer | Response to DS registration | Unused |
| NotifyUpdateDedicatedServerState | DS state change notification | Unused |
| NotifyMatchEscape | Player escapes match | Defined as type for RequestJoinMatching (0xCE) |
| NotifyMatchUpdated | Match state change | Unused |
| NotifyMatchBreak | Match terminated | Used as type for RequestUpdateBurstGroup (214) |
| NotifyMatchClosed | Match closed | Unused |
| NotifyMatchLeave | Player leaves match | Unused |
| NotifyMatchChangeState | Match state changed | Unused |
| NotifyMatchDiscontinue | Match discontinued | Unused |
| NotifyEventMatchBreak | Event match terminated | Unused |
| RequestAssignMatch | Assign match to server | Unused |
| ResponseAssignMatch | Response to match assign | Unused |
| RequestEnterMatch | Enter existing match | Unused |
| ResponseEnterMatch | Response to enter match | Unused |
| NotifyMatchFailure | Match failure | Defined as type for NotifyMatchFailure (0xCC) |
| NotifyMatchOpen | Match opened | Defined but unused |
| NotifyEventMatchBreak | Event match terminated | Unused |
| NotifyBurstRejectPlayer | Kick player from room | Unused |
| NotifyBurstMatchCancelled | Burst match cancelled | Unused |
| NotifyBurstMatchBreak | Burst match terminated | Unused |
| RequestIntrudeMatch | Intrude into match | Unused |

### Proto Definition Anomalies

1. **messageType 214** is mapped to `NotifyMatchBreak RequestUpdateBurstGroup` - the type name suggests it should be `RequestUpdateBurstGroup`, but it's aliased to the `NotifyMatchBreak` message type.
2. **messageType 206** is mapped to `NotifyMatchEscape RequestJoinMatching` - same aliasing pattern.
3. **messageType 202** is mapped to `NotifyMatchBegin RequestCancelMatching` - confusing reuse of `NotifyMatchBegin` type.
4. The `Emblem` message uses field names `pBg`, `pMa`, `pSb` but the JavaScript code accesses them as `Emblem.pBg.PartId` (line 171 of burstMode.js).
