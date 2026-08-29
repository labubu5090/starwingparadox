# G30R End-to-End Connection Proof

## Connection Chain Proven

```
AcrGame-Win64-Shipping.exe
  -> POST /mock/matching/server
  -> dev.starwing.jp resolves to 127.0.0.1
  -> local port-80 proxy (strips /mock prefix)
  -> Python server on 127.0.0.1:4001
  -> matching discovery handler
  -> response returned: {"ip_addr": "127.0.0.1:6666"}
  -> game accepts response: _IsSuccess[1]
  -> game advances: bChangeServer[1] IsSuccess[1]
```

## Evidence

| Step | Timestamp | Evidence |
|------|-----------|----------|
| Game sends request | 11:53:27.980 | `Request:[POST] http://dev.starwing.jp/mock/matching/server` |
| Proxy receives | 11:53:27.980 | Proxy log: `PROXY POST /mock/matching/server -> /matching/server` |
| Python responds | 11:53:27.997 | `Response url:[http://dev.starwing.jp/mock/matching/server]` |
| Game parses | 11:53:27.997 | `OnReceiveResponseMatchingServer / _IsSuccess[1] IPAddress[127.0.0.1:6666]` |
| Server change | 11:53:27.997 | `OnReceiveMatchingServer / bChangeServer[1] IsSuccess[1]` |

## Next Boundary

```
Error No MatchingServer so initialize Nesys before.
```

The game requires NESYS initialization before proceeding to matching entry.

## Classification

**GAME_ACCEPTED_MATCHING_DISCOVERY_RESPONSE**
