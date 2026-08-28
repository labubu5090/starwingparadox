# PRIVATE_SERVER_MINIMUM_ARCHITECTURE

## Status

**Classification:** GAME_CLIENT_CONTRACT_SUFFICIENT_FOR_NEXT_IMPLEMENTATION

## Recommendation

**Option A — Two-tier service** (proxy/adapter + Python server), operating at the
network/transport boundary.

## Architecture

```
Game (Shipping exe)
   │  hardcoded endpoint: http://dev.starwing.jp (port 80)
   ▼  (operator hosts-file/DNS: dev.starwing.jp -> 127.0.0.1)
┌────────────────────────────┐
│ Transport boundary         │
│  HTTP proxy :80            │  strips /mock/, forwards to :4001
│  (local pipe adapter later)│  only after pipe-role evidence
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│ Python private server      │
│  HTTP FastAPI :4001        │  matching, game data, fest result, error
│  TCP listener :6666        │  battle/matching (protobuf + LE length prefix)
│  SQLite                    │  single runtime
└────────────────────────────┘
```

## Why Option A

1. The game hardcodes its endpoint and offers **no supported override**; operator-level
   redirect (hosts file + local proxy) is the only practical path.
2. The game uses **multiple transports** (HTTP + TCP + local pipe), so a composite surface is
   required; a monolithic single-port design (Option D) is incompatible.
3. The existing deployed architecture (HTTP :4001, proxy :80, TCP :6666) already follows this shape.
4. The cleanroom synthetic foundation remains intact; the production adapter is gated on
   confirmed game-side evidence.

## Local Adapter (deferred)

A local named-pipe adapter for `\\.\pipe\nesys_games` is proposed but NOT built in G19.
It is only justified once the game's pipe role (server vs client) and message format are resolved.

## Excluded

- Running the proxy on a non-80 port (game uses default HTTP port 80).
- Modifying/redirecting the game executables (integrity constraint).
- Rebuilding full NesysService.
- Reproducing production certificate trust (https://cert2.nesys.jp) / card AMIC service.

## References

- `artifacts/phase_2a_g19/implementation_eligibility.json` (architecture_recommendation)
- `artifacts/phase_2a_g19/network_endpoint_classification.json`
- `docs/GAME_SUPPORTED_ENDPOINT_CONFIGURATION.md`
