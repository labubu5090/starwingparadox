# NESYS WINHTTP Sequence

## Observed External Connections

No external HTTPS connections were observed during the G4 extended boot. The game's NESYS client plugin uses WINHTTP internally, but the external connection to `cert3.nesys.jp` was not visible in TCP connection monitoring.

## Analysis

The NESYS plugin's WINHTTP client may:
1. Connect through a different process (NesysService.exe, which was not running)
2. Use a connection method not visible in TCP monitoring
3. Fail immediately without retry (since NesysService is not running)

## Game's Built-In HTTP

The game's OnlineObserver reported:
- WebServer: 0
- Nesys: 0
- HttpSuccess: 0

This indicates the game's HTTP client did not successfully connect to any server.

## Conclusion

No WINHTTP connections were observed. The game operates in offline mode when NesysService is not available.
