# Legacy JavaScript Server Runtime Audit

> **Audit date:** 2026-08-26
> **Scope:** `legacy-js/js/starwing.js` and dependencies
> **Goal:** Determine if the legacy JS server can run safely

---

## 1. Dependencies (`package.json`)

**Note:** `package.json` not found at `legacy-js/package.json`. Dependencies inferred from `require()` statements in `starwing.js`:

| Package | Usage | Required |
|---------|-------|----------|
| `node-fetch` | HTTP client (line 1) | Yes |
| `express` | HTTP server (line 2) | Yes |
| `protobufjs` | Protobuf encoding (line 3) | Yes |
| `pg` | PostgreSQL client (line 8) | Yes |
| `body-parser` | Request parsing (line 6) | Yes |

**Missing:** `package.json` — cannot install dependencies via `npm install`.

---

## 2. Runtime Requirements

### Node.js Version
- **Not specified** in any config file
- Uses `async/await` (line 488) → requires Node.js ≥ 7.6
- Uses `Buffer.alloc` (line 71) → requires Node.js ≥ 5.10
- **Recommended:** Node.js 14+ (LTS) for stability

### Required Environment Variables
**None.** All configuration is hard-coded in `starwing.js`:
- No `process.env` references found
- No `.env` file loading

### Required Ports

| Port | Protocol | Purpose | Line |
|------|----------|---------|------|
| 4001 | HTTP | Express REST API | `const web_port = 4001;` (line 28) |
| 6666 | TCP | Protobuf game server | `const pb_port = 6666;` (line 29) |
| 5432 | TCP | PostgreSQL | `port: 5432` (line 54) |

### Hard-coded Paths

| Path | Purpose | Line |
|------|---------|------|
| `starwing/c_resource.json` | Resource data file | line 786 |
| `starwingMessage.proto` | Protobuf schema | line 21 |
| `starwing/playerProfile.js` | Player profile module | line 10 |
| `starwing/battleRecorder.js` | Battle recorder module | line 11 |
| `starwing/burstMode.js` | Burst mode module | line 12 |

**Blocker:** These paths are relative to CWD. Server must be started from `legacy-js/js/` directory.

### Hard-coded Hostnames

| Hostname | Purpose | Line |
|----------|---------|------|
| `localhost` | PostgreSQL server | line 51 |
| `paradox.yourdomain.com` | Matcher/lobby address | line 31 |

**Blocker:** `paradox.yourdomain.com` is a placeholder DNS name. TCP connections from game cabinets will fail unless DNS resolves.

### Hard-coded Credentials

| Credential | Value | Line |
|------------|-------|------|
| PostgreSQL user | `paradox` | line 50 |
| PostgreSQL password | `XXXXXXX` | line 53 |
| PostgreSQL database | `paradox` | line 52 |
| PostgreSQL port | `5432` | line 54 |

**Blocker:** Password is placeholder `XXXXXXX`. Real password unknown.

---

## 3. PostgreSQL Requirements

### Connection Pool
```javascript
const pgdb = new Pool({
    user: 'paradox',
    host: 'localhost',
    database: 'paradox',
    password: 'XXXXXXX',
    port: 5432
});
```

### Can it start without PostgreSQL?
**Partially.** The `Pool` constructor does NOT immediately connect. It creates a lazy pool. The server will start and listen on ports 4001/6666.

**However:** Any request requiring DB access will fail:
- `/player/profile/load` → `pt.initWithNesys(pgdb, ...)` → crash
- `/player/login` → `pt.initWithPlayerID(pgdb, ...)` → crash
- `/game_data/load` → `pt.playerLoadGameData()` → crash
- `/battle/record_2on2` → `myBr.battleRecord2on2()` → crash

### Can static endpoints run without PostgreSQL?
**Yes.** These endpoints have zero DB interaction:
- `/version` — returns hardcoded versions
- `/resource` — reads `c_resource.json` file
- `/matching/match_id/generate` — returns random int
- `/mission/*` — returns `{}`
- `/credit/*` — returns `{}`
- `/tutorial/*` — returns `{"result":1}`
- `/ranking/*` — reads JSON files (but files may not exist)

---

## 4. Startup Sequence

### Command
```bash
cd legacy-js/js && node starwing.js
```

### Expected Output
```
StarWing Paradox prototype GameServer
HTTP 4001 Protobuf 6666
```

### What Happens at Startup
1. Loads `protobufjs` schema from `starwingMessage.proto` (line 21-25)
2. Creates Express app (line 27)
3. Creates PostgreSQL connection pool (lazy) (line 49-55)
4. Configures body-parser middleware (line 58-59)
5. Starts TCP server on port 6666 (line 80)
6. Starts HTTP server on port 4001 (line 791)

### TCP Server Behavior
- Listens on port 6666
- **Authorizes clients by IP** (line 87-94)
- Only accepts connections from IPs in `authorizedClients` array
- `authorizedClients` is populated by `/matching/server` endpoint (line 82-88)
- **Blocker:** No IPs are pre-authorized. First HTTP request to `/matching/server` with `x-galaxy-real-ip` header must happen before TCP connections work.

---

## 5. Exact Blockers for Running

### Critical Blockers (Server won't function)

| # | Blocker | Impact | Fix Required |
|---|---------|--------|--------------|
| 1 | **PostgreSQL password `XXXXXXX`** | All DB endpoints fail | Provide real password |
| 2 | **PostgreSQL database `paradox` may not exist** | Pool connection fails | Create database + schema |
| 3 | **Missing `package.json`** | Cannot install dependencies | Create package.json |
| 4 | **Missing `node_modules/`** | Cannot run | Run `npm install` |
| 5 | **Missing data files** (`c_resource.json`, ranking JSONs) | Static endpoints return errors | Provide data files |

### Moderate Blockers (Partial functionality)

| # | Blocker | Impact | Workaround |
|---|---------|--------|------------|
| 6 | **`paradox.yourdomain.com` DNS** | TCP matcher returns unresolvable hostname | Use real IP or localhost |
| 7 | **PostgreSQL schema unknown** | Tables may not exist | Reverse-engineer from `playerProfile.js` queries |
| 8 | **Relative file paths** | Must start from correct CWD | Always `cd legacy-js/js` first |
| 9 | **TCP IP authorization** | No IPs pre-authorized | Must call `/matching/server` first with correct IP |

### Minor Issues

| # | Issue | Impact |
|---|-------|--------|
| 10 | `deafult` typo in ranking switch (line 481) | Default case never executes |
| 11 | `new Buffer.alloc` deprecated API | Works but warns on newer Node.js |
| 12 | No error handling on DB queries | Unhandled rejections on DB failure |

---

## 6. Safe Running Assessment

### Can it start without PostgreSQL?
**YES** — the server will start and listen on ports. Static endpoints work.

### Can static endpoints run without PostgreSQL?
**YES** — `/version`, `/resource`, `/mission/*`, `/credit/*`, `/tutorial/*` have no DB dependency.

### What ports does it listen on?
- **4001** (HTTP/Express)
- **6666** (TCP/Protobuf)

### What environment variables are needed?
**NONE** — all configuration is hard-coded.

---

## 7. Recommendations

1. **Do not run the legacy server in production** — credentials are placeholder, DNS is fake
2. **For testing static endpoints only:** Create a minimal runner that skips DB initialization
3. **For full testing:** Need real PostgreSQL with correct schema and data
4. **For TCP testing:** Need to pre-authorize test client IP via `/matching/server`
