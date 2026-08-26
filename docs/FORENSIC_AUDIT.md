# Starwing Paradox - Legacy Server Forensic Audit

> Audit date: 2026-08-25
> Source: `legacy-js/` (cloned from https://github.com/ArcadeMachinist/StarwingParadox)

---

## 1. Repository Overview

- **GitHub**: ArcadeMachinist/StarwingParadox (public)
- **Commits**: 9
- **Language**: JavaScript (Node.js)
- **Description**: "Starwing Paradox Mock Server" - a work-in-progress prototype for the full-motion mecha arcade cabinet game Starwing Paradox by a]2 (AcrGame).
- **Game cabinet**: FMV mecha fight simulator arcade machines from Japan.

### Key Files

| Path | Purpose |
|------|---------|
| `js/starwing.js` | Main server (HTTP + TCP) |
| `js/starwing/playerProfile.js` | Player DB operations class |
| `js/starwing/battleRecorder.js` | Battle result recording |
| `js/starwing/burstMode.js` | Co-op room management (TCP) |
| `js/starwingMessage.proto` | Protobuf schema (390 lines) |
| `js/nginx.vhost.conf` | Nginx reverse proxy config |
| `paradox.sql` | PostgreSQL schema dump (15 tables) |
| `js/starwing/API-NOTES.txt` | Reverse-engineering notes |

---

## 2. Infrastructure

### HTTP Server
- **Framework**: Express.js
- **Port**: 4001 (HTTP)
- **Binding**: Not specified (Express default)

### TCP Server
- **Port**: 6666 (raw TCP, Protobuf-encoded)
- **Binding**: `0.0.0.0` (line 342 of `starwing.js`)

### Dependencies
- `express` - HTTP framework
- `protobufjs` - Protocol Buffers encoding/decoding
- `node-fetch` - HTTP client (imported but unused in current code)
- `body-parser` - Request body parsing
- `pg` (PostgreSQL) - Database driver (`Pool` from `pg`)

### Nginx Reverse Proxy (`nginx.vhost.conf`)
```
server {
    listen paradox.yourdomain.com:80;
    server_name paradox.yourdomain.com;
    root /var/www/paradox/html;
    index index.html;
    proxy_set_header x-galaxy-real-ip $remote_addr;
    location /mock         { proxy_pass http://127.0.0.1:4001; }
    location /matching     { proxy_pass http://127.0.0.1:4001; }
    location /version      { proxy_pass http://127.0.0.1:4001; }
    location /ranking      { proxy_pass http://127.0.0.1:4001; }
    location /resource     { proxy_pass http://127.0.0.1:4001; }
    location /player       { proxy_pass http://127.0.0.1:4001; }
    location /credit       { proxy_pass http://127.0.0.1:4001; }
    location /tutorial     { proxy_pass http://127.0.0.1:4001; }
    location /game_data    { proxy_pass http://127.0.0.1:4001; }
    location /battle       { proxy_pass http://127.0.0.1:4001; }
    location /mission      { proxy_pass http://127.0.0.1:4001; }
}
```

