# Phase 2A-G5R Final Report: NESYS Offline Block Root-Cause Investigation

## 1. Phase Status

**Status**: BLOCKED_BY_MISSING_NESYS_LAUNCHER

**Commit**: a69fc0c (current HEAD)

**Correction**: Previous reports incorrectly described InsertStart as a usable title state.
The game repeatedly reaches an offline/no-connection screen and cannot proceed with
card-based gameplay. This was confirmed by repeated physical runtime observation.

## 2. Network Model (Corrected)

### HTTP Game Server
- **URL**: `http://dev.starwing.jp/mock/matching/server`
- **Hosts mapping**: `dev.starwing.jp → 127.0.0.1`
- **Local proxy**: 127.0.0.1:80 → 127.0.0.1:4001 (prefix stripping)
- **Server response**: `{"ip_addr":"127.0.0.1:6666"}`
- **Status**: VERIFIED_WORKING

### NESYS Named-Pipe IPC
- **Pipe name**: `\\.\pipe\nesys_games\%s%s` (company ID + game ID)
- **Server**: NesysService.exe (NOT RUNNING)
- **Client**: AcrGame.exe (NesysClient plugin)
- **Status**: FAILED (pipe does not exist)

### Matching TCP
- **Endpoint**: 127.0.0.1:6666
- **Status**: NOT_STARTED (blocked by NESYS offline)

## 3. Hardcoded HTTP Endpoint

The game binary contains the hardcoded URL:
```
http://dev.starwing.jp/mock/matching/server
```

The game makes this HTTP request during boot. The request succeeds and returns
`{"ip_addr":"127.0.0.1:6666"}`. The game logs `_IsSuccess[1]`.

However, this HTTP success does NOT mean the game is online. The game then logs:
```
Error No MatchingServer so initialize Nesys before.
```

The game requires NESYS initialization BEFORE it will use the matching server address.

## 4. HTTP Routing Result

| Component | Status |
|-----------|--------|
| Hosts mapping | WORKING |
| Local proxy on :80 | WORKING |
| Python server on :4001 | WORKING |
| `/mock/matching/server` | Returns correct response |
| Game receives response | CONFIRMED (`_IsSuccess[1]`) |

## 5. NESYS Offline Result

### What the Game Displays
- 現在オフラインの為チェック出来ません。(Currently offline, cannot check.)
- オンラインになるまでお待ちください。(Wait until online.)
- 現在オフラインモードの為カードを使ったプレイはできません (Card play unavailable in offline mode)
- CREDIT(S) 0

### What the Game Logs
```
LogNesys: UCPP_NesysControl::RequestNetworkInfo OK.
LogNesys: UCPP_NesysControl::RequestNetworkInfo Error.
LogBoot: ACPP_GameModeBoot::NesysControlErrorMessage / ENesysNetworkServerMessage[CertError]
LogOnlineObserver: Nesys:0
LogAcrProtocol: Error No MatchingServer so initialize Nesys before.
LogAcrOutgame: ACPP_SystemDataCheck::Tick / EventRequest / UCPP_NesysControl::Get(this)->IsOnline[0]
```

### Root Cause
NesysService.exe is not running. The game's NESYS client plugin attempts to connect
to a named pipe (`\\.\pipe\nesys_games\...`) that does not exist.

## 6. Baseline Runs

### Run 1
- **Time to title**: 145s
- **Crash**: FRCPassPostProcessAA at 180s (intermittent)
- **Offline block**: Confirmed

### Run 2
- **Time to title**: ~145s
- **Crash**: None
- **Offline block**: Confirmed

Both runs display the same offline/no-connection screen.

## 7. Asset Preload

- **Assets loaded**: 5132/7553
- **Duration**: ~30s
- **Status**: COMPLETED

## 8. PromotionMovie

- **Start time**: ~145s
- **Status**: COMPLETED (plays normally)

## 9. InsertStart

- **Widget visible**: Yes
- **Overlaid by**: NESYS offline error screen
- **Status**: COMPLETED (but NOT a usable title state)

## 10. NESYS Service Analysis

### Binary Identity
- **Version**: 2.97
- **Company**: TAITO Corporation
- **PDB**: `NesysServiceCert_x64.pdb`
- **Built**: 2017/11/07

