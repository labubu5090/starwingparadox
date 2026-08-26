# Starwing Paradox — Legacy Route Inventory

> **Generated from**: `legacy-js/js/starwing.js`, `legacy-js/js/starwing/playerProfile.js`, `legacy-js/js/starwing/battleRecorder.js`, `legacy-js/js/starwing/burstMode.js`, `legacy-js/js/starwing/rankingCooker.js`, `legacy-js/js/nginx.vhost.conf`
>
> **Audit date**: 2026-08-26
>
> **Server ports**: HTTP `4001`, TCP/Protobuf `6666`

---

## Table of Contents

1. [HTTP Routes](#http-routes)
2. [TCP Behavior](#tcp-behavior)
3. [Complete Route Table](#complete-route-table)
4. [Route Details](#route-details)

---

## HTTP Routes

All HTTP routes are **POST** only (no GET routes exist in legacy JS).

### Nginx Proxy Configuration

Source: `nginx.vhost.conf:2-45`

```nginx
server {
    listen paradox.yourdomain.com:80;
    server_name paradox.yourdomain.com;
    root /var/www/paradox/html;
    index index.html;
    proxy_set_header x-galaxy-real-ip $remote_addr;
    location /mock {
                proxy_pass http://127.0.0.1:4001;
    }
    location /matching {
                proxy_pass http://127.0.0.1:4001;
    }
    location /version {
                proxy_pass http://127.0.0.1:4001;
    }
    location /ranking {
                proxy_pass http://127.0.0.1:4001;
    }
    location /resource {
                proxy_pass http://127.0.0.1:4001;
    }
    location /player  {
                proxy_pass http://127.0.0.1:4001;
    }
    location /credit  {
                proxy_pass http://127.0.0.1:4001;
    }
    location /tutorial {
                proxy_pass http://127.0.0.1:4001;
    }
    location /game_data {
                proxy_pass http://127.0.0.1:4001;
    }
    location /battle {
                proxy_pass http://127.0.0.1:4001;
    }
    location /mission {
                proxy_pass http://127.0.0.1:4001;
    }
    location / {
               try_files $uri $uri/ =404;
    }
}
```

**Key detail**: Nginx injects `x-galaxy-real-ip` header from `$remote_addr` for ALL proxied requests.

### Global Constants

Source: `starwing.js:28-33`

```javascript
const web_port = 4001;
const pb_port = 6666;
const matcher = "paradox.yourdomain.com:"+pb_port;
const version_main = 70571;
const version_data = 70571;
```

### Common Response Pattern

All routes set these headers:

```javascript
res.set('Content-type','application/json');
res.set('x-galaxy-api-id', req.header('x-galaxy-api-id'));
```

The `x-galaxy-api` header varies per route (detailed below). All responses use HTTP 200 status.

---

## TCP Behavior

### Port and Framing

Source: `starwing.js:80-342`

- **Port**: `6666` (TCP)
- **Bind address**: `0.0.0.0`
- **Framing protocol**: 4-byte little-endian uint32 length prefix, followed by protobuf payload
- **Protobuf message type**: `starwing.PbMessage` (loaded from `starwingMessage.proto`)

Source: `starwing.js:62-78`

```javascript
function PbSendPayload(socket, payload) {
    let PMessage = pbMessageRoot.lookupType("starwing.PbMessage");
    errMsg = PMessage.verify(payload);
    if (errMsg)
        throw Error(errMsg);
    let outMessage = PMessage.create(payload);
    let msgBuffer = PMessage.encode(outMessage).finish();
    let outBuffer = new Buffer.alloc(4+msgBuffer.byteLength);
    outBuffer.writeUInt32LE(msgBuffer.byteLength, 0);
    msgBuffer.copy(outBuffer,4);
    socket.write(outBuffer);
}
```

### Connection Behavior

Source: `starwing.js:80-342`

- Each connecting client is assigned a `connectionNumber` (incrementing counter `cCounter`)
- Client IP is checked against `authorizedClients` array
- If IP not in `authorizedClients`, connection is **destroyed** immediately
- `authorizedClients` is populated by POST `/matching/server` (the HTTP endpoint adds IPs)
- Socket events: `data`, `error`, `timeout`, `end`, `close`, `connection`
- On `close`, the game server is removed from `activeGameServers` array
- On `timeout`, socket is ended with `'Timed out!'`

Source: `starwing.js:87-94`

```javascript
if(authorizedClients. indexOf(socket.remoteAddress) !== -1){
    console.log("["+connectionNumber+"] Found client IP in authorized list");
    console.log("["+connectionNumber+"] Cabinet " + socket.name + " connected");
} else {
    console.log("["+connectionNumber+"] Connection from " + socket.name + " not authorized");
    socket.destroy();
}
```

### Inbound Framing

Source: `starwing.js:96-112`

```javascript
socket.on('data', async function(data) {
    var hexdata = new Buffer.from(data, 'ascii').toString('hex');
    let recvBuffer = new Buffer.from(data, 'ascii');
    let packetLen = recvBuffer.readUIntLE(0, 4);
    let incomingPB = recvBuffer.slice(4, 4+packetLen);
    let PMessage = pbMessageRoot.lookupType("starwing.PbMessage");
    let decoded = PMessage.decode(incomingPB);
    // decoded has: packetId, messageType, and message-specific sub-fields
```

### Message Types Handled

Source: `starwing.js:117-300`

| messageType | Name | Direction | Handler |
|---|---|---|---|
| `0x66` (102) | Ping | Request→Response | Reply with `0x67` + server timestamp |
| `200` | RequestEntryMatching | Request→Response | Returns `ResponseEntryMatching` (msg 201), then `NotifyMatchMade` (302), then `NotifyMatchBegin` (304) |
| `208` | RequestEntryBurstGroup | Request→Response | Returns `ResponseEntryBurstGroup` (209) |
| `210` | RequestChangeBurstGroupMode | Request→Response | Returns `ResponseChangeBurstGroupMode` (211) |
| `214` | RequestUpdateBurstGroup | Request→Response | Returns `ResponseUpdateBurstGroup` (215) |
| `216` | RequestBurstGroupSelect | Request→Response | Returns `ResponseBurstGroupSelect` (217), then `NotifyBurstGroupApply` (308), `NotifyBurstGroupUpdated` (307), `NotifyBurstMade` (310) |
| default | Unhandled | — | Logs "Unhandled ProtoBuf, ID: {type}" |

### Message: Ping (0x66 → 0x67)

Source: `starwing.js:118-123`

```javascript
case 0x66: // ping!
    console.log("Processing message 0x66 (ping), TS:" + decoded.Ping.unixTimestamp);
    payload = { packetId: decoded.packetId, messageType: 0x67, Ping: { unixTimestamp: parseInt(Date.now()/1000)} };
    PbSendPayload(socket,payload);
    break;
```

- **Input fields**: `Ping.unixTimestamp`
- **Output fields**: `packetId` (echoed), `messageType: 0x67`, `Ping.unixTimestamp` (server time)
- **Behavior**: Returns server's current unix timestamp

### Message: RequestEntryMatching (200 → 201 + 302 + 304)

Source: `starwing.js:222-294`

```javascript
case 200: // 100 yen mode
    console.log("Processing message 200 (RequestEntryMatching)");
    console.log("UserId       : "+decoded.RequestEntryMatching.UserId);
    console.log("CardId       : "+decoded.RequestEntryMatching.CardId);
    console.log("MacAddress   : "+decoded.RequestEntryMatching.MacAddress.toString(16).padStart(12, '0').toUpperCase());
    console.log("GameVersion  : "+decoded.RequestEntryMatching.GameVersion);
    console.log("LocationId   : "+decoded.RequestEntryMatching.LocationId);
    console.log("LocationName : "+decoded.RequestEntryMatching.LocationName);
    console.log("PlayMode     : "+decoded.RequestEntryMatching.PlayMode);

    payload = { packetId: decoded.packetId, messageType: 201, ResponseEntryMatching: { messageId: 1, timeout: 45 } };
    PbSendPayload(socket,payload);

    // send another fake msg
    payload = { packetId: parseInt(decoded.packetId)+1, messageType: 302, NotifyMatchMade:
            { Match: {
                    Team:[{
                        PlayerCount: 2,
                        Player: [{
                            PlayerId: 10010,
                            MacAddress: 247207015480323,
                            CardId: 7020392000000000,
                            PlayerName: "ArcadeMachinist",
                            PlayerRank: 20,
                            BuddyId: 5,
                            LocationId: 77,
                            LocationName: "ZenGarden",
                            Intrude: false,
                            Rank2on2: 20
                        },
                            {
                                PlayerId: 10011,
                                MacAddress: 12346,
                                CardId: 7020392000000001,
                                PlayerName: "LordCereth",
                                PlayerRank: 20,
                                BuddyId: 2,
                                LocationId: 77,
                                LocationName: "ZenGarden",
                                Rank2on2: 20
                            }
                        ]
                    }
                    ],
                    MatchId: 12345,
                    State: 1,
                    PlayMode: 101,
                    Difficulty: 0,
                    CoopModeIndex: 0,
                    MatchGroup: 0,
                    MatchMode: 0,
                    StageId: 20001,
                    Version: "70571",
                    VsCPU: true,
                    GameMode: 0
                },
                ds: { ServerId: 6789, State: 1, address: "192.168.0.55", version: "70571", language: "0" },
                MatchType: 1,
                GameMode: 0,
                StageId: 20001
            } };
    PbSendPayload(socket,payload);

    payload = { packetId: decoded.packetId, messageType: 304, NotifyMatchBegin: { MatchId: 12345 } };
    PbSendPayload(socket,payload);
    break;
```

**3 messages sent in sequence:**

1. **ResponseEntryMatching** (msgType 201): `{messageId: 1, timeout: 45}` — static
2. **NotifyMatchMade** (msgType 302): Entirely hardcoded fake match with two players, `MatchId: 12345`, `VsCPU: true`, `StageId: 20001`
3. **NotifyMatchBegin** (msgType 304): `{MatchId: 12345}` — static

- **Input fields used**: `UserId`, `CardId`, `MacAddress`, `GameVersion`, `LocationId`, `LocationName`, `PlayMode` (all logged, none used in response)
- **Deterministic**: Yes (entirely hardcoded response)

### Message: RequestEntryBurstGroup (208 → 209)

Source: `starwing.js:125-129`, `burstMode.js:158-209`

```javascript
case 208:
    console.log("Processing message 208 (RequestEntryBurstGroup) aka register for coop");
    payload = await burstHandler.RequestEntryBurstGroup(decoded.packetId, decoded.RequestEntryBurstGroup, socket);
    PbSendPayload(socket,payload);
    break;
```

**burstMode.js handler**:

```javascript
async RequestEntryBurstGroup(packetId,request,socket) {
    console.log("( 1) PlayerId       : "+request.PlayerId);
    console.log("( 2) CardId         : "+request.CardId);
    console.log("( 3) MacAddress     : "+request.MacAddress.toString(16).padStart(12, '0').toUpperCase());
    console.log("( 4) Version        : "+request.Version);
    console.log("( 5) LocationId     : "+request.LocationId);
    console.log("( 6) LocationName   : "+request.LocationName);
    console.log("( 7) PlayMode       : "+request.PlayMode);
    console.log("( 8) Mode           : "+request.Mode);
    console.log("( 9) PlayerName     : "+request.PlayerName);
    console.log("(10) PlayerRank     : "+request.PlayerRank);
    console.log("(11) TitleId        : "+request.TitleId);
    console.log("(12) Emblem         : "+request.Emblem.pBg.PartId + "/"+request.Emblem.pMa.PartId+ "/" +request.Emblem.pSb.PartId);
    console.log("(13) BurstMode      : "+request.BurstMode);
    console.log("(14) Rank2on2       : "+request.Rank2on2);
    console.log("(15) TitleId2on2    : "+request.TitleId2on2);
    console.log("(16) Emblem2on2     : "+request.Emblem2on2.pBg.PartId + "/"+request.Emblem2on2.pMa.PartId+ "/" +request.Emblem2on2.pSb.PartId);
    console.log("(17) GameMode       : "+request.GameMode);

    let Player = new Object();
    Player.PlayerId = parseInt(request.PlayerId);
    Player.CardId = parseInt(request.CardId);
    Player.MacAddress = parseInt(request.MacAddress);
    Player.Version   =request.Version;
    Player.LocationId   =parseInt(request.LocationId);
    Player.LocationName  =request.LocationName;
    Player.PlayMode       =parseInt(request.PlayMode);
    Player.Mode           =parseInt(request.Mode);
    Player.PlayerName   =request.PlayerName;
    Player.PlayerRank   =parseInt(request.PlayerRank);
    Player.TitleId        =parseInt(request.TitleId);
    Player.Emblem      =request.Emblem;
    Player.BurstMode    =parseInt(request.BurstMode);
    Player.Rank2on2     =parseInt(request.Rank2on2);
    Player.TitleId2on2  =parseInt(request.TitleId2on2);
    Player.Emblem2on2   = request.Emblem2on2;
    Player.GameMode       = parseInt(request.GameMode);

    // Remove existing player with same ID
    this.players = this.players.filter(function(value, index, arr){
        return value.PlayerId !=  Player.PlayerId;
    });
    Player.ts = new Date().getTime() / 1000;
    Player.socket = socket;
    this.players.push(Player);

    let payload  = { packetId: packetId, messageType: 209, ResponseEntryBurstGroup: { MessageId: 1, Timeout: 120, BurstNumMax: 2  } };
    return  payload;
}
```

- **Input fields**: `PlayerId`, `CardId`, `MacAddress`, `Version`, `LocationId`, `LocationName`, `PlayMode`, `Mode`, `PlayerName`, `PlayerRank`, `TitleId`, `Emblem` (sub: `pBg.PartId`, `pMa.PartId`, `pSb.PartId`), `BurstMode`, `Rank2on2`, `TitleId2on2`, `Emblem2on2`, `GameMode`
- **Side effect**: Adds player to `this.players` array (in-memory, replaces existing with same PlayerId)
- **Response**: Static `{MessageId:1, Timeout:120, BurstNumMax:2}`
- **Deterministic**: Yes

### Message: RequestChangeBurstGroupMode (210 → 211)

Source: `starwing.js:137-143`, `burstMode.js:110-157`

```javascript
case 210:
    payload = await burstHandler.RequestChangeBurstGroupMode(decoded.packetId, decoded.RequestChangeBurstGroupMode);
    PbSendPayload(socket,payload);
    break;
```

**burstMode.js handler**:

```javascript
async RequestChangeBurstGroupMode(packetId,request) {
    console.log("PlayerId      : "+request.PlayerId);
    console.log("Mode          : "+request.Mode);
    if (typeof request.StageId != 'undefined')
        console.log("StageId       : "+request.StageId);

    // Kill room if already exists
    this.rooms = this.rooms.filter(function(value, index, arr){
        if (typeof value.Player[0].PlayerId == 'undefined') return true;
        return value.Player[0].PlayerId !=  request.PlayerId;
    });

    // Get current player from saved data
    let roomOwner;
    for (let i = 0; i < this.players.length; i++) {
        if (this.players[i].PlayerId == request.PlayerId) roomOwner = this.players[i];
    }

    let newRoom = {
        Player:[ roomOwner ],
        MessageId: 1,
        Result: 1
    };
    if (typeof request.StageId != 'undefined') newRoom.StageId = request.StageId;
    newRoom.Player[0].MateNum = 0;
    this.rooms.push(newRoom);

    for (let i = 0; i < this.rooms.length; i++) {
        if(this.rooms[i].Player[0].PlayerId == request.PlayerId) newRoom.Player[0].Number = i+1;
    }

    let payload = { packetId: packetId, messageType: 211, ResponseChangeBurstGroupMode:  newRoom, Timeout: 100 };
    return payload;
}
```

- **Input fields**: `PlayerId`, `Mode`, `StageId` (optional)
- **Side effect**: Removes existing room owned by this player, creates new room, adds to `this.rooms`
- **Response**: Echoes room object with `Player` array, `MessageId:1`, `Result:1`, `Timeout:100`
- **Dynamic values**: `Player[0].Number` = room index+1, `Player[0].MateNum` = 0
- **Deterministic**: Yes (depends on in-memory room state)

### Message: RequestUpdateBurstGroup (214 → 215)

Source: `starwing.js:216-220`, `burstMode.js:94-109`

```javascript
case 214:
    console.log("Processing message 210 (RequestUpdateBurstGroup) aka ListRooms");
    payload = await burstHandler.RequestUpdateBurstGroup(decoded.packetId, decoded.RequestUpdateBurstGroup);
    PbSendPayload(socket,payload);
    break;
```

**burstMode.js handler**:

```javascript
async RequestUpdateBurstGroup(packetId, request) {
    let pRooms = [];
    for (let i = 0; i < this.rooms.length; i++) {
        this.rooms[i].Player[0].Number=i+1;
        this.rooms[i].Player[0].MateNum=this.rooms[i].Player.length-1;
        pRooms.push(this.rooms[i].Player[0]);
    }
    let payload = { packetId: packetId, messageType: 215, ResponseUpdateBurstGroup: { MessageId: 5,
            Result: pRooms.length, Player: pRooms, Timeout: 300 } };
    return payload;
}
```

- **Input fields**: (none used from request)
- **Side effect**: Mutates `Number` and `MateNum` on each room's Player[0]
- **Response**: `MessageId:5`, `Result` = room count, `Player` = array of room owners, `Timeout:300`
- **Dynamic values**: `Result` = number of rooms, `Player` = list of room owner objects
- **Deterministic**: Depends on in-memory state

### Message: RequestBurstGroupSelect (216 → 217 + 308 + 307 + 310)

Source: `starwing.js:131-135`, `burstMode.js:28-93`

```javascript
case 216:
    console.log("Processing message 216 (RequestBurstGroupSelect) aka Select Room");
    payload = await burstHandler.RequestBurstGroupSelect(decoded.packetId, decoded.RequestBurstGroupSelect);
    //PbSendPayload(socket,payload);  // NOTE: commented out in main switch, but sent inside handler
    break;
```

**burstMode.js handler**:

```javascript
async RequestBurstGroupSelect (packetId, request) {
    console.log("PlayerId      : "+request.PlayerId);
    console.log("MateId        : "+request.MateId);

    // locate joining player
    let joiner = new Object();
    for (let i = 0; i < this.players.length; i++) {
        if (this.players[i].PlayerId == request.PlayerId) joiner = this.players[i];
    }

    // locate room to join, update PlayerCount and push player into the room
    for (let i = 0; i < this.rooms.length; i++) {
        if (this.rooms[i].Player[0].PlayerId == parseInt(request.MateId)) {
            this.rooms[i].Player[0].MateNum++;
            this.rooms[i].Player.push(joiner);
        }
    }

    // Send ResponseBurstGroupSelect to joiner
    let payload = { packetId: packetId, messageType: 217, ResponseBurstGroupSelect: { MessageId: 1, Timeout: 100, Result: 0  } };
    this.pbSendPayload(joiner.socket, payload);

    // Send NotifyBurstGroupApply + NotifyBurstGroupUpdated to all in room
    let tRoomPlayers;
    for (let i = 0; i < this.rooms.length; i++) {
        if (this.rooms[i].Player[0].PlayerId == parseInt(request.MateId)) {
            let payload = { packetId: packetId, messageType: 308, NotifyBurstGroupApply : { Player: this.rooms[i].Player  } };
            let payload2 = { packetId: packetId, messageType: 307, NotifyBurstGroupUpdated : { Player: this.rooms[i].Player, StageId: 20001  } };
            for (let j = 0; j < this.rooms[i].Player.length; j++) {
                let player = this.rooms[i].Player[j];
                this.pbSendPayload(player.socket, payload);
                this.snooze(10);
                this.pbSendPayload(player.socket, payload2);
            }
            tRoomPlayers = this.rooms[i].Player;
        }
    }

    // Send NotifyBurstMade to all players (after 500ms delay)
    this.snooze(500);
    let payload2 = { packetId: 111, messageType: 310, NotifyBurstMade: {
            BurstGroupId: 1, BurstNum: 2, StageId: 20001,
            Player: tRoomPlayers
        }
    }
    this.pbSendPayload(this.players[0].socket, payload2);
    this.pbSendPayload(this.players[1].socket, payload2);

    // NotifyBurstMeets (commented out in source)
    payload2 = { packetId: 111, messageType: 311, NotifyBurstMeets: {
            BurstGroupId: 1, BurstNum: 2,
            Player: tRoomPlayers, State: 1
        }
    }
    // this.pbSendPayload(this.players[0].socket, payload2);  // commented out
}
```

- **Input fields**: `PlayerId`, `MateId`
- **Side effect**: Adds joiner to room, increments MateNum
- **Messages sent**:
  1. `ResponseBurstGroupSelect` (217) to joiner: `{MessageId:1, Timeout:100, Result:0}`
  2. `NotifyBurstGroupApply` (308) to all room members: `{Player: [...]}`
  3. `NotifyBurstGroupUpdated` (307) to all room members: `{Player: [...], StageId: 20001}`
  4. `NotifyBurstMade` (310) to players[0] and players[1]: `{BurstGroupId:1, BurstNum:2, StageId:20001, Player: [...]}`
  5. `NotifyBurstMeets` (311) — **commented out**, not actually sent

---

## HTTP Route Details

### Route: POST /matching/server

**Source**: `starwing.js:345-369`

**Required headers**:
- `x-galaxy-api-id` (echoed back)
- `x-galaxy-real-ip` (used for IP authorization side effect; injected by nginx)

**Request body**: JSON (logged, not used)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**: Static JSON string

```json
{
    "ip_addr": "paradox.yourdomain.com:6666"
}
```

**Side effect**: If `x-galaxy-real-ip` header is present and IP not already in `authorizedClients`, it is added:

```javascript
if (req.header('x-galaxy-real-ip')) {
    if(authorizedClients. indexOf(req.header('x-galaxy-real-ip')) !== -1){
        console.log("Client IP " + req.header('x-galaxy-real-ip') + " already authorized");
    } else {
        console.log("Added Client IP " + req.header('x-galaxy-real-ip') + " to AcrProto authorization list");
        authorizedClients.push(req.header('x-galaxy-real-ip'));
    }
}
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes (value is constant)
**Generic success**: No — returns specific `ip_addr` field

---

### Route: POST /mock/matching/server

**Source**: `starwing.js:371-387`

Identical to `/matching/server` but **without** the IP authorization side effect.

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "ip_addr": "paradox.yourdomain.com:6666"
}
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: No — returns `ip_addr`

---

### Route: POST /mock/* (fallback)

**Source**: `starwing.js:389-405`

Catches any `/mock/` sub-path not matching `/mock/matching/server`.

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "ip_addr": "paradox.yourdomain.com:6666"
}
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes

---

### Route: POST /version

**Source**: `starwing.js:407-426`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**: JSON (logged, not used)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "client_version": "70571",
    "data_version": "70571",
    "stage_ids": []
}
```

**Source code**:
```javascript
res.send("{\n" +
    "\t\"client_version\": \"" + version_main + "\",\n" +
    "\t\"data_version\": \"" + version_data + "\",\n" +
    "\t\"stage_ids\": []"+
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes (constant values)
**Generic success**: No — returns version info

---

### Route: POST /matching/match_id/generate

**Source**: `starwing.js:428-438`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**: JSON (logged, not used)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "match_id": <random_integer_10000_to_99999>
}
```

**Source code**:
```javascript
let matchId = getRandomInt(10000,99999);
res.send("{\"match_id\":"+matchId+"}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: No — random integer in range [10000, 99999)
**Generic success**: No — returns `match_id` field

---

### Route: POST /matching/* (fallback)

**Source**: `starwing.js:440-449`

Catches any `/matching/` sub-path not matching `/matching/server` or `/matching/match_id/generate`.

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{}
```

**Source code**:
```javascript
res.send("{}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: No — returns empty `{}`

---

### Route: POST /ranking/national

**Source**: `starwing.js:458-461`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**: JSON (logged, not used)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: ranking/national`
- `x-galaxy-api-id: {echoed from request}`

**Response body**: Raw JSON from file `starwing/c_rankingNational.json`

**Source code**:
```javascript
res.set('x-galaxy-api', 'ranking/national');
res.send(fs.readFileSync('starwing/c_rankingNational.json','utf8'));
```

**Database reads**: None (file read)
**Database writes**: None
**Deterministic**: Yes (static file)
**Generic success**: No — returns full ranking data

---

### Route: POST /ranking/location

**Source**: `starwing.js:462-465`

**Response headers**:
- `x-galaxy-api: ranking/location`

**Response body**: Raw JSON from file `starwing/c_rankingStore.json`

**Source code**:
```javascript
res.set('x-galaxy-api', 'ranking/location');
res.send(fs.readFileSync('starwing/c_rankingStore.json','utf8'));
```

**Database reads**: None (file read)
**Database writes**: None
**Deterministic**: Yes

---

### Route: POST /ranking/prefecture

**Source**: `starwing.js:466-469`

**Response headers**:
- `x-galaxy-api: ranking/prefecture`

**Response body**: Raw JSON from file `starwing/c_rankingPrefecture.json`

**Source code**:
```javascript
res.set('x-galaxy-api', 'ranking/prefecture');
res.send(fs.readFileSync('starwing/c_rankingPrefecture.json','utf8'));
```

**Database reads**: None (file read)
**Database writes**: None
**Deterministic**: Yes

---

### Route: POST /ranking/event

**Source**: `starwing.js:470-473`

**Response headers**:
- `x-galaxy-api: ranking/event`

**Response body**: Raw JSON from file `starwing/c_rankingEvent.json`

**Source code**:
```javascript
res.set('x-galaxy-api', 'ranking/event');
res.send(fs.readFileSync('starwing/c_rankingEvent.json','utf8'));
```

**Database reads**: None (file read)
**Database writes**: None
**Deterministic**: Yes

---

### Route: POST /ranking/weapon

**Source**: `starwing.js:474-480`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**:
```json
{
    "role_id": <string>
}
```

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: ranking/event` ← **BUG**: should be `ranking/weapon`
- `x-galaxy-api-id: {echoed from request}`

**Response body**: JSON from file `starwing/c_rankingWeapon_r{role_id}.json` with `role_id` field injected

**Source code**:
```javascript
res.set('x-galaxy-api', 'ranking/event');
console.log("Weapon id: "+req.body.role_id);
let jWeapons = JSON.parse(fs.readFileSync('starwing/c_rankingWeapon_r'+req.body.role_id+'.json','utf8'));
jWeapons.role_id = req.body.role_id;
res.send(JSON.stringify(jWeapons,null,4));
```

**Database reads**: None (file read, path depends on `req.body.role_id`)
**Database writes**: None
**Deterministic**: Yes (file read, but `role_id` injected into response)
**Depends on request values**: Yes — `role_id` determines which file is read
**Error behavior**: If file doesn't exist, `fs.readFileSync` will throw unhandled exception → 500

---

### Route: POST /ranking/* (fallback)

**Source**: `starwing.js:481-485`

```javascript
res.set('x-galaxy-api', 'ranking/unknown');
res.send("{}");
```

**NOTE**: The `default` keyword is misspelled as `deafult` in the switch statement (line 481), so this case **never actually runs**. The Express route still matches, but the switch's default branch is dead code. The response will still be `{}` from the empty `res.send("{}")` call that follows the switch.

**Response headers**:
- `x-galaxy-api: ranking/unknown` (if switch default executed)
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{}
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes

---

### Route: POST /player/profile/load

**Source**: `starwing.js:488-507`, `playerProfile.js:26-73` (initWithNesys), `playerProfile.js:297-350` (getProfile)

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**:
```json
{
    "nesys_id": <integer>
}
```

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: player/profile`
- `x-galaxy-api-id: {echoed from request}`

**Source code** (starwing.js):
```javascript
res.set('x-galaxy-api', 'player/profile');
let pt = new pp.PlayerProfile();
await pt.initWithNesys(pgdb,req.body.nesys_id);
res.send(JSON.stringify(await pt.getProfile()));
```

**Behavior**:
1. `initWithNesys(pgdb, nesys_id)`:
   - If `nesys_id` is 0, null, or undefined: returns false (no response sent correctly)
   - Queries: `SELECT * FROM player WHERE nesys_id=$1`
   - If no row found: **INSERT** `INSERT INTO player(nesys_id) VALUES ($1) RETURNING player_id`, then re-SELECT
   - Populates `this.Player` with all columns from `player` table

2. `getProfile()`:
   - Queries: `SELECT COUNT(id) AS same_day_login_count FROM player_logins WHERE date_trunc('day', ts_when) = $1 AND player_id=$2`
   - Queries: `SELECT COUNT(DISTINCT(date_trunc('day', ts_when))) AS total_login_days FROM player_logins WHERE player_id=$1`
   - Sets `consecutive_login_days` = `same_day_login_count ? 1 : 0`
   - Sets `last_pref_ranking_order_id = 0`
   - Sets `pref_ranking_top_player_count = 0`
   - Sets `official_player_type_id = 0`
   - Builds hardcoded emblem object (all zeros)
   - Queries: `SELECT progress_key,status FROM player_progress WHERE player_id=$1`
   - Returns entire `this.Player` object (all columns from `player` table + computed fields + `progresses`)

**Database reads**:
1. `SELECT * FROM player WHERE nesys_id=$1`
2. `SELECT * FROM player WHERE player_id=$1` (after insert)
3. `SELECT COUNT(id) ... FROM player_logins WHERE ... AND player_id=$1`
4. `SELECT COUNT(DISTINCT(...)) FROM player_logins WHERE player_id=$1`
5. `SELECT progress_key,status FROM player_progress WHERE player_id=$1`

**Database writes**:
1. `INSERT INTO player(nesys_id) VALUES ($1) RETURNING player_id` (only if nesys_id not found)

**Deterministic**: No (depends on DB state, creates player if not found)
**Generic success**: No — returns full player profile

**Response shape** (all fields from `player` table plus):
```json
{
    "player_id": <int>,
    "nesys_id": <int>,
    "same_day_login_count": <int>,
    "total_login_days": <int>,
    "consecutive_login_days": 0|1,
    "last_pref_ranking_order_id": 0,
    "pref_ranking_top_player_count": 0,
    "official_player_type_id": 0,
    "emblem": {
        "outline": {"part_id":0, "offset":[0,0], "scale":[1,1], "angle":0},
        "main_design": {"part_id":0, "offset":[0,0], "scale":[1,1], "angle":0},
        "sub_design": {"part_id":0, "offset":[0,0], "scale":[1,1], "angle":0}
    },
    "progresses": [{"progress_key":"...", "status":"..."}]
}
```

---

### Route: POST /player/login

**Source**: `starwing.js:509-531`, `playerProfile.js:6-25` (initWithPlayerID), `playerProfile.js:351-392` (playerLogin)

**Required headers**:
- `x-galaxy-api-id` (echoed)
- `x-galaxy-real-ip` (used for IP logging)

**Request body**:
```json
{
    "player_id": <integer>,
    "location_id": <integer>,
    "client_version": <string>,
    "data_version": <string>
}
```

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: player/login`
- `x-galaxy-api-id: {echoed from request}`

**Source code** (starwing.js):
```javascript
res.set('x-galaxy-api', 'player/login');
let pt = new pp.PlayerProfile();
await pt.initWithPlayerID(pgdb,req.body.player_id);
res.send(JSON.stringify(await pt.playerLogin(req.header('x-galaxy-real-ip'),req.body)));
```

**Behavior**:
1. `initWithPlayerID`: `SELECT * FROM player WHERE player_id=$1` — returns false if not found
2. `playerLogin(ip_addr, req_body)`:
   - INSERT into `player_logins`
   - SELECT progresses from `player_progress`
   - SELECT login counts from `player_logins`
   - Returns player data with login-specific fields

**Database reads**:
1. `SELECT * FROM player WHERE player_id=$1`
2. `SELECT progress_key,status FROM player_progress WHERE player_id=$1`
3. `SELECT COUNT(id) AS same_day_login_count FROM player_logins WHERE date_trunc('day', ts_when) = $1 AND player_id=$2`
4. `SELECT COUNT(DISTINCT(date_trunc('day', ts_when))) AS total_login_days FROM player_logins WHERE player_id=$1`

**Database writes**:
1. `INSERT INTO player_logins (player_id,ip_addr,ts_when,location_id,client_version,data_version) VALUES ($1,$2,now(),$3,$4,$5)`

**Response shape** (all `player` table fields plus):
```json
{
    "player_id": <int>,
    "progresses": [{"progress_key":"...", "status":"..."}],
    "greeting_ids": [1],
    "battle_count": 3,
    "same_day_login_count": <int>,
    "total_login_days": <int>,
    "consecutive_login_days": 0|1,
    "burst_match": false,
    "next_burst_begin": "",
    "next_burst_end": "",
    "open_boss_matches": [20001],
    "next_boss_matches": [20002]
}
```

**Deterministic**: No (DB-dependent)
**Generic success**: No — returns full player login state

---

### Route: POST /player/login_bonus

**Source**: `starwing.js:534-554`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**: JSON (logged, not used)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: player/login` ← **NOTE**: not `*/\*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "result": 1,
    "login_bonuses": [],
    "update_items": {}
}
```

**Source code**:
```javascript
res.set('x-galaxy-api', 'player/login');
res.send("{\n" +
    "\"result\": 1, " +
    "\"login_bonuses\": [],"+
    "\"update_items\": {}"+
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: No — returns `result:1` with `login_bonuses` and `update_items`

---

### Route: POST /player/register

**Source**: `starwing.js:557-574`, `playerProfile.js:394-436` (playerRegister)

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**:
```json
{
    "player_id": <integer>,
    "player_name": "...",
    "progresses": "[{\"progress_key\":\"...\",\"status\":\"...\"}]"
}
```

(Plus any additional fields that are dynamically written to the `player` table)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: player/register`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "result": 1
}
```

**Source code**:
```javascript
res.set('x-galaxy-api', 'player/register');
let pt = new pp.PlayerProfile();
await pt.initWithPlayerID(pgdb,req.body.player_id);
await pt.playerRegister(req.body);
res.send("{\n" + "\"result\": 1" + "}");
```

**Behavior** (`playerRegister`):
1. Builds dynamic UPDATE query: `UPDATE player SET {key}=$N ... WHERE player_id=$M` for all fields in `req_body` except `player_id` and `progresses`
2. Parses `progresses` (JSON string) and UPSERTs each into `player_progress`

**Database reads**:
1. `SELECT * FROM player WHERE player_id=$1`

**Database writes**:
1. `UPDATE player SET {dynamic_fields} WHERE player_id=$N`
2. For each progress: `INSERT INTO player_progress (player_id, progress_key, status) VALUES ($1,$2,$3) ON CONFLICT (player_id,progress_key) DO UPDATE SET status = excluded.status`

**Deterministic**: No (DB-dependent)
**Generic success**: Yes — always returns `{"result":1}` regardless of outcome

---

### Route: POST /player/* (fallback)

**Source**: `starwing.js:576-592`

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "result": 1
}
```

**Source code**:
```javascript
res.send("{\n" +
    "\"result\": 1" +
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: Yes

---

### Route: POST /mission/* (fallback)

**Source**: `starwing.js:595-614`

**Request body**: JSON (logged, not used)

Comment in source documents known sub-route:
```
// mission/reward/get {"player_id":"10010","mission_id":"136001","mission_reward_ids":"[7102551]"}
// waits for intimacy_reward_ids:[], update_items: {}, update_missions: []
```

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{}
```

**Source code**:
```javascript
res.send("{\n" +
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: No — returns empty `{}` (not `{"result":1}`)

---

### Route: POST /credit/* (fallback)

**Source**: `starwing.js:616-631`

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{}
```

**Source code**:
```javascript
res.send("{\n" +
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: No — returns empty `{}`

---

### Route: POST /tutorial/* (fallback)

**Source**: `starwing.js:634-650`

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "result": 1
}
```

**Source code**:
```javascript
res.send("{\n" +
    "\"result\": 1" +
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: Yes

---

### Route: POST /game_data/load/mission

**Source**: `starwing.js:653-676`, `playerProfile.js:74-86`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**:
```json
{
    "player_id": <integer>
}
```

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: game_data/load` ← **NOTE**: different from actual path
- `x-galaxy-api-id: {echoed from request}`

**Source code** (starwing.js):
```javascript
res.set('x-galaxy-api', 'game_data/load');
let pt = new pp.PlayerProfile();
await pt.initWithPlayerID(pgdb,req.body.player_id);
let pgd = await pt.playerLoadGameDataMissions();
res.send(JSON.stringify(pgd,0,4));
```

**Behavior** (`playerLoadGameDataMissions`):
```javascript
async playerLoadGameDataMissions() {
    if (this.Player.player_id){
        let gameData = new Object();
        let qtext = "SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1";
        let res = await this.db.query(qtext, [this.Player.player_id]);
        gameData.missions = [];
        for(let k in res.rows) {
            gameData.missions.push(res.rows[k]);
        }
        return gameData;
    }
}
```

**Database reads**:
1. `SELECT * FROM player WHERE player_id=$1` (via initWithPlayerID)
2. `SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1`

**Database writes**: None
**Deterministic**: No (DB-dependent)
**Generic success**: No — returns `{"missions":[...]}`

**Response shape**:
```json
{
    "missions": [
        {
            "mission_id": "...",
            "clear_count": <int>,
            "clear_num": <int>,
            "status": <int>,
            "mission_status": <int>
        }
    ]
}
```

---

### Route: POST /game_data/load

**Source**: `starwing.js:677-698`, `playerProfile.js:87-296`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**:
```json
{
    "player_id": <integer>
}
```

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: game_data/load`
- `x-galaxy-api-id: {echoed from request}`

**Source code** (starwing.js):
```javascript
res.set('x-galaxy-api', 'game_data/load');
let pt = new pp.PlayerProfile();
await pt.initWithPlayerID(pgdb,req.body.player_id);
let pgd = await pt.playerLoadGameData();
res.send(JSON.stringify(pgd,0,4));
```

**Database reads** (all via `playerLoadGameData`):
1. `SELECT * FROM player WHERE player_id=$1`
2. `SELECT COUNT(id) AS same_day_login_count FROM player_logins WHERE date_trunc('day', ts_when) = $1 AND player_id=$2`
3. `SELECT COUNT(DISTINCT(date_trunc('day', ts_when))) AS total_login_days FROM player_logins WHERE player_id=$1`
4. `SELECT buddy_id, buddy_key, buddy_value FROM player_buddies WHERE player_id=$1`
5. `SELECT progress_key,status FROM player_progress WHERE player_id=$1`
6. `SELECT option_key,value_num FROM player_options WHERE player_id=$1`
7. `SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1`
8. `SELECT * FROM player_buddy_win_poses WHERE player_id=$1`
9. `SELECT * FROM player_emblems WHERE player_id=$1`
10. `SELECT * FROM player_emblem_parts WHERE player_id=$1`
11. `SELECT * FROM player_titles WHERE player_id=$1`
12. `SELECT * FROM player_line_colors WHERE player_id=$1`
13. `SELECT * FROM player_mecha_sets WHERE player_id=$1`
14. `SELECT * FROM player_mecha_set_parts WHERE player_id=$1`
15. `SELECT * FROM player_mecha_colors WHERE player_id=$1`
16. `SELECT * FROM player_weapon_set WHERE player_id=$1`
17. `SELECT * FROM player_weapon_set_slots WHERE player_id=$1`
18. `SELECT * FROM player_side_weapons WHERE player_id=$1`

**Database writes**: None

**Deterministic**: No (DB-dependent)
**Generic success**: No — returns comprehensive game data

**Response shape**:
```json
{
    "player": { ...all player fields + computed fields... },
    "buddies": [{"buddy_id":<int>, "buddy_key":"...", "buddy_value":"..."}],
    "progresses": [{"progress_key":"...", "status":"..."}],
    "options": [{"option_key":"...", "value_num":<int>}],
    "missions": [{"mission_id":"...", "clear_count":<int>, "clear_num":<int>, "status":<int>, "mission_status":<int>}],
    "buddy_skills": [],
    "buddy_win_poses": [{"buddy_id":<int>, "win_pose_id":<int>, "status":<int>}],
    "emblems": [{"emblem_id":<int>, "outline":{...}, "main_design":{...}, "sub_design":{...}, "status":<int>, "editable":<int>}],
    "emblem_parts": [{"part_id":<int>, "status":<int>}],
    "titles": [{"title_id":<int>, "status":<int>}],
    "line_colors": [{"line_color_id":<int>, "status":<int>}],
    "mecha_sets": [{"mecha_set_id":<int>, ...}],
    "mecha_set_parts": [{"mecha_set_id":<int>, "part_id":<int>, "mecha_id":<int>, "design_id":<int>, "color_id":<int>}],
    "mecha_colors": [{"mecha_color_id":<int>, "status":<int>}],
    "weapon_set": [{"weapon_set_id":<int>, ...}],
    "weapon_set_slots": [{"weapon_set_id":<int>, "slot_id":<int>, "weapon_id":<int>, ...}],
    "side_weapons": [{"side_weapon_id":<int>, ...}],
    "violation_point": 0,
    "winning_streaks_2on2": 1
}
```

---

### Route: POST /game_data/save

**Source**: `starwing.js:700-720`, `playerProfile.js:438-722`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**: JSON with `player_id` plus any number of data categories. Each category is a JSON string that gets `JSON.parse()`d.

```json
{
    "player_id": "<int>",
    "options": "[{\"option_key\":\"...\",\"value_num\":<int>}]",
    "buddies": "[{\"buddy_id\":<int>,\"buddy_key\":\"...\",\"buddy_value\":\"...\"}]",
    "progresses": "[{\"progress_key\":\"...\",\"status\":\"...\"}]",
    "missions": "[{\"mission_id\":\"...\",\"clear_count\":<int>,\"clear_num\":<int>,\"status\":<int>,\"mission_status\":<int>}]",
    "titles": "[{\"title_id\":<int>,\"status\":<int>}]",
    "emblems": "[{\"emblem_id\":<int>,\"outline\":{\"part_id\":<int>,\"offset\":[x,y],\"scale\":[x,y],\"angle\":<int>},...}]",
    "emblem_parts": "[{\"part_id\":<int>,\"status\":<int>}]",
    "mecha_sets": "[{\"mecha_set_id\":<int>,...}]",
    "mecha_set_parts": "[{\"mecha_set_id\":<int>,\"part_id\":<int>,\"mecha_id\":<int>,\"design_id\":<int>,\"color_id\":<int>}]",
    "buddy_win_poses": "[{\"buddy_id\":<int>,\"win_pose_id\":<int>,\"status\":<int>}]",
    "line_colors": "[{\"line_color_id\":<int>,\"status\":<int>}]",
    "mecha_colors": "[{\"mecha_color_id\":<int>,\"status\":<int>}]",
    "weapon_set": "[{\"weapon_set_id\":<int>,\"use_count\":<int>,\"use_time\":<int>,\"status\":<int>}]",
    "weapon_set_slots": "[{\"weapon_set_id\":<int>,\"slot_id\":<int>,\"weapon_id\":<int>,\"use_count\":<int>,\"use_time\":<int>}]",
    "side_weapons": "[{\"side_weapon_id\":<int>,\"use_count\":<int>,\"use_time\":<int>,\"status\":<int>}]",
    "title_id_2on2": <int>,
    "mecha_set_id": <int>,
    "emblem_id_2on2": <int>,
    "line_color_id_2on2": <int>,
    "side_weapon_id": <int>,
    "mecha_preset_id": <int>,
    "rank_point": <int>,
    "max_rank_id": <int>,
    "rank_point_2on2": <int>,
    "max_rank_id_2on2": <int>,
    "buddy_id": <int>
}
```

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: game_data/save`
- `x-galaxy-api-id: {echoed from request}`

**Source code** (starwing.js):
```javascript
res.set('x-galaxy-api', 'game_data/save');
let pt = new pp.PlayerProfile();
await pt.initWithPlayerID(pgdb,req.body.player_id);
let gd = await pt.playerSaveGameData(req.body);
res.send(JSON.stringify(gd,0,4));
```

**Database reads**:
1. `SELECT * FROM player WHERE player_id=$1` (via initWithPlayerID)
2. `SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1` (appended to response after all saves)

**Database writes** (per category, all use UPSERT pattern):

| Category | Table | Query |
|---|---|---|
| `options` | `player_options` | `INSERT INTO player_options (player_id, option_key, value_num) VALUES ($1,$2,$3) ON CONFLICT (player_id,option_key) DO UPDATE SET value_num = excluded.value_num` |
| `buddies` | `player_buddies` | `INSERT INTO player_buddies (player_id, buddy_id, buddy_key, buddy_value) VALUES ($1,$2,$3,$4) ON CONFLICT (player_id,buddy_id,buddy_key) DO UPDATE SET buddy_value = excluded.buddy_value` |
| `progresses` | `player_progress` | `INSERT INTO player_progress (player_id, progress_key, status) VALUES ($1,$2,$3) ON CONFLICT (player_id,progress_key) DO UPDATE SET status = excluded.status` |
| `missions` | `player_missions` | `INSERT INTO player_missions (player_id, mission_id, clear_count, clear_num, status, mission_status) VALUES (...) ON CONFLICT (player_id,mission_id) DO UPDATE SET clear_count=..., clear_num=..., status=..., mission_status=...` |
| `titles` | `player_titles` | `INSERT INTO player_titles (player_id, title_id, status) VALUES (...) ON CONFLICT (player_id,title_id) DO UPDATE SET status = excluded.status` |
| `emblems` | `player_emblems` | `INSERT INTO player_emblems (player_id, emblem_id, outline_part_id, ...) VALUES (...) ON CONFLICT (player_id,emblem_id) DO UPDATE SET ...` |
| `emblem_parts` | `player_emblem_parts` | `INSERT INTO player_emblem_parts (player_id, part_id, status) VALUES (...) ON CONFLICT (player_id,part_id) DO UPDATE SET status = excluded.status` |
| `mecha_sets` | `player_mecha_sets` | `INSERT INTO player_mecha_sets (player_id, mecha_set_id, ...) VALUES (...) ON CONFLICT (player_id,mecha_set_id) DO UPDATE SET ...` |
| `mecha_set_parts` | `player_mecha_set_parts` | `INSERT INTO player_mecha_set_parts (player_id, mecha_set_id, part_id, ...) VALUES (...) ON CONFLICT (player_id,mecha_set_id,part_id) DO UPDATE SET ...` |
| `buddy_win_poses` | `player_buddy_win_poses` | `INSERT INTO player_buddy_win_poses (player_id, buddy_id, win_pose_id, status) VALUES (...) ON CONFLICT (player_id,buddy_id,win_pose_id) DO UPDATE SET status = excluded.status` |
| `line_colors` | `player_line_colors` | `INSERT INTO player_line_colors (player_id, line_color_id, status) VALUES (...) ON CONFLICT (player_id,line_color_id) DO UPDATE SET status = excluded.status` |
| `mecha_colors` | `player_mecha_colors` | `INSERT INTO player_mecha_colors (player_id, mecha_color_id, status) VALUES (...) ON CONFLICT (player_id,mecha_color_id) DO UPDATE SET status = excluded.status` |
| `weapon_set` | `player_weapon_set` | `INSERT INTO player_weapon_set (player_id, weapon_set_id, use_count, use_time, status) VALUES (...) ON CONFLICT (player_id,weapon_set_id) DO UPDATE SET ...` |
| `weapon_set_slots` | `player_weapon_set_slots` | `INSERT INTO player_weapon_set_slots (player_id, weapon_set_id, slot_id, weapon_id, use_count, use_time) VALUES (...) ON CONFLICT (player_id,weapon_set_id,slot_id) DO UPDATE SET ...` |
| `side_weapons` | `player_side_weapons` | `INSERT INTO player_side_weapons (player_id, side_weapon_id, use_count, use_time, status) VALUES (...) ON CONFLICT (player_id,side_weapon_id) DO UPDATE SET ...` |

**Scalar field updates** (direct UPDATE on `player` table):

| Field | Query |
|---|---|
| `title_id_2on2` | `UPDATE player SET title_id_2on2=$2 WHERE player_id=$1` |
| `mecha_set_id` | `UPDATE player SET mecha_set_id=$2 WHERE player_id=$1` |
| `emblem_id_2on2` | `UPDATE player SET emblem_id_2on2=$2 WHERE player_id=$1` |
| `line_color_id_2on2` | `UPDATE player SET line_color_id_2on2=$2 WHERE player_id=$1` |
| `side_weapon_id` | `UPDATE player SET side_weapon_id=$2 WHERE player_id=$1` |
| `mecha_preset_id` | `UPDATE player SET mecha_preset_id=$2 WHERE player_id=$1` |
| `rank_point` | `UPDATE player SET rank_point=$2 WHERE player_id=$1` |
| `max_rank_id` | `UPDATE player SET max_rank_id=$2 WHERE player_id=$1` |
| `rank_point_2on2` | `UPDATE player SET rank_point_2on2=$2 WHERE player_id=$1` |
| `max_rank_id_2on2` | `UPDATE player SET max_rank_id_2on2=$2 WHERE player_id=$1` |
| `buddy_id` | `UPDATE player SET buddy_id=$2 WHERE player_id=$1` |

**Response shape**:
```json
{
    "result": 1,
    "missions": [
        {"mission_id":"...", "clear_count":<int>, "clear_num":<int>, "status":<int>, "mission_status":<int>}
    ]
}
```

**Deterministic**: No (DB-dependent)
**Generic success**: Partially — always returns `result:1` but also includes current missions state
**Error behavior**: Unknown data types log `"UNHANDLED DATA SAVE TYPE"` but don't fail

---

### Route: POST /game_data/* (fallback)

**Source**: `starwing.js:722-738`

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "result": 1
}
```

**Source code**:
```javascript
res.send("{\n" +
    "\"result\": 1" +
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: Yes

---

### Route: POST /battle/record_2on2

**Source**: `starwing.js:739-759`, `battleRecorder.js:1-47`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**:
```json
{
    "player_id": <integer>,
    "stage_id": <integer>
}
```

(Other fields in `req_body` are logged but not used)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Source code** (starwing.js):
```javascript
res.set('x-galaxy-api', '*/*');
let myBr = new br.BattleRecorder(pgdb);
let response = await myBr.battleRecord2on2(req.body);
res.send(JSON.stringify(response,0,4));
```

**Source code** (battleRecorder.js):
```javascript
async battleRecord2on2(req_body){
    let response = new Object();
    response.winning_streaks_2on2 = 1;
    response.rank_point_2on2 = 10000;
    response.ranking_score_2on2 = 500;
    response.ranking_high_score_2on2 = 1000;
    response.gained_ranking_score_2on2 = 200;
    response.is_update_rank_point_2on2 = true;
    response.is_update_ranking_score_2on2 = true;
    response.is_up_ranking_score_2on2 = true;
    response.is_new_record_ranking_score_2on2 = true;

    response.update_items = new Object();
    response.update_items.game_moneys = [];
    let gamemoney = new Object;
    gamemoney.game_money_id=1;
    gamemoney.count = 50;
    response.update_items.game_moneys.push(gamemoney);

    response.battle_reward_ids = [1];
    response.rank_up_reward_ids = [2];
    response.rank_point_reward_ids = [3];
    response.intimacy_up_reward_ids = [4];
    response.avg_minute_score = new Object();
    response.avg_minute_score.stage_id = req_body.stage_id;
    response.avg_minute_score.rank_id = 1;
    response.avg_minute_score.avg_minute_score = 44;

    let qtext = "SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1";
    let res = await this.db.query(qtext, [req_body.player_id]);
    response.missions = [];
    for(let k in res.rows) {
        response.missions.push(res.rows[k]);
    }
    return response;
}
```

**Database reads**:
1. `SELECT mission_id,clear_count,clear_num,status,mission_status FROM player_missions WHERE player_id=$1`

**Database writes**: None (battle results are **not persisted**)

**Response shape**:
```json
{
    "winning_streaks_2on2": 1,
    "rank_point_2on2": 10000,
    "ranking_score_2on2": 500,
    "ranking_high_score_2on2": 1000,
    "gained_ranking_score_2on2": 200,
    "is_update_rank_point_2on2": true,
    "is_update_ranking_score_2on2": true,
    "is_up_ranking_score_2on2": true,
    "is_new_record_ranking_score_2on2": true,
    "update_items": {
        "game_moneys": [{"game_money_id":1, "count":50}]
    },
    "battle_reward_ids": [1],
    "rank_up_reward_ids": [2],
    "rank_point_reward_ids": [3],
    "intimacy_up_reward_ids": [4],
    "avg_minute_score": {
        "stage_id": <int from request>,
        "rank_id": 1,
        "avg_minute_score": 44
    },
    "missions": [...]
}
```

**Deterministic**: Partially — most fields are hardcoded; `avg_minute_score.stage_id` comes from request; `missions` from DB
**Generic success**: No — returns complex battle result object
**Depends on request values**: Only `stage_id` is used (for `avg_minute_score.stage_id`)

---

### Route: POST /battle/* (fallback)

**Source**: `starwing.js:761-777`

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**:

```json
{
    "result": 1
}
```

**Source code**:
```javascript
res.send("{\n" +
    "\"result\": 1" +
    "}");
```

**Database reads**: None
**Database writes**: None
**Deterministic**: Yes
**Generic success**: Yes

---

### Route: POST /resource

**Source**: `starwing.js:779-789`

**Required headers**:
- `x-galaxy-api-id` (echoed)

**Request body**: JSON (logged, not used)

**Response headers**:
- `Content-type: application/json`
- `x-galaxy-api: */*`
- `x-galaxy-api-id: {echoed from request}`

**Response body**: Raw JSON from file `starwing/c_resource.json`

**Source code**:
```javascript
res.send(fs.readFileSync('starwing/c_resource.json','utf8'));
```

**Database reads**: None (file read)
**Database writes**: None
**Deterministic**: Yes (static file)
**Generic success**: No — returns resource data

---

## Complete Route Table

| # | Method | Path | Request Format | Response Status | Response Format | Deterministic | Database | Evidence Lines | Generic Success | Parity Gap |
|---|--------|------|----------------|-----------------|-----------------|---------------|----------|----------------|-----------------|------------|
| 1 | POST | `/matching/server` | JSON body (unused), `x-galaxy-real-ip` header | 200 | `{"ip_addr":"paradox.yourdomain.com:6666"}` | Yes | None | `starwing.js:345-369` | No | IP auth side effect; response has `ip_addr` not `result` |
| 2 | POST | `/mock/matching/server` | JSON body (unused) | 200 | `{"ip_addr":"paradox.yourdomain.com:6666"}` | Yes | None | `starwing.js:371-387` | No | No Python equivalent |
| 3 | POST | `/mock/*` | JSON body (unused) | 200 | `{"ip_addr":"paradox.yourdomain.com:6666"}` | Yes | None | `starwing.js:389-405` | No | No Python equivalent |
| 4 | POST | `/version` | JSON body (unused) | 200 | `{"client_version":"70571","data_version":"70571","stage_ids":[]}` | Yes | None | `starwing.js:407-426` | No | Strings not ints for versions |
| 5 | POST | `/matching/match_id/generate` | JSON body (unused) | 200 | `{"match_id":<random_int_10000-99999>}` | No | None | `starwing.js:428-438` | No | Python returns empty string |
| 6 | POST | `/matching/*` | JSON body (unused) | 200 | `{}` | Yes | None | `starwing.js:440-449` | No | Python returns `{"result":1}` |
| 7 | POST | `/ranking/national` | JSON body (unused) | 200 | Raw JSON from `c_rankingNational.json` | Yes | None (file) | `starwing.js:458-461` | No | Python returns empty array |
| 8 | POST | `/ranking/location` | JSON body (unused) | 200 | Raw JSON from `c_rankingStore.json` | Yes | None (file) | `starwing.js:462-465` | No | Python returns empty array |
| 9 | POST | `/ranking/prefecture` | JSON body (unused) | 200 | Raw JSON from `c_rankingPrefecture.json` | Yes | None (file) | `starwing.js:466-469` | No | Python returns empty array |
| 10 | POST | `/ranking/event` | JSON body (unused) | 200 | Raw JSON from `c_rankingEvent.json` | Yes | None (file) | `starwing.js:470-473` | No | Python returns empty array |
| 11 | POST | `/ranking/weapon` | JSON: `{"role_id":"..."}` | 200 | JSON from `c_rankingWeapon_r{role_id}.json` with `role_id` injected | Yes (file) | None (file) | `starwing.js:474-480` | No | Python returns empty array; legacy has header bug (`ranking/event`) |
| 12 | POST | `/ranking/*` | JSON body (unused) | 200 | `{}` | Yes | None | `starwing.js:481-485` | No | Switch default is dead code (`deafult` typo) |
| 13 | POST | `/player/profile/load` | JSON: `{"nesys_id":<int>}` | 200 | Player profile object | No | READ: player, player_logins, player_progress; WRITE: INSERT player (auto-create) | `starwing.js:488-507`, `playerProfile.js:26-73,297-350` | No | Legacy returns raw player table fields + computed stats |
| 14 | POST | `/player/login` | JSON: `{"player_id":<int>,"location_id":<int>,"client_version":"...","data_version":"..."}` | 200 | Player login state object | No | READ: player, player_logins, player_progress; WRITE: INSERT player_logins | `starwing.js:509-531`, `playerProfile.js:6-25,351-392` | No | Legacy returns greeting_ids, battle_count, boss_matches, burst_match |
| 15 | POST | `/player/login_bonus` | JSON body (unused) | 200 | `{"result":1,"login_bonuses":[],"update_items":{}}` | Yes | None | `starwing.js:534-554` | No | Header is `player/login` not `*/*` |
| 16 | POST | `/player/register` | JSON: `{"player_id":<int>,...fields,"progresses":"[...]"}` | 200 | `{"result":1}` | No | READ: player; WRITE: UPDATE player, UPSERT player_progress | `starwing.js:557-574`, `playerProfile.js:394-436` | Yes | Python returns extra fields |
| 17 | POST | `/player/*` | JSON body (unused) | 200 | `{"result":1}` | Yes | None | `starwing.js:576-592` | Yes | None |
| 18 | POST | `/game_data/load/mission` | JSON: `{"player_id":<int>}` | 200 | `{"missions":[...]}` | No | READ: player, player_missions | `starwing.js:653-676`, `playerProfile.js:74-86` | No | Python returns `{"result":1,"missions":[]}` |
| 19 | POST | `/game_data/load` | JSON: `{"player_id":<int>}` | 200 | Comprehensive game data object (18+ sub-objects) | No | READ: 18 tables | `starwing.js:677-698`, `playerProfile.js:87-296` | No | Python returns `{"result":1,"game_data":{}}` |
| 20 | POST | `/game_data/save` | JSON: `{"player_id":<int>,...categories}` | 200 | `{"result":1,"missions":[...]}` | No | READ: player, player_missions; WRITE: UPSERT 15 tables, UPDATE player (11 scalar fields) | `starwing.js:700-720`, `playerProfile.js:438-722` | No | Python returns `{"result":1}` |
| 21 | POST | `/game_data/*` | JSON body (unused) | 200 | `{"result":1}` | Yes | None | `starwing.js:722-738` | Yes | None |
| 22 | POST | `/battle/record_2on2` | JSON: `{"player_id":<int>,"stage_id":<int>}` | 200 | Complex battle result object | Partial | READ: player_missions | `starwing.js:739-759`, `battleRecorder.js:1-47` | No | Python returns `{"result":1}` |
| 23 | POST | `/battle/*` | JSON body (unused) | 200 | `{"result":1}` | Yes | None | `starwing.js:761-777` | Yes | None |
| 24 | POST | `/mission/*` | JSON body (unused) | 200 | `{}` | Yes | None | `starwing.js:595-614` | No | Returns `{}` not `{"result":1}` |
| 25 | POST | `/credit/*` | JSON body (unused) | 200 | `{}` | Yes | None | `starwing.js:616-631` | No | Returns `{}` not `{"result":1}` |
| 26 | POST | `/tutorial/*` | JSON body (unused) | 200 | `{"result":1}` | Yes | None | `starwing.js:634-650` | Yes | None |
| 27 | POST | `/resource` | JSON body (unused) | 200 | Raw JSON from `c_resource.json` | Yes | None (file) | `starwing.js:779-789` | No | File-based response |

---

## Database Table Summary

### Tables READ by legacy JS

| Table | Read By | Query |
|---|---|---|
| `player` | `/player/profile/load`, `/player/login`, `/player/register`, `/game_data/load/mission`, `/game_data/load`, `/game_data/save` | `SELECT * FROM player WHERE player_id=$1` or `nesys_id=$1` |
| `player_logins` | `/player/profile/load`, `/player/login`, `/game_data/load` | `SELECT COUNT(...) FROM player_logins WHERE ...` |
| `player_progress` | `/player/profile/load`, `/player/login`, `/game_data/load` | `SELECT progress_key,status FROM player_progress WHERE player_id=$1` |
| `player_buddies` | `/game_data/load` | `SELECT buddy_id,buddy_key,buddy_value FROM player_buddies WHERE player_id=$1` |
| `player_options` | `/game_data/load` | `SELECT option_key,value_num FROM player_options WHERE player_id=$1` |
| `player_missions` | `/game_data/load/mission`, `/game_data/load`, `/game_data/save`, `/battle/record_2on2` | `SELECT mission_id,... FROM player_missions WHERE player_id=$1` |
| `player_buddy_win_poses` | `/game_data/load` | `SELECT * FROM player_buddy_win_poses WHERE player_id=$1` |
| `player_emblems` | `/game_data/load` | `SELECT * FROM player_emblems WHERE player_id=$1` |
| `player_emblem_parts` | `/game_data/load` | `SELECT * FROM player_emblem_parts WHERE player_id=$1` |
| `player_titles` | `/game_data/load` | `SELECT * FROM player_titles WHERE player_id=$1` |
| `player_line_colors` | `/game_data/load` | `SELECT * FROM player_line_colors WHERE player_id=$1` |
| `player_mecha_sets` | `/game_data/load` | `SELECT * FROM player_mecha_sets WHERE player_id=$1` |
| `player_mecha_set_parts` | `/game_data/load` | `SELECT * FROM player_mecha_set_parts WHERE player_id=$1` |
| `player_mecha_colors` | `/game_data/load` | `SELECT * FROM player_mecha_colors WHERE player_id=$1` |
| `player_weapon_set` | `/game_data/load` | `SELECT * FROM player_weapon_set WHERE player_id=$1` |
| `player_weapon_set_slots` | `/game_data/load` | `SELECT * FROM player_weapon_set_slots WHERE player_id=$1` |
| `player_side_weapons` | `/game_data/load` | `SELECT * FROM player_side_weapons WHERE player_id=$1` |

### Tables WRITTEN by legacy JS

| Table | Written By | Operation |
|---|---|---|
| `player` | `/player/profile/load` (auto-create), `/player/register`, `/game_data/save` | INSERT (auto-create), UPDATE (dynamic fields) |
| `player_logins` | `/player/login` | INSERT |
| `player_progress` | `/player/register`, `/game_data/save` | UPSERT |
| `player_options` | `/game_data/save` | UPSERT |
| `player_buddies` | `/game_data/save` | UPSERT |
| `player_missions` | `/game_data/save` | UPSERT |
| `player_titles` | `/game_data/save` | UPSERT |
| `player_emblems` | `/game_data/save` | UPSERT |
| `player_emblem_parts` | `/game_data/save` | UPSERT |
| `player_mecha_sets` | `/game_data/save` | UPSERT |
| `player_mecha_set_parts` | `/game_data/save` | UPSERT |
| `player_buddy_win_poses` | `/game_data/save` | UPSERT |
| `player_line_colors` | `/game_data/save` | UPSERT |
| `player_mecha_colors` | `/game_data/save` | UPSERT |
| `player_weapon_set` | `/game_data/save` | UPSERT |
| `player_weapon_set_slots` | `/game_data/save` | UPSERT |
| `player_side_weapons` | `/game_data/save` | UPSERT |

---

## Static Files Served

| Route | File | Header |
|---|---|---|
| `/ranking/national` | `starwing/c_rankingNational.json` | `x-galaxy-api: ranking/national` |
| `/ranking/location` | `starwing/c_rankingStore.json` | `x-galaxy-api: ranking/location` |
| `/ranking/prefecture` | `starwing/c_rankingPrefecture.json` | `x-galaxy-api: ranking/prefecture` |
| `/ranking/event` | `starwing/c_rankingEvent.json` | `x-galaxy-api: ranking/event` |
| `/ranking/weapon` | `starwing/c_rankingWeapon_r{role_id}.json` | `x-galaxy-api: ranking/event` (BUG) |
| `/resource` | `starwing/c_resource.json` | `x-galaxy-api: */*` |

---

## Known Bugs in Legacy JS

1. **`deafult` typo** (`starwing.js:481`): The switch `default` case in `/ranking/*` is misspelled as `deafult`, making it dead code. The ranking fallback still sends `{}` because the `res.send("{}")` call is outside the switch.

2. **Wrong header for `/ranking/weapon`** (`starwing.js:475`): Sets `x-galaxy-api: ranking/event` instead of `ranking/weapon`.

3. **`res.status(200).end()` after `res.send()`** (all routes): In Express, `res.send()` already ends the response. Calling `res.status(200).end()` after `res.send()` is harmless but redundant (Express ignores it because headers already sent).

4. **`battleRecord2on2` does not persist results** (`battleRecorder.js:5-43`): Battle rewards, ranking scores, and streaks are returned but never written to the database.

5. **Hardcoded fake data in matching** (`starwing.js:236-284`): `NotifyMatchMade` contains entirely hardcoded player data and `MatchId: 12345`.

---

## Parity Gaps Summary

| Category | Gap |
|---|---|
| **Response shape mismatch** | `/matching/server` returns `ip_addr` not `result`; `/matching/*` returns `{}` not `{"result":1}`; `/mission/*` returns `{}` not `{"result":1}`; `/credit/*` returns `{}` not `{"result":1}` |
| **Missing DB operations** | `/game_data/load` queries 18 tables; Python returns empty object; `/game_data/save` writes to 15+ tables; Python does nothing; `/battle/record_2on2` reads missions; Python returns hardcoded |
| **Static file reads** | All `/ranking/*` and `/resource` serve raw JSON files; Python returns placeholder arrays |
| **IP authorization** | `/matching/server` adds client IP to `authorizedClients` array; Python does not |
| **Header values** | Legacy uses route-specific `x-galaxy-api` values for ranking, player/profile, player/login, player/login_bonus, player/register, game_data/load, game_data/save; Python uses `*/*` for all |
| **match_id type** | Legacy returns random integer; Python returns empty string |
| **version type** | Legacy returns strings `"70571"`; Python may return different type |
| **login_bonus x-galaxy-api** | Legacy sets `player/login`; Python sets `*/*` |
| **game_data/load/mission x-galaxy-api** | Legacy sets `game_data/load`; Python likely sets `*/*` |
