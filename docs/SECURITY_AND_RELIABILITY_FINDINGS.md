# Starwing Paradox - Security and Reliability Findings

> Audit date: 2026-08-25
> Source: `legacy-js/` (all JS files)

---

## Critical Findings

### 1. SQL Injection in playerRegister

**Location**: `playerProfile.js:394-436`
**Severity**: High
**Type**: SQL Injection (column name injection)

The `playerRegister` function dynamically builds an UPDATE statement using unsanitized key names directly from the request body:

```javascript
for(let k in req_body) {
    if (p>1) qtext += ", ";
    qtext += k + "=$"+p;  // k is directly from client request body
    p++;
    qvars.push(req_body[k]);
}
```

While the values are parameterized (preventing value injection), the **column names** are not sanitized. An attacker could inject arbitrary SQL in column names. For example, sending a key like `"x=1; DROP TABLE player; --"` could corrupt the query.

**Mitigation**: Whitelist allowed column names before building the query.

---

### 2. Hard-coded Database Credentials

**Location**: `starwing.js:49-55`
**Severity**: Medium
**Type**: Hardcoded Secrets

```javascript
const pgdb = new Pool({
    user: 'paradox',
    host: 'localhost',
    database: 'paradox',
    password: 'XXXXXXX',
    port: 5432
});
```

The password `XXXXXXX` is committed to the public GitHub repository. Even if this is a placeholder, it establishes a pattern of hardcoding credentials.

**Mitigation**: Use environment variables (`process.env.DB_PASSWORD`).

---

### 3. No Authentication Beyond IP Whitelist

**Location**: `starwing.js:40,87-93,345-358`
**Severity**: Medium
**Type**: Weak Authentication

The entire authentication system consists of:
1. Nginx adds `x-galaxy-real-ip` header from `$remote_addr`
2. First request to `/matching/server` auto-adds the IP to `authorizedClients`
3. TCP connections check `socket.remoteAddress` against `authorizedClients`

There are no session tokens, API keys, or cabinet-specific credentials. Any machine that can reach the server's IP can become authorized by making a single HTTP request.

**Mitigation**: Implement proper cabinet authentication (e.g., certificate-based, token-based).

---

## High Findings

### 4. No Input Validation on Most Endpoints

**Location**: All route handlers in `starwing.js`
**Severity**: High
**Type**: Missing Input Validation

Almost no endpoint validates:
- Required fields in request body
- Data types (everything arrives as string from form-encoded)
- Value ranges (e.g., rank IDs, weapon IDs)
- Field lengths

The cabinet sends data as `application/x-www-form-urlencoded`, which body-parser converts to JSON objects, but field types are never checked.

**Mitigation**: Add schema validation (e.g., Joi, Zod) for all request bodies.

---

### 5. Faked consecutive_login_days

**Location**: `playerProfile.js:104,311,378`
**Severity**: Medium (functional bug)
**Type**: Incorrect Business Logic

```javascript
this.Player.consecutive_login_days = this.Player.same_day_login_count ? 1 : 0;
```

This is always 0 or 1, regardless of actual consecutive login streaks. The source has `// FAKED TODO SQL count` comments. This means:
- Players never get rewards based on consecutive login days
- Login streak achievements are impossible
- The login bonus system cannot function correctly

**Mitigation**: Implement proper consecutive login day counting with SQL.

---

### 6. Hardcoded Battle Results

**Location**: `battleRecorder.js:5-43`
**Severity**: Medium (functional bug)
**Type**: Incomplete Implementation

```javascript
response.rank_point_2on2 = 10000;
response.ranking_score_2on2 = 500;
response.ranking_high_score_2on2 = 1000;
response.gained_ranking_score_2on2 = 200;
```

All battle result values are hardcoded. The actual battle result data sent by the cabinet (in `score_2on2`, `detail_2on2`, `players_2on2` fields seen in `API-NOTES.txt:16`) is completely ignored. This means:
- Rankings never change
- Battle rewards are always the same
- Player skill has no effect on progression

**Mitigation**: Implement actual ranking computation from battle data.

---

## Medium Findings

### 7. No Rate Limiting

**Location**: All route handlers
**Severity**: Medium
**Type**: Missing DoS Protection

No rate limiting exists on any endpoint. A malicious client could:
- Flood `/matching/server` to fill the `authorizedClients` array
- Spam `/player/register` to corrupt player data
- Overwhelm the database with concurrent `/game_data/save` requests

**Mitigation**: Add rate limiting middleware (e.g., express-rate-limit).

---

### 8. No Transaction Wrapping in playerSaveGameData

**Location**: `playerProfile.js:438-722`
**Severity**: Medium
**Type**: Data Integrity Risk

The `playerSaveGameData` function performs 15+ separate database operations without transaction wrapping:
- UPSERTs to 12 different tables
- UPDATEs to the player table for scalar fields
- Final SELECT on missions

If any operation fails midway, the database is left in an inconsistent state. For example, options might be saved but buddies are not.

**Mitigation**: Wrap the entire save operation in a PostgreSQL transaction.

---

### 9. Race Conditions in Burst Mode Room Management

**Location**: `burstMode.js:3-217`
**Severity**: Medium
**Type**: Concurrency Bug

Room management uses in-memory JavaScript arrays without any locking mechanism:
- `this.rooms = []`
- `this.players = []`

Concurrent operations could corrupt state:
1. Two cabinets create rooms simultaneously (`RequestChangeBurstGroupMode`)
2. One cabinet joins a room while another leaves (`RequestBurstGroupSelect`)
3. Room owner disconnects while others are joined

