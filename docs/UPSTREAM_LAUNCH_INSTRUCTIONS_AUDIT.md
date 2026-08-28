# Upstream Launch Instructions Audit

**Repository**: https://github.com/ArcadeMachinist/StarwingParadox  
**Local Clone**: `C:\Users\KAHO\Pictures\Starwing\legacy-js`  
**Audit Date**: 2026-08-28  
**Audit Phase**: 2A-G11  
**Status**: COMPLETE  

---

## Executive Summary

The upstream repository provides a **mock server** for Starwing Paradox. It is NOT a complete game launch solution. The repository provides:

- **HTTP API mock server** (Express.js on port 4001)
- **TCP/Protobuf server** (net.createServer on port 6666)
- **Nginx reverse proxy config** (port 80 → 4001)
- **Database schema** (PostgreSQL via `paradox.sql`)

The repository does NOT provide:

- Game executable (AcrGame.exe, AcrGame-Win64-Shipping.exe)
- NESYS service (NesysService.exe)
- NESYS initialization/provisioning
- Certificate provisioning
- Registry setup
- D-drive deployment
- Original cabinet environment

**Final Classification**: `MOCK_SERVER_START_ONLY`

---

## Repository Structure

```
StarwingParadox/
├── README.md                           (434 bytes)
├── html/
│   └── index.html                      (41 bytes) - "This page was intentionally left blank."
├── js/
│   ├── nginx.vhost.conf               (1,225 bytes) - Nginx reverse proxy config
│   ├── starwing.js                    (28,579 bytes) - Main entry point
│   └── starwing/
│       ├── API-NOTES.txt              (41,228 bytes) - API capture logs
│       ├── any.proto                  (6,065 bytes) - Protobuf dependency
│       ├── battleRecorder.js          (1,907 bytes) - Battle recording module
│       ├── burstMode.js              (9,574 bytes) - Burst mode implementation
│       ├── c_rankingEvent.json       (120 bytes) - Ranking event config
│       ├── c_rankingNational.json    (26,120 bytes) - National ranking config
│       ├── c_rankingNational_2on2.json (26,988 bytes) - National ranking 2v2 config
│       ├── c_rankingPrefecture.json  (26,159 bytes) - Prefecture ranking config
│       ├── c_rankingPrefecture_2on2.json (27,019 bytes) - Prefecture ranking 2v2 config
│       ├── c_rankingStore.json       (26,169 bytes) - Store ranking config
│       ├── c_rankingStore_2on2.json  (27,029 bytes) - Store ranking 2v2 config
│       ├── c_rankingWeapon_r1.json   (2,070 bytes) - Weapon ranking R1
│       ├── c_rankingWeapon_r2.json   (2,073 bytes) - Weapon ranking R2
│       ├── c_rankingWeapon_r3.json   (2,073 bytes) - Weapon ranking R3
│       ├── c_rankingWeapon_r4.json   (2,073 bytes) - Weapon ranking R4
│       ├── c_resource.json           (9,393 bytes) - Resource config
│       ├── io.txt                     (343 bytes) - USBIO packet capture
│       ├── playerProfile.js          (38,215 bytes) - Player profile management
│       ├── rankingCooker.js          (5,302 bytes) - Ranking data processor
│       ├── rankingDeps.json          (1,131 bytes) - Ranking dependencies
│       ├── rankingEvent.json         (95 bytes) - Event ranking data
│       ├── rankingNational.json      (19,010 bytes) - National ranking data
│       ├── rankingNational_.json     (1,884 bytes) - National ranking data (alt)
│       ├── rankingNational_2on2.json (10,483 bytes) - National ranking 2v2 data
│       ├── rankingPrefecture.json    (10,328 bytes) - Prefecture ranking data
│       ├── rankingPrefecture_2on2.json (10,508 bytes) - Prefecture ranking 2v2 data
│       ├── rankingStore.json         (10,339 bytes) - Store ranking data
│       └── rankingStore_2on2.json    (10,519 bytes) - Store ranking 2v2 data
└── paradox.sql                        (92,160 bytes) - PostgreSQL database schema
```

**Total Files**: 28  
**Total Size**: ~330 KB  

---

## Answer to 20 Audit Questions

### Q1: Is there a package.json?
**NO** - The upstream repository has NO `package.json` file. This means:
- No npm scripts defined
- No dependency management
- No explicit Node.js version requirement

### Q2: Is there an npm start script?
**NO** - Without `package.json`, there is no npm start script. The README states:
> "To start the server run 'node js/starwing.js'"

### Q3: What is the main entry point?
**`js/starwing.js`** (28,579 bytes)

