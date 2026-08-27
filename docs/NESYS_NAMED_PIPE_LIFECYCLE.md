# NESYS Named Pipe Lifecycle

## Pre-Launch Baseline

- Named pipes scanned before game launch
- No `nesys_games` pipe existed in baseline
- System pipes: InitShutdown, lsass, ntsvcs, Winsock2, epmapper, etc.

## During Boot

- No `nesys_games` named pipe was created during the observed boot
- NesysService.exe was never started by the game
- No pipe server was created by any process

## Classification

**GAME_CREATES_PIPE**: NOT_OBSERVED  
**NESYS_SERVICE_CREATES_PIPE**: NOT_OBSERVED  
**GAME_CONNECTS_AS_CLIENT**: NOT_OBSERVED  
**NESYS_SERVICE_CONNECTS_AS_CLIENT**: NOT_OBSERVED  

## Analysis

The game's NESYS client plugin (`NesysClientPlugin.uplugin`) initializes at frame 2 but does not create a named pipe. The game expects NesysService.exe to create the pipe server. Since NesysService was never started, no pipe was created.

The CertError loop (7557 occurrences, frames 4-560) is the game's NESYS client retrying to connect to the pipe server. Despite this, the game progresses past the boot phase.

## Conclusion

The named pipe lifecycle is: NesysService creates pipe → Game connects as client. Without NesysService, no pipe exists.
