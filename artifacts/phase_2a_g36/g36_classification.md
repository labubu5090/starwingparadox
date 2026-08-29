# G36 Classification: TUTORIAL_COMPLETED_ONBOARDING_PASSED

## Timestamp
2026-08-29 18:30 UTC+8

## Classification
**TUTORIAL_COMPLETED_ONBOARDING_PASSED**

## Evidence Summary

### 1. Complete Game Sequence Chain
The game executed the full first-time onboarding flow:
```
Boot → Notice → SeatCheck → AdvertiseMovie → SystemDataCheck → PromotionMovie → Title
→ SystemDataCheck → PromotionMovie → Title (idle)
→ SystemDataCheck → ReadCard → BuyCredit → WarningDisp → UserDataCheck → HowToPlay
→ UserDataInput → Immersion → Introduction → FirstTimeTutorial → Battle
→ LeavedBattle → TerminatedBattle → Title (returned)
```

### 2. TCP Connection Lifecycle
| Event | Timestamp | Evidence |
|-------|-----------|----------|
| Initial disconnect | 18:05:20 | `[UAcrProtocol::Disconnect] Start Disconnect Addr:` |
| Failed ping | 18:05:20 | `Failed to post Ping : Lost Connection` |
| Connect attempt | 18:06:20 | `TryToConnect / Connect to Address[127.0.0.1:6666]` |
| Success | 18:06:20 | `Success to connect. / GetTargetAddress[127.0.0.1:6666]` |
| First pong | 18:06:20 | `OnReceivePong / WebServer Revived!` |
| Pong state | 18:06:20 | `bWebServerLive[1] bNesysServerLive[0] bNesicaReception[0]` |
| Last ping | 18:19:17 | `Ping id[59] sessionid[0]` |
| Total pings | 43 | Every 20 seconds |

### 3. NESYS Error Pattern
- **Count**: 46 occurrences
- **Message**: `Error No MatchingServer so initialize Nesys before.`
- **Frequency**: Every 20 seconds (on Ping cycle)
- **Impact**: Non-blocking - tutorial completed despite errors
- **First seen**: L128202

### 4. Tutorial Battle
- **Start**: `SetGameSequence Old:[FirstTimeTutorial] New:[Battle]`
- **End**: `RequestEndBattle (Team(TEAM_A)BattleResult:Result_Timeover_Lose InTimeOver:1)`
- **Total respawns**: 51
- **Return to Title**: `SetGameSequence Old:[LeavedBattle] New:[Title] Req:[TerminatedBattle]`

### 5. Credit Flow
| Event | Credit |
|-------|--------|
| Initial | 0,0,0,0 |
| After BuyCredit | 1,0,0,1 |
| After Z/Z | 2,0,0,2 |
| After Battle | 1,0,0,1 |

### 6. Save Data
- **OpenKey.json**: Exists (96 bytes), unchanged
- **SaveData.json**: Exists (3771 bytes) - master data metadata only
- **New player save files**: None
- **Conclusion**: No player-specific save data created

### 7. Keyboard Controls
| Action | Key |
|--------|-----|
| Forward | W |
| Left | A |
| Right | D |
| Backward | S |
| Jump | Space |
| Dash | LShift |
| Attack L | Q |
| Attack R | E |
| AR Skill | F |
| Weapon Change | MMB |
| Step | LCtrl |
| Start | Enter |
| Debug Credit | Z |

## Next Blocker
**NESYS_PROTOCOL_MISSING**
- Game sends NESYS initialization request every 20s
- Our TCP server only responds to Ping/Pong
- MatchingServer not initialized (bNesysServerLive[0])
- Non-blocking for tutorial, may block online features

## Key Findings
1. **Full onboarding flow works** - All 22 game sequences execute correctly
2. **TCP Ping/Pong is stable** - 43 pings, all received Pong responses
3. **Tutorial completes** - Battle ends with Timeover_Lose, returns to Title
4. **No player save data** - Tutorial completion not persisted locally
5. **NESYS protocol missing** - 46 errors but non-blocking
6. **Controller mapper functional** - XInput detected, keyboard output working

## Classification Rationale
The game successfully completed the full first-time onboarding flow:
- Reached and played tutorial battle
- TCP connection stable with Ping/Pong working
- Returned to Title after tutorial completion
- All critical paths functional for single-player operation
