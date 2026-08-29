# Phase 2A G36 Final Report

## Classification

**TUTORIAL_COMPLETED_ONBOARDING_PASSED**

## Summary

Game launched successfully with proven INI config path. TCP connection established and stable with Ping/Pong (43 pings, all received Pong). Full first-time onboarding flow completed: Boot → Notice → SeatCheck → AdvertiseMovie → SystemDataCheck → PromotionMovie → Title → ReadCard → BuyCredit → WarningDisp → UserDataCheck → HowToPlay → UserDataInput → Immersion → Introduction → FirstTimeTutorial → Battle → LeavedBattle → TerminatedBattle → Title. Tutorial battle ended with Timeover_Lose, game returned to Title. No new player save data created. NESYS errors (46) non-blocking.

## Runtime Confirmation

### INI Config Path (reproduced from G34/G35)

```
L109985: FAcrNetworkConfig::Init / port[7777]
L109989: MatchingServer : 127.0.0.1:6666 (UseConfigMatchingServer : 1)
L110003: Decide connect type INI file address
```

### Complete Game Sequence Chain

| Step | From | To | Timestamp | Notes |
|------|------|----|-----------|-------|
| 1 | Boot | Notice | 18:05:15 | Startup |
| 2 | Notice | SeatCheck | 18:05:20 | |
| 3 | SeatCheck | AdvertiseMovie | 18:05:20 | |
| 4 | AdvertiseMovie | SystemDataCheck | 18:05:20 | |
| 5 | SystemDataCheck | PromotionMovie | 18:05:20 | |
| 6 | PromotionMovie | Title | 18:06:15 | First idle |
| 7 | Title | SystemDataCheck | 18:06:31 | After idle |
| 8 | SystemDataCheck | PromotionMovie | 18:06:31 | |
| 9 | PromotionMovie | Title | 18:07:11 | Second idle |
| 10 | Title | SystemDataCheck | 18:07:14 | After Z/Z/Enter |
| 11 | SystemDataCheck | ReadCard | 18:07:14 | |
| 12 | ReadCard | BuyCredit | 18:07:15 | 1 credit consumed |
| 13 | BuyCredit | WarningDisp | 18:07:16 | |
| 14 | WarningDisp | UserDataCheck | 18:07:18 | |
| 15 | UserDataCheck | HowToPlay | 18:07:35 | |
| 16 | HowToPlay | UserDataInput | 18:07:37 | |
| 17 | UserDataInput | Immersion | 18:07:38 | |
| 18 | Immersion | Introduction | 18:07:38 | |
| 19 | Introduction | FirstTimeTutorial | 18:07:47 | |
| 20 | FirstTimeTutorial | Battle | 18:07:48 | Tutorial battle starts |
| 21 | Battle | LeavedBattle | 18:17:34 | Timeover_Lose |
| 22 | LeavedBattle | Title | 18:17:44 | Tutorial complete |

### TCP Connection Lifecycle

| Event | Timestamp | Line | Evidence |
|-------|-----------|------|----------|
| Initial disconnect | 18:05:20 | L109982 | `[UAcrProtocol::Disconnect] Start Disconnect Addr:` |
| Failed ping | 18:05:20 | L110007 | `Failed to post Ping : Lost Connection` |
| Connect attempt | 18:06:20 | L110652 | `TryToConnect / Connect to Address[127.0.0.1:6666]` |
| Success | 18:06:20 | L110657 | `Success to connect. / GetTargetAddress[127.0.0.1:6666]` |
| First pong | 18:06:20 | L110662 | `OnReceivePong / WebServer Revived!` |
| Pong state | 18:06:20 | L110663 | `bWebServerLive[1] bNesysServerLive[0] bNesicaReception[0] bLiveFromTestmode[1] bLiveFromGame[1] bGameConnect[0] bHttpSuccess[1]` |
| Last ping | 18:19:17 | — | `Ping id[59] sessionid[0]` |
| Total pings | — | — | 43 (every 20 seconds) |

### NESYS Error Pattern

