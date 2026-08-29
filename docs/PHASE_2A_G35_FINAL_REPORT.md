# Phase 2A G35 Final Report

## Classification

**PLAYABLE_FLOW_BLOCKED_AFTER_START**

## Summary

Game launched successfully with proven INI config path. Z, Z, Enter inputs consumed. Game entered first-time onboarding flow (BuyCredit → WarningDisp → UserDataCheck → HowToPlay → UserDataInput → Immersion → Introduction → Tutorial Battle). TCP connection attempted but never established. No non-Ping frames captured. Tutorial battle runs locally with no network dependency.

## Runtime Confirmation

### INI Config Path (reproduced from G34)

```
L109993: FAcrNetworkConfig::Init / port[7777]
L109997: MatchingServer : 127.0.0.1:6666 (UseConfigMatchingServer : 1)
L110011: Decide connect type INI file address
```

### First-Time Onboarding Sequence

| Step | Sequence | Timestamp |
|------|----------|-----------|
| 1 | BuyCredit | 17:52:03 |
| 2 | WarningDisp | 17:52:03 |
| 3 | UserDataCheck | 17:52:06 |
| 4 | HowToPlay | 17:52:37 |
| 5 | UserDataInput | 17:52:41 |
| 6 | Immersion | 17:52:41 |
| 7 | Introduction | 17:52:42 |
| 8 | Tutorial Battle | 17:55:45+ |

### TCP Connection Status

| Phase | Status | Evidence |
|-------|--------|----------|
| Connect Start | OK | `UCPP_TcpThread::Connect / addr[127.0.0.1:6666]` |
| Setup Connect | OK | `UCPP_TcpThread::SetupConnect / TargetAddress[127.0.0.1:6666]` |
| Failed Ping | WARN | `Failed to post Ping : Lost Connection` |
| DNS Resolve | OK | `ResolvedAddr complete! / ResolvedAddr[127.0.0.1:6666]` |
| TCP Handshake | **STALLED** | No `TryToConnect` or `Success to connect` after DNS resolution |
| Established | **0** | No TCP connections on port 6666 |

### Credit Flow

| Event | Total | Debug | Action |
|-------|-------|-------|--------|
| Initial | 0 | 0 | — |
| ZPressed_1 | 1 | 1 | Added debug credit |
| ZPressed_2 | 2 | 2 | Added debug credit |
| CreditSubtracted | 1 | 1 | Consumed for BuyCredit |
| ZPressed_3 | 2 | 2 | Added debug credit |
| ZPressed_4 | 3 | 3 | Added debug credit |

### Post-Start UI State

- **CurrentBattleSequence**: Battle
- **BattleSequencePlayer**: E_BattlePlayer
- **BattlePlayerId**: 0
- **UserId**: -1 (no player identity)
- **Tutorial Widget**: Active (UCPP_TutorialWidgetManager::SetVisibleIngame)
- **Buddy Window**: Active (WBP_BuddyWindow_Old animations)

## Key Findings

1. **First-time onboarding is the blocker**: The game detects first-time launch and enters a local-only onboarding flow before any online matching. This flow requires no network.

2. **TCP connection stalled**: DNS resolved successfully but TCP handshake never completed. The 60-second timeout may have expired during onboarding, or the game only retries TCP at specific state transitions.

3. **Credit consumption**: 1 credit consumed for BuyCredit sequence. Additional Z presses add debug credits but don't advance the flow.

4. **Tutorial battle is local**: The tutorial runs entirely locally with UserId=-1. No network traffic occurs during tutorial.

## Blocker Analysis

The game's first-time flow requires completing onboarding (UserDataInput sets player identity) before reaching online matching. The TCP connection attempt during onboarding appears to be abandoned when the game transitions to local-only sequences.

## Next Implementation

1. **Pre-complete onboarding**: Create save data that marks onboarding as complete (UserDataCheck passed, HowToPlay shown, etc.)
2. **Or complete tutorial**: Let the tutorial finish and return to title, then test matching
3. **Fix TCP retry**: Ensure TCP connection retries after onboarding completes
4. **Investigate save data structure**: Determine what save data fields control onboarding state

## Artifacts

- `g35_runtime.log` — Full game log (123K lines, 16.5MB)
- `runtime_timeline.json` — Complete event timeline
- `tcp_frames.json` — TCP frame capture (0 frames)
- `first_non_ping_message.json` — Non-Ping message analysis (none captured)
- `response_eligibility.json` — Response contract eligibility (not eligible)
- `next_blocker.json` — Next blocker analysis
- `test_reconciliation.json` — Test reconciliation
- `safety_results.json` — Safety constraint verification