### Named Pipe Protocol
- **Prefix**: `\\.\pipe\`
- **Full name**: `\\.\pipe\nesys_games\%s%s`
- **Protocol**: LCOMMAND/SCOMMAND pairs
- **Commands**: CLIENT_START, GAME_START_REQUEST, GAME_FREE_START_REQUEST, etc.

### External Service Endpoints
| Host | Protocol | Purpose |
|------|----------|---------|
| cert3.nesys.jp | HTTPS | Certificate verification |
| data.nesys.jp | HTTP | Data downloads |
| nesys.taito.co.jp | HTTP | Alive check |
| proxy.nesys.jp | HTTPS | Proxy |
| fjm170920zero.nesica.net | HTTPS | NESICA card service |

### Why NesysService Exits Immediately
- No D: drive mounted
- No launcher with correct arguments
- No Windows certificates
- No registry configuration
- No parent process context

## 11. Required D: Drive Structure

```
D:\Saved\ACRSaved\SaveData\OpenKey.json
D:\Saved\ACRSaved\SaveData\SaveData.json
D:\Saved\ACRSaved\Ranking\RankingData.json
D:\Saved\ACRSaved\Debug\DebugSetting.json
D:\Saved\ACRSaved\TestMode\NesicaTime\NesicaTime.json
D:\Saved\ACRSaved\TestMode\System\System.json
D:\Saved\ACRSaved\TestMode\Game\Game.json
D:\system\DUA\event\system_management_*.json
```

**D: drive does not exist on this system.**

## 12. D: Drive Contents (X:\StarwingParadox\D DRIVE CONTENTS\)

The game distribution includes a backup of D: drive contents:
- `Saved\ACRSaved\SaveData\` — 120+ CSV game data files, OpenKey.json, SaveData.json
- `Saved\ACRSaved\TestMode\` — Test mode settings (System, Game, NesicaTime, etc.)
- `Saved\ACRSaved\Ranking\RankingData.json`
- `Saved\GalaxySaved\` — UE4 config files
- `system\Service\NesysService.exe` — The service binary
- `system\option.txt` — Option configuration
- `system\DUA\` — Event/news data
- `system\CmdFile\log\Log.txt` — Historical service logs (2018-2021)

## 13. Coin Input

**NOT_YET_VALID** — Cannot test coin input while game is in offline error state.

## 14. Start Input

**NOT_YET_VALID** — Cannot test start input while game is in offline error state.

## 15. Next State

The game cannot advance beyond the offline error screen without NESYS initialization.

## 16. HTTP Requests After Input

**No input possible** — game is blocked at offline screen.

## 17. TCP 6666 Activity

**No TCP connections** — matching server connection blocked by NESYS offline state.

## 18. Rendering Crash Reproduction

The `FRCPassPostProcessAA::Process()` crash is **intermittent**:
- Run 1: Crashed at 180s
- Run 2: No crash

Classification: **INTERMITTENT**

The crash is secondary to the NESYS offline block.

## 19. Rendering Workaround

**NOT APPLIED** — crash did not reproduce consistently, and NESYS is the primary blocker.

## 20. Offline Mode Limit

The game is permanently blocked in offline mode. Without NESYS:
- Card-based gameplay unavailable
- Normal game flow not reached
- Coin/start cannot be validated
- Matching cannot be attempted
- Battle cannot be attempted

## 21. Matching Guard

**ACTIVE** — matching endpoint returns 501 NOT_IMPLEMENTED.

## 22. Battle Guard

**ACTIVE** — battle endpoint returns 501 NOT_IMPLEMENTED.

## 23. Tests

```
794 passed, 2 failed (pre-existing), 6 skipped
```

## 24. Ruff

0 errors.

## 25. Mypy

0 errors.

## 26. Original Game Files Changed

**NONE** — no files under `X:\StarwingParadox` modified.

## 27. Correction Notice

Previous G4 reports incorrectly described InsertStart as a usable title state waiting
normally for coin/start input. This was disproven by repeated physical runtime observation.
The game reaches an offline/no-connection screen and cannot proceed.

See: `docs/NESYS_OFFLINE_BLOCK_CORRECTION.md`

## 28. Recommended Next Action

**PRIMARY**: Determine how NesysService.exe was originally started in the cabinet environment.

Options:
1. **Find the original launcher** — The cabinet likely had a startup script or launcher
   that started NesysService with correct arguments before launching AcrGame.
2. **Create a D: drive** — Mount the D DRIVE CONTENTS as D: and test if NesysService
   can start with the correct directory structure.
3. **Investigate registry keys** — NESYS may store configuration in Windows registry.
4. **Analyze NesysService arguments** — Determine what command-line arguments
   NesysService expects from the launcher.

**Do not**:
- Fabricate NESYS online status
- Bypass certificate verification
- Modify game files
- Implement matching or battle
