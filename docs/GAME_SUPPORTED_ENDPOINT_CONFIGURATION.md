# GAME_SUPPORTED_ENDPOINT_CONFIGURATION

## Status

**Classification:** NO_SUPPORTED_ENDPOINT_OVERRIDE_FOUND

## Conclusion

The game client has **no supported, game-side mechanism** to redirect its network endpoints to a
private server. The hardcoded game-server URL is `http://dev.starwing.jp/mock/matching/server`
(default HTTP port 80).

## Mechanisms Evaluated (all absent / not supported)

| Mechanism | Supported? | Notes |
|-----------|-----------|-------|
| Command-line argument | NO | No evidence in launcher or Shipping for an endpoint override flag |
| UE4 .ini (Engine.ini / GameUserSettings.ini) | NO | No endpoint-override key found |
| JSON/XML config file | NO | No endpoint redirect in OpenKey/SaveData/test_mode_setting |
| Environment variable | NO | No evidence |
| Registry | NO | Original registry absent; no game-side registry override path |
| In-game test mode | UNKNOWN | `test_mode_setting.json` exists but no endpoint config proven |

## Practical Redirection Path (operator-level, out of scope for G19)

- **Hosts-file / DNS** mapping `dev.starwing.jp` → `127.0.0.1`. This is operator action, not a
  game "supported" configuration. A hosts entry was previously applied.
- Proxy at `127.0.0.1:80` handling `/mock/` paths toward the private server.

## Implication for Architecture

Because the game hardcodes the endpoint and offers no supported override, any private-server
integration must operate at the **network/transport boundary** (hosts file + local proxy +
local TCP listener) rather than via game configuration. This matches the two-tier architecture
recommendation.

## Constraint Reminder

No binary modification or in-memory redirection of the game is permitted. Redirection may only
occur at the operator-owned TLS/DNS/proxy/transport boundary.

## References

- `artifacts/phase_2a_g19/network_endpoint_classification.json` (endpoint_override = NO_SUPPORTED_ENDPOINT_OVERRIDE_FOUND)
- `artifacts/phase_2a_g19/implementation_eligibility.json`