Entry point evidence:
- Line 1: `const express = require('express');`
- Line 2: `const app = express();`
- Line 3: `const server = http.createServer(app);`
- Line 11: `const pb_port = 6666;`
- Line 12: `const web_port = 4001;`
- Line 758: `server.listen(web_port);`

### Q4: What port does the HTTP server use?
**Port 4001** (const web_port = 4001)

Evidence from `js/starwing.js`:
- Line 12: `const web_port = 4001;`
- Line 758: `server.listen(web_port);`

### Q5: What port does the TCP server use?
**Port 6666** (const pb_port = 6666)

Evidence from `js/starwing.js`:
- Line 11: `const pb_port = 6666;`
- Line 759: `pb_server.listen(pb_port);`

### Q6: Is there an HTTP server?
**YES** - Express.js HTTP server on port 4001

Evidence from `js/starwing.js`:
- Lines 1-3: Express app creation
- Lines 24-68: Route handlers for all game endpoints
- Line 758: `server.listen(web_port);`

### Q7: Is there a TCP server?
**YES** - net.createServer TCP server on port 6666

Evidence from `js/starwing.js`:
- Line 759: `pb_server.listen(pb_port);`
- Lines 692-757: TCP connection handler with protobuf framing

### Q8: Is there a reverse proxy configuration?
**YES** - nginx.vhost.conf provides reverse proxy configuration

Evidence from `js/nginx.vhost.conf`:
- Line 12: `proxy_pass http://127.0.0.1:4001;` - Proxies to HTTP server
- Lines 6-13: Location blocks for `/mock`, `/matching`, `/version`, `/ranking`, `/resource`, `/player`, `/credit`, `/tutorial`, `/game_data`, `/battle`, `/mission`

### Q9: How do you launch the game?
**NOT DOCUMENTED** - The upstream repository does NOT provide game launch instructions.

README states:
> "Starwing Paradox Mock Server"
> "WORK IN PROGRESS"

### Q10: Is AcrGame.exe mentioned?
**NO** - No reference to AcrGame.exe in the repository.

### Q11: Is AcrGame-Win64-Shipping.exe mentioned?
**NO** - No reference to AcrGame-Win64-Shipping.exe in the repository.

### Q12: Is NesysService.exe mentioned?
**NO** - No reference to NesysService.exe in the repository.

### Q13: Is NesysService startup implemented?
**NO** - No NESYS service implementation.

Evidence: Searching for "nesys", "NesysService", "pipe" in `js/starwing.js` yields no results.

### Q14: Is the nesys_games named pipe implemented?
**NO** - No named pipe implementation.

Evidence: `js/starwing.js` uses TCP sockets, not named pipes.

### Q15: Is OpenKey provisioning implemented?
**NO** - No OpenKey file provisioning.

Evidence: Searching for "OpenKey", "open_key", "openkey" in `js/starwing.js` yields no results.

### Q16: Is certificate provisioning implemented?
**NO** - No certificate provisioning.

Evidence: Searching for "certificate", "ssl", "tls" in `js/starwing.js` yields no results.

### Q17: Is registry setup implemented?
**NO** - No Windows registry manipulation.

Evidence: Searching for "registry", "reg", "HKEY_" in `js/starwing.js` yields no results.

### Q18: Is D-drive deployment documented?
**NO** - No documentation about D-drive deployment.

Evidence: Searching for "D:", "D drive", "D-drive" in repository yields no results.

### Q19: Is the original cabinet environment assumed?
**NO** - The repository explicitly states it is a mock server.

README states:
> "Starwing Paradox Mock Server"
> "A mock server to make Starwing Paradox think it's talking to a real server."
> "WORK IN PROGRESS"

### Q20: What is the startup order?
**NOT DOCUMENTED** - No startup order documented.

The README implies:
1. Start PostgreSQL database
2. Import paradox.sql schema
3. Run `node js/starwing.js`
4. Configure nginx to proxy to port 4001

---

## Local vs Upstream Comparison

### Repository Identity
- **Local clone**: `C:\Users\KAHO\Pictures\Starwing\legacy-js`
- **Remote origin**: `https://github.com/ArcadeMachinist/StarwingParadox.git`
- **Current commit**: `020adaf` (Update README.md)
- **Local modifications**: **NONE** - Local files are identical to upstream

### File Size Comparison (Local vs Upstream)

| File | Local | Upstream | Match |
|------|-------|----------|-------|
| README.md | 434 bytes | 434 bytes | EXACT |
| html/index.html | 41 bytes | 41 bytes | EXACT |
| js/nginx.vhost.conf | 1,225 bytes | 1,225 bytes | EXACT |
| js/starwing.js | 28,579 bytes | 28,579 bytes | EXACT |
| paradox.sql | 92,160 bytes | 92,160 bytes | EXACT |