- Nginx adds `x-galaxy-real-ip` header from `$remote_addr` (the client's real IP).
- All locations proxy to `127.0.0.1:4001`.

---

## 3. Database

### PostgreSQL Configuration (hard-coded in `starwing.js:49-55`)
```javascript
const pgdb = new Pool({
    user: 'paradox',
    host: 'localhost',
    database: 'paradox',
    password: 'XXXXXXX',
    port: 5432
});
```

- **PostgreSQL version**: 12.6 (Ubuntu 20.04)
- **Schema**: 15 tables (see `DATABASE_MAP.md`)
- **Test data**: 2 players pre-seeded (IDs 10010 "ArcadeMachinist", 10011 "Lord Cereth")
- **No battle/match tables** in the schema

---

## 4. Hard-Coded Values

| Constant | Value | Location |
|----------|-------|----------|
| `version_main` | 70571 | `starwing.js:32` |
| `version_data` | 70571 | `starwing.js:33` |
| `matcher` | `paradox.yourdomain.com:6666` | `starwing.js:31` |
| `web_port` | 4001 | `starwing.js:28` |
| `pb_port` | 6666 | `starwing.js:29` |

---

## 5. Client Identification

### HTTP (via Nginx)
- Client IP identified via `x-galaxy-real-ip` header (injected by Nginx from `$remote_addr`).
- IP is accumulated at runtime in the `authorizedClients` array (`starwing.js:40`).
- First time an IP hits `/matching/server`, it's added to the whitelist.
- Subsequent requests check the whitelist; unauthorized TCP connections are destroyed.

### TCP (Protobuf)
- On connection, `socket.remoteAddress` is checked against `authorizedClients`.
- If not in the list, the socket is immediately destroyed (`starwing.js:87-93`).
- The authorizedClients list is populated only through the HTTP `/matching/server` endpoint.

### Cabinet User-Agent
```
game=AcrGame, engine=UE4, version=4.16.3-0+++UE4+Release-4.16, platform=Windows, osver=6.2.9200.1.256
```
Source: `API-NOTES.txt:27`

---

## 6. HTTP Protocol Details

### Request
- **Content-Type**: `application/x-www-form-urlencoded` (but body-parser also parses JSON)
- **Codec**: JSON (via `body-parser.json()`)

### Response
- **Content-Type**: `application/json`
- **Response Headers**:
  - `x-galaxy-api`: Service name or `*/*`
  - `x-galaxy-api-id`: Echoed from request header

---

## 7. TCP/Protobuf Protocol

### Wire Format
- **Length prefix**: 4-byte unsigned little-endian (byte length of protobuf payload)
- **Payload**: Protobuf-encoded `starwing.PbMessage`
- Source: `PbSendPayload()` at `starwing.js:62-78`

### PbMessage Envelope
```protobuf
message PbMessage {
    int64 packetId = 1;
    int64 messageType = 2;
    optional int64 sessionId = 3;
    oneof Message { ... }  // message-specific payload
}
```

### TCP Connection Lifecycle
1. Cabinet connects to port 6666
2. Server checks `socket.remoteAddress` against `authorizedClients`
3. If authorized, listens for data events
4. Each packet: 4-byte LE length + PbMessage bytes
5. Decoded via `pbMessageRoot.lookupType("starwing.PbMessage").decode()`
6. `messageType` determines the handler

---

## 8. HTTP Route Status Matrix

| Method | Path | Status | Notes |
|--------|------|--------|-------|
| POST | `/version` | IMPLEMENTED_STATIC | Returns hardcoded `version_main` and `version_data` |
| POST | `/resource` | IMPLEMENTED_STATIC | Reads and returns `c_resource.json` |
| POST | `/matching/server` | IMPLEMENTED_STATIC | Returns matcher address, auto-authorizes client IP |
| POST | `/matching/match_id/generate` | IMPLEMENTED_STATIC | Returns random int 10000-99999 |
| POST | `/matching/*` | PLACEHOLDER | Returns `{}` |
| POST | `/ranking/national` | IMPLEMENTED_STATIC | Reads `c_rankingNational.json` |
| POST | `/ranking/location` | IMPLEMENTED_STATIC | Reads `c_rankingStore.json` |
| POST | `/ranking/prefecture` | IMPLEMENTED_STATIC | Reads `c_rankingPrefecture.json` |
| POST | `/ranking/event` | IMPLEMENTED_STATIC | Reads `c_rankingEvent.json` |
| POST | `/ranking/weapon` | IMPLEMENTED_STATIC | Reads weapon ranking JSON by `role_id` param |
| POST | `/player/profile/load` | IMPLEMENTED_DB_BACKED | Loads/creates player by `nesys_id` |
| POST | `/player/login` | IMPLEMENTED_DB_BACKED | Loads player by `player_id`, logs login, returns profile |
| POST | `/player/login_bonus` | PLACEHOLDER | Returns `result:1`, empty bonuses |
| POST | `/player/register` | IMPLEMENTED_DB_BACKED | Updates player profile and progress |
| POST | `/player/*` | PLACEHOLDER | Returns `{result:1}` |
| POST | `/mission/*` | PLACEHOLDER | Returns `{}` |
| POST | `/credit/*` | PLACEHOLDER | Returns `{}` |
| POST | `/tutorial/*` | PLACEHOLDER | Returns `{result:1}` |
| POST | `/game_data/load` | IMPLEMENTED_DB_BACKED | Loads full game data for player |
| POST | `/game_data/load/mission` | IMPLEMENTED_DB_BACKED | Loads mission data only |
| POST | `/game_data/save` | IMPLEMENTED_DB_BACKED | Saves full game data (options, buddies, progresses, missions, titles, emblems, mecha_sets, etc.) |
| POST | `/game_data/*` | PLACEHOLDER | Returns `{result:1}` |
| POST | `/battle/record_2on2` | IMPLEMENTED_DB_BACKED | Records battle result, returns hardcoded rankings |
| POST | `/battle/*` | PLACEHOLDER | Returns `{result:1}` |
| POST | `/mock/*` | PLACEHOLDER | Returns matcher address |
| POST | `/mock/matching/server` | PLACEHOLDER | Returns matcher address |

### Status Legend
- **IMPLEMENTED_STATIC**: Fully functional, returns static data (no DB)
- **IMPLEMENTED_DB_BACKED**: Fully functional with PostgreSQL queries
- **PLACEHOLDER**: Returns stub response, logic not implemented

---

## 9. TCP/Protobuf Handler Status

| messageType | Hex | Name | Handler | Status |
|-------------|-----|------|---------|--------|
| 102 | 0x66 | Ping | `starwing.js:118-123` | IMPLEMENTED (echoes timestamp) |
| 200 | 0xC8 | RequestEntryMatching | `starwing.js:222-294` | IMPLEMENTED (hardcoded fake match) |
| 208 | 0xD0 | RequestEntryBurstGroup | `starwing.js:125-129` | IMPLEMENTED (co-op registration) |
| 210 | 0xD2 | RequestChangeBurstGroupMode | `starwing.js:137-141` | IMPLEMENTED (create room) |
| 214 | 0xD6 | RequestUpdateBurstGroup | `starwing.js:216-220` | IMPLEMENTED (list rooms) |
| 216 | 0xD8 | RequestBurstGroupSelect | `starwing.js:131-135` | IMPLEMENTED (join room) |
| other | - | Unhandled | `starwing.js:296-299` | Logged as unhandled |

---

## 10. Security Findings

### SQL Injection (`playerProfile.js:394-436`)
The `playerRegister` function builds an UPDATE statement dynamically using unsanitized key names from the request body:
```javascript
for(let k in req_body) {
    qtext += k + "=$"+p;  // k is directly from client request body
    p++;
    qvars.push(req_body[k]);
}
```
This allows column name injection. While parameterized values prevent value injection, an attacker could target arbitrary columns.

### Hard-coded Credentials
- Database password `'XXXXXXX'` is hard-coded at `starwing.js:53`.
- Should be moved to environment variables.

### No Authentication Beyond IP Whitelist
- No session tokens, API keys, or cabinet authentication.
- Any IP that first hits `/matching/server` is auto-authorized.
- TCP connections are authorized the same way.

### No Input Validation
- Most endpoints perform no validation on request body fields.
- Missing fields silently become `undefined`.

### Faked `consecutive_login_days` (`playerProfile.js:104,311,378`)
```javascript
this.Player.consecutive_login_days = this.Player.same_day_login_count ? 1 : 0;
```
This is always 0 or 1, regardless of actual consecutive login streaks. Marked with `// FAKED TODO SQL count`.

### Hardcoded Battle Results (`battleRecorder.js:5-43`)
`battleRecord2on2` returns hardcoded ranking values:
```javascript
response.rank_point_2on2 = 10000;
response.ranking_score_2on2 = 500;
response.ranking_high_score_2on2 = 1000;
response.gained_ranking_score_2on2 = 200;
```
No actual battle result processing or ranking computation.

### No Rate Limiting
- No request throttling on any endpoint.
- No protection against rapid-fire requests.

### No Transaction Wrapping
- Multiple sequential DB queries in `playerSaveGameData` are not wrapped in a transaction.
- Partial failures could leave inconsistent state.

### Race Conditions in Burst Mode (`burstMode.js`)
- Room management uses in-memory arrays without locking.
- Concurrent `RequestChangeBurstGroupMode` and `RequestBurstGroupSelect` could corrupt room state.

---

## 11. Data Flow Summary

### HTTP Flow
```
Cabinet (UE4) --HTTP POST--> Nginx (:80) --proxy--> Express (:4001)
                  Headers: x-galaxy-real-ip (added by Nginx)
                  Content-Type: application/x-www-form-urlencoded
                  Body: JSON
```

### TCP Flow
```
Cabinet (UE4) --TCP--> Node.js (:6666)
  Wire: [4-byte LE length][PbMessage bytes]
  messageType determines handler
```

### Matching Flow
1. Cabinet POSTs to `/matching/server`
2. Server returns matcher address `paradox.yourdomain.com:6666`
3. Cabinet connects to TCP port 6666
4. Cabinet sends `RequestEntryMatching` (200)
5. Server responds with `ResponseEntryMatching` (201)
6. Server sends `NotifyMatchMade` (302) with fake match data
7. Server sends `NotifyMatchBegin` (304) with match ID

---

## 12. Summary Statistics

| Metric | Count |
|--------|-------|
| HTTP routes | 27 (5 implemented, 22 placeholders) |
| TCP handlers | 6 (all implemented) |
| DB tables | 15 |
| Proto messages | ~40 |
| Hardcoded test players | 2 (10010, 10011) |
| Source files | 4 JS + 1 proto + 1 SQL + 1 nginx conf |
| Total JS lines | ~1,785 |
