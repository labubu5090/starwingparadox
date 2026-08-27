# Starwing Port Ownership

## Port Model (Updated G4)

| Port | Expected Owner | Role | Protocol | Evidence | Confidence | G4 Status |
|------|---------------|------|----------|----------|------------|-----------|
| 4000 | Unknown/WebAPI | Optional UI service or client | HTTP | Game config `WebAPIPort=4000`; NesysService binary has 5 uint16 refs | LOW | UNUSED_IN_OBSERVED_BOOT |
| 4001 | Python HTTP server | Game server (main backend) | HTTP | Game config `GameServerPort=4001`; no NesysService refs | HIGH | NO_GAME_CONNECTION |
| 6666 | NesysService.exe | NESYS card/network service | Named Pipe | Game config `NesysServerPort=6666`; binary uses named pipes, NOT TCP | HIGH | PIPE_NOT_CREATED |
| 8000 | Python dev server | Development HTTP server | HTTP | Current implementation; not game-facing | N/A | NOT_GAME_FACING |

## G4 Evidence

### Port 4001 — Game Server
- Game booted to title screen WITHOUT connecting to port 4001
- OnlineObserver: WebServer:0, HttpSuccess:0
- **Port 4001 is NOT needed for boot to title screen**
- May be needed for later game stages (online play, updates)

### Port 6666 — NESYS Service (Named Pipe, NOT TCP)
- Binary analysis confirmed: NesysService uses named pipes, NOT TCP sockets
- Pipe format: `\\.\pipe\nesys_games\%s%s`
- No pipe was created during the observed boot
- NesysService was never started by the game

### Port 4000 — Unknown
- UNUSED in observed boot
- No game connection observed
- May be needed for web API in later stages

### Port 8000 — Development
- Not game-facing

## Superseded Assumptions

The following earlier port assumptions are superseded by G4 runtime evidence:

1. ~~Port 6666 is a TCP listener~~ → Actually named pipe IPC
2. ~~Port 4001 is required for boot~~ → Not needed for title screen
3. ~~Port 4000 is needed for boot~~ → Unused in observed boot

## Recommendation

1. Python HTTP server → port 4001 (keep for future use)
2. Do NOT start Python TCP server on 6666 (NesysService uses pipes)
3. Do NOT implement port 4000 unless evidence requires it
4. Focus on rendering crash resolution before NESYS investigation