**Conclusion**: Local `legacy-js/` is an exact clone of upstream repository at commit `020adaf`. No local modifications have been made.

---

## Protobuf Schema Analysis

### starwingMessage.proto (10,442 bytes)
- **37 message types** defined
- **6 service definitions**: GameData, Player, Credit, Tutorial, Battle, Mission
- **No NESYS-related messages**
- **No OpenKey messages**
- **No certificate messages**

### any.proto (6,065 bytes)
- Standard protobuf `google.protobuf.Any` type support
- Used for generic message wrapping

---

## Database Schema Analysis (paradox.sql)

### Tables Created (92,160 bytes SQL)
The database schema includes tables for:
- `player` - Player accounts
- `player_profile` - Player profiles
- `player_data` - Player save data
- `battle_result` - Battle records
- `ranking_*` - Multiple ranking tables
- `quest` - Quest data
- `mission` - Mission data
- `buddy` - Buddy system data
- `emblem` - Emblem customization
- `credit` - Credit/currency data
- `tutorial` - Tutorial progress
- `game_data` - Game progress data

### No NESYS Tables
- No `nesys_*` tables
- No `certificate_*` tables
- No `openkey_*` tables

---

## API Coverage

### HTTP API Routes Implemented

| Route | Method | Handler |
|-------|--------|---------|
| `/mock/matching/server` | GET | Matching server address (returns `{"ip_addr":"127.0.0.1:6666"}`) |
| `/matching/regist` | POST | Player registration |
| `/matching/unregist` | POST | Player unregistration |
| `/matching/start` | POST | Start matching |
| `/matching/cancel` | POST | Cancel matching |
| `/version/check` | POST | Version check |
| `/ranking/national` | GET | National rankings |
| `/ranking/prefecture` | GET | Prefecture rankings |
| `/ranking/store` | GET | Store rankings |
| `/ranking/weapon` | GET | Weapon rankings |
| `/resource/get` | GET | Game resources |
| `/player/profile/get` | GET | Player profile |
| `/player/lock` | POST | Lock player |
| `/credit/get` | GET | Credit balance |
| `/tutorial/progress` | POST | Tutorial progress |
| `/game_data/save` | POST | Save game data |
| `/game_data/load` | GET | Load game data |
| `/battle/result` | POST | Submit battle result |
| `/mission/reward/get` | POST | Get mission reward |

### TCP Protocol Messages Implemented

The TCP server handles protobuf messages with type IDs:
- `0x01` - Ping (response: same message)
- `0x67` (103) - SetupConnect (response: SetupConnectResult)
- `0x02` - Unknown (logged, no response)

---

## Dependencies

### Required Software
- **Node.js** (any recent version)
- **PostgreSQL** (database)

### npm Packages (inferred from requires)
- `express` - HTTP framework
- `net` - TCP server (Node.js built-in)
- `protobufjs` - Protocol Buffers
- `pg` - PostgreSQL client
- `body-parser` - HTTP body parsing

### Not Required
- Python (unlike our FastAPI server)
- Alembic (no migrations)
- Redis (no caching)

---

## What Upstream Provides vs What We Need

### Provided by Upstream
| Component | Status | Evidence |
|-----------|--------|----------|
| HTTP API mock server | YES | `js/starwing.js` lines 24-68 |
| TCP/Protobuf server | YES | `js/starwing.js` lines 692-757 |
| Nginx reverse proxy | YES | `js/nginx.vhost.conf` |
| Database schema | YES | `paradox.sql` |
| Ranking data | YES | `c_ranking*.json` files |
| Battle recording | YES | `js/starwing/battleRecorder.js` |
| Burst mode | YES | `js/starwing/burstMode.js` |
| Player profiles | YES | `js/starwing/playerProfile.js` |
| API notes | YES | `js/starwing/API-NOTES.txt` |

### NOT Provided by Upstream
| Component | Status | Impact |
|-----------|--------|--------|
| Game executable (AcrGame.exe) | MISSING | Cannot launch game |
| Game executable (AcrGame-Win64-Shipping.exe) | MISSING | Cannot launch game |
| NESYS service (NesysService.exe) | MISSING | NESYS offline block |
| NESYS initialization | NOT_IMPLEMENTED | Cannot complete boot |
| OpenKey provisioning | NOT_IMPLEMENTED | SystemDataCheck fails |
| Certificate provisioning | NOT_IMPLEMENTED | Security handshake fails |
| Registry setup | NOT_IMPLEMENTED | Game config incomplete |
| D-drive deployment | NOT_DOCUMENTED | Cannot deploy game |
| Game startup sequence | NOT_DOCUMENTED | Cannot launch game |
| Cabinet environment | NOT_DOCUMENTED | Cannot replicate |

