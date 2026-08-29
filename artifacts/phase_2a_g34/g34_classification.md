# G34 Classification: INI_CONFIG_PATH_RUNTIME_CONFIRMED

## Summary

The game reads `DefaultMatchingServerAddress` from `[/Script/NetworkModule.NetworkConfig]` in `DefaultGame.ini` at runtime and uses it to establish a TCP connection to `127.0.0.1:6666` **without NESYS certificate trust**.

## Classification

**INI_CONFIG_PATH_RUNTIME_CONFIRMED**

## Evidence

### Critical Log Lines (from `g34_ini_config_capture.log`)

```
L110557: FAcrNetworkConfig::Init / port[7777]
L110561: MatchingServer : 127.0.0.1:6666 (UseConfigMatchingServer : 1)
L110567: Use Config(.ini)MatchingServer address:127.0.0.1:6666
L110575: Decide connect type INI file address
L111229: Success to connect. / GetTargetAddress[127.0.0.1:6666]
L111234: OnReceivePong / WebServer Revived!
```

### Config Source

```ini
[/Script/NetworkModule.NetworkConfig]
DefaultMatchingServerAddress=127.0.0.1:6666
```

File: `X:\StarwingParadox\WindowsNoEditor\AcrGame\Config\DefaultGame.ini`  
SHA-256: `37AE67B38CE6DB41E99F8D9BEE59BEE4E7AD7B53A3DEF05162D53AAE12BFBF62`

### Config Location Analysis

| Location | Exists | Contains NetworkConfig |
|----------|--------|----------------------|
| Source `Config\DefaultGame.ini` | Yes | Yes |
| `Saved\Config\WindowsNoEditor` | No | N/A |
| AppData `Game.ini` | Yes (2 bytes) | No |
| `Engine.ini` | No | N/A |

**Conclusion**: DefaultGame.ini is the sole config source. No overrides exist.

## Decision Path Flow

1. Game boots, preloads ~7553 assets
2. HTTP POST to `http://dev.starwing.jp/mock/matching/server` (via hosts file -> 127.0.0.1:80)
3. Proxy strips `/mock`, forwards to Python HTTP server on port 4001
4. Python returns `{"ip_addr":"127.0.0.1:6666"}`
5. Game sets ConnectAddress to `127.0.0.1:6666`
6. `Error No MatchingServer so initialize Nesys before.` — bootstrap message, NOT a boot blocker
7. `FAcrNetworkConfig::Init` reads `DefaultMatchingServerAddress=127.0.0.1:6666` from INI
8. `UseConfigMatchingServer=1` enables INI path (origin: likely code default, command line is empty)
9. **`Decide connect type INI file address`** — INI path selected
10. TCP connects to `127.0.0.1:6666`
11. Ping/Pong round-trip successful
12. Title screen visible (WBP_InsertStart animation)

## State Transitions

### Before Config Read
- `bNesysServerLive[0]`, `bGameConnect[1]`, `bHttpSuccess[1]`
- TCP: not connected

### After Config Read
- `bNesysServerLive[0]`, `bWebServerLive[1]`, `bGameConnect[0]`
- TCP: connected to `127.0.0.1:6666`, Ping/Pong working

## Unresolved Questions

1. **UseConfigMatchingServer origin**: Value is `1` but not set in INI or command line. Likely UE4 code default for `UseConfigMatchingServer` property.

2. **MatchingServerType**: Not set in INI. Exact enum/constant values unknown. Binary strings show property exists but no runtime value logged.

3. **NESYS control sequence**: `RequestNesysControlInitiazlize [Cert]` runs in background. CertError loop continues. `IsOnline` remains 0. NOT a boot blocker.

## Implications

### What This Proves

- **The game has a working INI-based network config path** that bypasses NESYS trust
- **No NESYS certificate trust is required** to reach a matching frame
- **DefaultGame.ini is the correct config file** for network settings
- **The existing proxy/HTTP/TCP server stack works** end-to-end

### What This Does NOT Prove

- Whether `MatchingServerType` is required (not tested, not set)
- Whether the game can proceed past title screen without NESYS (requires card swipe / Start button)
- Whether the TCP protocol can handle full matching flow (only Ping/Pong tested)

### Next Steps

1. Test with `MatchingServerType` set to determine exact values
2. Test game progression past title screen (card swipe simulation)
3. Implement TCP protocol handlers for full matching flow
4. Determine if NESYS pipe mock is needed for gameplay