- **Count**: 46 occurrences
- **Message**: `Error No MatchingServer so initialize Nesys before.`
- **Frequency**: Every 20 seconds (on Ping cycle)
- **First seen**: L128202 (18:13:53)
- **Impact**: Non-blocking - tutorial completed despite errors

### Tutorial Battle

- **Start**: `SetGameSequence Old:[FirstTimeTutorial] New:[Battle]` (L120596)
- **End**: `RequestEndBattle (Team(TEAM_A)BattleResult:Result_Timeover_Lose InTimeOver:1)` (L128358)
- **Duration**: ~10 minutes (18:07:48 to 18:17:34)
- **Total respawns**: 51
- **Return to Title**: `SetGameSequence Old:[LeavedBattle] New:[Title] Req:[TerminatedBattle]` (L131309)

### Credit Flow

| Event | Total | Debug | Action |
|-------|-------|-------|--------|
| Initial | 0,0,0,0 | 0 | — |
| After BuyCredit | 1,0,0,1 | 0 | Consumed for onboarding |
| After Z/Z | 2,0,0,2 | 2 | Debug credits added |
| After Battle | 1,0,0,1 | 1 | Credit consumed |

### Save Data

- **OpenKey.json**: Exists (96 bytes), unchanged
- **SaveData.json**: Exists (3771 bytes) - master data metadata only (CSV file list)
- **New player save files**: None
- **Conclusion**: No player-specific save data created. Tutorial completion not persisted to local storage.

### Keyboard Controls

| Action | Key | Notes |
|--------|-----|-------|
| Forward | W | |
| Left | A | |
| Right | D | |
| Backward | S | |
| Jump | Space | |
| Dash | LShift | |
| Attack L | Q | LButton equivalent |
| Attack R | E | RButton equivalent |
| AR Skill | F | |
| Weapon Change | MMB | Middle mouse button |
| Step | LCtrl | |
| Start | Enter | |
| Debug Credit | Z | |

## Key Findings

1. **Full onboarding flow works** — All 22 game sequences execute correctly from Boot to Title.
2. **TCP Ping/Pong is stable** — 43 pings, all received Pong responses. Connection maintained throughout.
3. **Tutorial completes** — Battle ends with Timeover_Lose, returns to Title. No network dependency.
4. **No player save data** — Tutorial completion not persisted locally. Game treats each session as fresh.
5. **NESYS protocol missing** — 46 errors but non-blocking. `bNesysServerLive[0]` throughout.
6. **Controller mapper functional** — XInput detected, keyboard output working.

## Blocker Analysis

### Current Blocker: NESYS_PROTOCOL_MISSING

The game sends NESYS initialization requests every 20 seconds (`Error No MatchingServer so initialize Nesys before.`). Our TCP server only responds to Ping/Pong. This is non-blocking for single-player tutorial but may block online features (matching, rankings, etc.).

### Next Implementation

1. **Implement NESYS protocol** — Respond to NESYS initialization handshake in TCP server
2. **Test post-tutorial matching** — After tutorial, test if game requests matching
3. **Implement save data persistence** — Determine what save data fields control onboarding state
4. **Test re-launch persistence** — Check if tutorial completion persists across sessions

## Quality Gates

| Gate | Result |
|------|--------|
| Game launch | PASS |
| INI config path | PASS (Decide connect type INI file address) |
| TCP connection | PASS (Success to connect) |
| Ping/Pong | PASS (43 pings, all Pong) |
| Onboarding flow | PASS (all 22 sequences) |
| Tutorial battle | PASS (completes with Timeover_Lose) |
| Return to Title | PASS (TerminatedBattle → Title) |
| NESYS errors | NON-BLOCKING (46 errors, tutorial completes) |
| No fabricated data | PASS |
| No NESYS pipe mock | PASS |
| No fake player identities | PASS |

## Artifacts

| Artifact | Path |
|----------|------|
| G36 Decision | artifacts/phase_2a_g36/g36_decision.json |
| G36 Classification | artifacts/phase_2a_g36/g36_classification.md |
| Runtime Timeline | artifacts/phase_2a_g36/runtime_timeline.json |
| G36 Final Report | docs/PHASE_2A_G36_FINAL_REPORT.md |
