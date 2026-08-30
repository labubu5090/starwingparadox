# G39 Final Report: Local Profile and Offline Session

## Classification
**Status:** `LOCAL_PROFILE_IMPLEMENTED`
**Game Integration:** `UNAVAILABLE` (tutorial persistence requires HTTP endpoints not yet implemented)

## Summary
Local profile system implemented with SQLite persistence, CRUD API endpoints, card-style PyQt5 GUI, server status dashboard, and tutorial progress tracking.

## Root Cause Analysis: Tutorial Persistence Failure

### Symptom
Tutorial progress (`$IsTutorialProgress`) resets to `0` on every relaunch. After completing the tutorial in G36, the game still shows the full onboarding flow on next launch.

### Root Cause Chain
The game client queries the HTTP backend for tutorial completion state via:
- `POST /tutorial/*` endpoints
- `POST /game_data/save` and `POST /game_data/load`

Our server returned **HTTP 501 (not implemented)** for all these endpoints. The game has **no local file persistence** for this flag — it is entirely server-authoritative.

### Evidence Chain
1. `ACPP_UserDataCheckMain::BeginPlay / $IsTutorialProgress[0]` on both first and second launch
2. `POST /tutorial/{path}` returns HTTP 501 (`server/app/api/tutorial.py` placeholder)
3. `POST /game_data/save` returns HTTP 501 (`server/app/api/game_data.py` placeholder)
4. `PlayerData1.sav` never created (always fails to load)
5. No HTTP calls to `game_data/save` or `/tutorial` in game log

### Note on Causation
The tutorial persistence failure is a multi-factor issue. The HTTP 501 response is the proximate cause, but the game's complete absence of local fallback persistence and the UserId=-1 state (no authenticated player) are contributing factors. We do not claim any single factor as the sole root cause without direct branch evidence proving causation.

### UserId Value
- **UserId = -1** when no card is inserted
- Meaning: Free play / test mode, no authenticated player identity
- BattlePlayerId = 0 (local index)

### Result_Timeover_Lose Flow
The tutorial battle is **scripted to time out** (unwinnable by design):
1. `FirstTimeTutorial` → Battle (51 respawns, ~590 seconds)
2. Timer expires → `RequestEndBattle` with `Result_Timeover_Lose`, `InTimeOver:1`
3. `LeaveMindWayBattle` → `NoContinue` map → `TerminatedBattle` → Title

## Implementation Deliverables

### Database Schema
- Table: `local_profile`
- Migration: `002_local_profile`
- 13 fields: id, profile_uuid, display_name, created_at, last_used_at, tutorial_attempts, tutorial_completed, tutorial_last_result, preferred_controller_index, settings_json, session_active, session_started_at, notes

### API Endpoints (7 routes)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/profile/local/create` | POST | Create a new local profile |
| `/profile/local/list` | POST | List all local profiles |
| `/profile/local/select` | POST | Select a profile and start session |
| `/profile/local/end` | POST | End the current session |
| `/profile/local/update` | POST | Update profile fields |
| `/profile/local/delete` | POST | Delete a profile |
| `/profile/local/tutorial/record` | POST | Record a tutorial attempt |

### GUI Applications
- **Profile Manager** (`tools/profile_manager/app.py`): Card-style PyQt5 interface
- **Server Dashboard** (`tools/profile_manager/dashboard.py`): Real-time server health monitoring

### Tests
- 11 tests in `tests/phase_2a/test_g39_local_profile.py`
- All passing

## Security Boundaries Maintained
- No NESYS/NESICA identity fabrication
- No game binary modification
- No forced `bNesysServerLive` or `IsOnline`
- Profile labeled as "Local Profile" / "Private Profile"
- No external interfaces exposed
- All tools bind to loopback only
- Tutorial completion is not fabricated