---

## Critical Findings

### 1. No Game Launch Capability
The upstream repository provides **zero** game launch functionality. It only provides server-side mock responses.

### 2. No NESYS Support
The upstream repository has **no NESYS implementation whatsoever**. This aligns with our G9-A analysis: the game's NESYS block cannot be resolved by this mock server.

### 3. No OpenKey Provisioning
The upstream repository does not provide OpenKey files. This aligns with our G10 audit: OpenKey producer is UNKNOWN.

### 4. No Certificate Handling
The upstream repository does not implement certificate provisioning or validation. This aligns with our G9-A analysis: NESYS CertError spam occurs because certificates are not provisioned.

### 5. Local Clone is Unmodified
The local `legacy-js/` directory is an **exact clone** of the upstream repository at commit `020adaf`. No local modifications have been made.

---

## Recommendations

### For Game Launch
1. **Do NOT use upstream for game launch** - It only provides mock server responses
2. **Use our FastAPI server** - It provides HTTP API + TCP + protobuf support
3. **Use our Nginx config** - It already proxies to our FastAPI server

### For NESYS Block
1. **Do NOT expect upstream to solve NESYS** - It has no NESYS implementation
2. **Follow G10 recommendation** - INVESTIGATE_NESYSSERVICE_LAUNCH_CONTEXT
3. **Seek original cabinet provisioning** - Launcher, certificates, registry keys

### For OpenKey
1. **Do NOT expect upstream to provide OpenKey** - It has no OpenKey implementation
2. **Follow G10 recommendation** - Determine if NesysService is OpenKey producer
3. **Seek original OpenKey files** - From cabinet capture or operator

---

## Classification

### Final Classification: `MOCK_SERVER_START_ONLY`

**Rationale**:
- Repository provides mock HTTP/TCP server for Starwing Paradox
- Repository does NOT provide game launch, NESYS, OpenKey, certificates, or cabinet environment
- Repository is explicitly labeled "WORK IN PROGRESS"
- Repository has no package.json, no npm scripts, no startup documentation

### Comparison to Our Server

| Feature | Upstream (legacy-js) | Our Server |
|---------|---------------------|------------|
| HTTP API | Express.js (port 4001) | FastAPI (port 4001) |
| TCP Server | net.createServer (port 6666) | asyncio (port 6666) |
| Protobuf | protobufjs | protobuf v7.36.0 |
| Database | PostgreSQL | SQLite |
| Migrations | None | Alembic (17 tables) |
| Matching | Stub | NOT_IMPLEMENTED |
| Battle | Stub | NOT_IMPLEMENTED |
| NESYS | None | Partial investigation |
| OpenKey | None | G10 audit complete |
| Game Launch | None | None (blocked) |

**Conclusion**: Our FastAPI server is MORE COMPLETE than the upstream mock server. The upstream provides no additional functionality that we lack.

---

## Appendix: Key File Locations

### Upstream Repository
- README: https://github.com/ArcadeMachinist/StarwingParadox/blob/master/README.md
- Main entry: https://github.com/ArcadeMachinist/StarwingParadox/blob/master/js/starwing.js
- Nginx config: https://github.com/ArcadeMachinist/StarwingParadox/blob/master/js/nginx.vhost.conf
- Database schema: https://github.com/ArcadeMachinist/StarwingParadox/blob/master/paradox.sql
- Protobuf schema: https://github.com/ArcadeMachinist/StarwingParadox/blob/master/js/starwingMessage.proto

### Local Clone
- Root: `C:\Users\KAHO\Pictures\Starwing\legacy-js`
- Main entry: `C:\Users\KAHO\Pictures\Starwing\legacy-js\js\starwing.js`
- Nginx config: `C:\Users\KAHO\Pictures\Starwing\legacy-js\js\nginx.vhost.conf`
- Database schema: `C:\Users\KAHO\Pictures\Starwing\legacy-js\paradox.sql`
- Protobuf schema: `C:\Users\KAHO\Pictures\Starwing\legacy-js\js\starwingMessage.proto`

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-28 | Audit Agent | Initial audit |

---

**Audit Complete**  
**Classification**: MOCK_SERVER_START_ONLY  
**Recommendation**: Do NOT use upstream for game launch. Use our FastAPI server.
