# G44 Final Report

## Classification: NESYS_CARD_EVENT_REQUIRED

## Live Validation Summary

### What Was Proven
1. **`POST /matching/server`** — dedicated handler, returns `{"ip_addr":"127.0.0.1:6666"}`, game accepts it
2. **TCP `127.0.0.1:6666`** — ping/pong working, connection established
3. **`POST /player/profile/load`** — handler implemented, returns 32-field profile response
4. **OpenKey.json** — loads correctly (`IsOpen[1]`)
5. **SystemDataCheck** — passes
6. **INI matching address** — `127.0.0.1:6666` read correctly

### What Was NOT Proven
1. **`/player/profile/load` never called** — game does not issue this request without NESYS pipe
2. **No card-present event** — NESYS pipe not connected
3. **No green network icon** — NESYS initialization failed
4. **Player Data screen not reached** — game stuck at PromotionMovie
5. **Card confirmation not reached** — requires NESYS pipe

### Root Cause
The game's `LogAcrProtocol: Error No MatchingServer so initialize Nesys before.` confirms that the NESYS named pipe (`\\.\pipe\nesys_games`) must be initialized before the game can use the matching server and proceed to card/profile flow.

The NESYS pipe handles:
- `LCOMMAND_CARD_SELECT_REQUEST` — card identification
- `LCOMMAND_CARD_INSERT_REQUEST` — card insertion
- `LCOMMAND_CONNECT_REQUEST` — NESYS connection with certificate
- `SCOMMAND_CERT_INIT_NOTICE` — certificate initialization

Without NESYS pipe, the game blocks at the title/promotion screen with no network icon.

### Security Boundary
NESYS pipe emulation requires:
- Binary protocol (4-byte LE command ID + payload)
- Certificate initialization (`SCOMMAND_CERT_INIT_NOTICE`)
- Shop/tenpo identification
- Network configuration

This is a **security boundary** that cannot be crossed without:
- Forging NESYS authentication
- Creating fake certificates
- Identifying as an official operator

## Handler Status

### POST /player/profile/load — IMPLEMENTED, NOT REACHED
- Dedicated handler (not catch-all)
- Returns 32 fields matching public implementation format
- Query `player` table by `nesys_id`
- Create new player if not found
- **Classification**: GAME_CLIENT_CONFIRMED, LIVE_VALIDATION_INCONCLUSIVE

### POST /matching/server — WORKING, ACCEPTED
- Dedicated handler returns `{"ip_addr":"127.0.0.1:6666"}`
- Game logs: `_IsSuccess[1] IPAddress[127.0.0.1:6666]`
- **Classification**: RUNTIME_CONFIRMED

## Test Totals
- **125 collected, 125 passed, 0 failed, 0 skipped**
- Mypy: clean (85 files)
- Ruff: clean

## Next Steps (G45)
The only path forward requires resolving the NESYS pipe dependency:
1. Determine if the game can proceed without NESYS in any mode
2. Investigate `MatchingServerType` configuration options
3. Explore whether test mode or alternate INI settings bypass NESYS requirement
4. If NESYS pipe emulation is ever implemented (with strict security controls), retry live validation
