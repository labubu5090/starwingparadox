# GAME_CLIENT_STARTUP_DEPENDENCY_GRAPH

## Status

**Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

## Startup Criticality

The `ResidentModule` (`OpenKeyCheck.cpp`, `CPP_ErrorObserver.cpp`) is classified **STARTUP_CRITICAL**.
OpenKey validation governs whether the game proceeds to load content and enter play.

## Startup Sequence (as evidenced)

1. **AcrGame.exe launcher** starts, resolves the path to the Shipping build, and launches it
   (`CreateProcessW`). It contributes no network protocol.
2. **AcrGame-Win64-Shipping.exe** begins UE4 startup, loads configuration and master-data
   resources from disk (OpenKey, SaveData.json, master CSVs, test_mode_setting.json).
3. **ResidentModule** performs OpenKey check and installs the error observer.
4. **NetworkModule** initializes the HTTP layer (WININET/WinHTTP) and game session
   (`AcrGameSession.cpp`, `CPP_Session.cpp`).
5. **OutGameModule** sets up matching and disconnect handling (`CPP_MatchingMain.cpp`,
   `CPP_GameModeDisConnect.cpp`).
6. **USBIOModule** wraps GALAXYIO for local card I/O.
7. Battle system (BattleModule) initializes for in-game play.

## Dependencies

| Dependency | Source | Startup-critical | Network role |
|------------|--------|------------------|--------------|
| OpenKeyCheck | ResidentModule | YES | none (local file) |
| Master data (SaveData.json, CSVs) | disk | YES | local |
| HTTP layer (WININET/WINHTTP) | NetworkModule | YES | HTTP to server |
| Game session (AcrGameSession) | NetworkModule | YES | HTTP/TCP |
| Matching/disconnect | OutGameModule | NO (post-startup) | HTTP/TCP |
| GALAXYIO card I/O | USBIOModule | NO (card insert) | local HTTP cert + USB |
| Battle system | BattleModule | NO (in-game) | TCP |

## HTTP Endpoint Bindings (startup-adjacent)

- `BindHttpMatchingServer` — matching server
- `BindHttpMatchingMatchIdGenerate` — match ID generation
- `BindHttpGameDataSaveData` — save data
- `BindHttpFestResult` — festival result
- `BindHttpErrorCallback` — error callback
- `https://log.starwing.jp/acr/public/` — log upload (production, not private-server scope)

## Notes

- The game reads OpenKey and master data from **local disk** before contacting any server,
  so startup does not strictly require a live private server for **local content loading**.
- The exact client-handshake JSON for each Bind* endpoint is NOT yet confirmed from game-side
  evidence; HTTP payloads are open.
- OpenKey config is operator-supplied via the D-drive backup, not via the private server.

## References

- `artifacts/phase_2a_g19/startup_dependency_graph.json`
- `artifacts/phase_2a_g19/module_map.json`