The `snooze(10)` calls (`burstMode.js:67-68`) suggest the developer was aware of timing issues but used delays instead of proper synchronization.

**Mitigation**: Implement proper locking or use a database-backed room state.

---

### 10. Memory Leak in Burst Mode Players Array

**Location**: `burstMode.js:200-205`
**Severity**: Medium
**Type**: Memory Leak

```javascript
this.players = this.players.filter(function(value, index, arr){
    return value.PlayerId != Player.PlayerId;
});
Player.ts = new Date().getTime() / 1000;
Player.socket = socket;
this.players.push(Player);
```

Players are added to `this.players` on every `RequestEntryBurstGroup` but there is no cleanup when:
- A TCP connection is closed (no handler removes the player)
- A player leaves a room
- A match ends

Over time, this array will grow unboundedly with stale entries, each holding a reference to a closed socket.

**Mitigation**: Add cleanup on socket close/end events.

---

### 11. Path Traversal in /ranking/weapon

**Location**: `starwing.js:477`
**Severity**: Low-Medium
**Type**: Path Traversal

```javascript
let jWeapons = JSON.parse(fs.readFileSync('starwing/c_rankingWeapon_r'+req.body.role_id+'.json','utf8'));
```

The `role_id` parameter from the request body is directly concatenated into a file path without sanitization. An attacker could send `role_id=../../etc/passwd` to read arbitrary files.

**Mitigation**: Validate that `role_id` is a numeric value; use path.join with base directory.

---

### 12. No Error Handling on DB Queries

**Location**: `playerProfile.js` (throughout)
**Severity**: Medium
**Type**: Missing Error Handling

Most database queries have no try/catch:
- `initWithPlayerID` has no error handling
- `playerLoadGameData` has no error handling
- `playerSaveGameData` has no error handling
- `playerLogin` has no error handling

Only `initWithNesys` has try/catch blocks. A database error in any of these functions will crash the request handler and potentially the server.

**Mitigation**: Add comprehensive error handling with proper HTTP error responses.

---

## Low Findings

### 13. Deprecated Buffer Constructor

**Location**: `starwing.js:71,97,99`
**Severity**: Low
**Type**: Deprecated API

```javascript
let outBuffer = new Buffer.alloc(4+msgBuffer.byteLength);  // line 71
var hexdata = new Buffer.from(data, 'ascii').toString('hex');  // line 97
let recvBuffer = new Buffer.from(data, 'ascii');  // line 99
```

While `Buffer.alloc` is correct, lines 97 and 99 use `Buffer.from` in ways that may not handle binary data correctly. The `'ascii'` encoding may corrupt protobuf data.

**Mitigation**: Use `Buffer.from(data)` without encoding specification for binary data.

---

### 14. Console Logging of Sensitive Data

**Location**: Throughout `starwing.js` and `burstMode.js`
**Severity**: Low
**Type**: Information Disclosure

Full request bodies, headers, and decoded protobuf messages are logged to console:
```javascript
console.log(req.headers);
console.log('Body: '+JSON.stringify(req.body));
console.log("Decoded: %s", decoded);
```

In production, this could expose player data, IP addresses, and session information.

**Mitigation**: Use a structured logging framework with log levels; avoid logging full request bodies in production.

---

### 15. Typo in Ranking Handler

**Location**: `starwing.js:481`
**Severity**: Low (functional bug)
**Type**: Code Defect

```javascript
deafult:
    res.set('x-galaxy-api', 'ranking/unknown');
    res.send("{}");
```

The keyword is misspelled as `deafult` instead of `default`. This means the default case in the ranking switch statement will never execute. Any unknown ranking path will fall through without setting the x-galaxy-api header or sending a response body.

**Mitigation**: Fix the typo.

---

### 16. Typo in Option Key

**Location**: Database data (player_options)
**Severity**: Low (functional bug)
**Type**: Data Defect

The option key `map_displa` is missing the trailing 'y'. Should be `map_display`. This is consistent across both test players.

**Mitigation**: Data migration to fix the typo; update client code if needed.

---

### 17. Typo in Child Mode Key

**Location**: Database data (player_options)
**Severity**: Low (functional bug)
**Type**: Data Defect

The option key `chaild_mode` should be `child_mode`. Consistent across both test players.

**Mitigation**: Data migration to fix the typo.

---

### 18. Missing Null Check in RequestBurstGroupSelect

**Location**: `burstMode.js:38-40`
**Severity**: Low
**Type**: Null Reference Risk

```javascript
let joiner = new Object();
for (let i = 0; i < this.players.length; i++) {
    if (this.players[i].PlayerId == request.PlayerId) joiner = this.players[i];
}
```

If the player is not found in `this.players`, `joiner` remains an empty object. Subsequent code attempts to access `joiner.socket`, which will be undefined, causing a crash.

**Mitigation**: Check if player was found and return error if not.

---

## Summary

| Severity | Count | Key Issues |
|----------|-------|-----------|
| Critical | 3 | SQL injection, hardcoded credentials, weak auth |
| High | 3 | No input validation, faked login days, hardcoded battle results |
| Medium | 5 | No rate limiting, no transactions, race conditions, memory leak, no error handling |
| Low | 6 | Deprecated APIs, logging, typos, null checks |

**Total findings**: 17

The most impactful issues for a production rewrite are:
1. SQL injection in playerRegister (must fix)
2. Transaction wrapping for data integrity (must fix)
3. Proper authentication beyond IP whitelist (should fix)
4. Input validation on all endpoints (should fix)
5. Actual battle result processing (must implement)
6. Consecutive login day counting (should implement)
