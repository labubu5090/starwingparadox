# TCP Server Evidence Audit

**Date:** 2026-08-26
**Auditor:** opencode
**Verdict:** **LEGACY TCP SERVER CONFIRMED — Python implementation is SOURCE_VERIFIED**

---

## 1. Executive Summary

A raw TCP server **was part of the legacy system**. The original Node.js server (`starwing.js`) runs a `net.createServer` TCP listener on port 6666 alongside an HTTP Express server on port 4001. The Python rewrite accurately replicates the framing, port, byte order, and handler dispatch. All key parameters are source-verified against the legacy code.

---

## 2. Evidence Catalog

### 2.1 Raw TCP Server Exists in Legacy

| # | Source | Line(s) | Exact Code | What It Proves |
|---|--------|---------|------------|----------------|
| E1 | `legacy-js/js/starwing.js` | 4 | `const net = require('net');` | `net` module imported — raw TCP capability |
| E2 | `legacy-js/js/starwing.js` | 29 | `const pb_port = 6666;` | TCP port is 6666 |
| E3 | `legacy-js/js/starwing.js` | 80 | `net.createServer(socket => {` | Raw TCP server created |
| E4 | `legacy-js/js/starwing.js` | 342 | `}).listen(pb_port,"0.0.0.0");` | Listens on `0.0.0.0:6666` |
| E5 | `legacy-js/js/starwing.js` | 793 | `` console.log(`HTTP ${web_port} Protobuf ${pb_port}`); `` | Confirms dual-port architecture: HTTP 4001, TCP 6666 |

### 2.2 Framing Protocol: 4-Byte Little-Endian Length Prefix

| # | Source | Line(s) | Exact Code | What It Proves |
|---|--------|---------|------------|----------------|
| E6 | `legacy-js/js/starwing.js` | 71-73 | `let outBuffer = new Buffer.alloc(4+msgBuffer.byteLength);`<br>`outBuffer.writeUInt32LE(msgBuffer.byteLength, 0);`<br>`msgBuffer.copy(outBuffer,4);` | **4-byte uint32 LE length prefix**, then raw protobuf bytes |
| E7 | `legacy-js/js/starwing.js` | 101 | `let packetLen = recvBuffer.readUIntLE(0, 4);` | Receive side reads 4-byte LE length prefix |
| E8 | `legacy-js/js/starwing.js` | 104 | `let incomingPB = recvBuffer.slice(4, 4+packetLen);` | Payload extracted after 4-byte header |
| E9 | `legacy-js/js/starwing/burstMode.js` | 15-17 | `let outBuffer = new Buffer.alloc(4+msgBuffer.byteLength);`<br>`outBuffer.writeUInt32LE(msgBuffer.byteLength, 0);`<br>`msgBuffer.copy(outBuffer,4);` | Same framing in co-op module (independent confirmation) |

### 2.3 Byte Order: Little-Endian

| # | Source | Line(s) | What It Proves |
|---|--------|---------|----------------|
| E10 | `legacy-js/js/starwing.js` | 72 | `writeUInt32LE` — explicit LE on send |
| E11 | `legacy-js/js/starwing.js` | 101 | `readUIntLE(0, 4)` — explicit LE on receive |
| E12 | `server/app/protocol/codec.py` | 63 | `struct.unpack_from("<I", data, 0)[0]` — Python `<` = little-endian |
| E13 | `server/app/protocol/codec.py` | 79 | `struct.pack("<I", len(payload))` — Python `<` = little-endian |

### 2.4 Port and Bind Address

| # | Source | Line(s) | What It Proves |
|---|--------|---------|----------------|
| E14 | `legacy-js/js/starwing.js` | 29 | `const pb_port = 6666;` — port constant |
| E15 | `legacy-js/js/starwing.js` | 31 | `const matcher = "paradox.yourdomain.com:"+pb_port;` — client-facing address includes port |
| E16 | `legacy-js/js/starwing.js` | 342 | `.listen(pb_port,"0.0.0.0")` — binds to all interfaces |
| E17 | `server/app/config.py` | 10 | `pb_port: int = 6666` — Python config matches |
| E18 | `server/app/tcp_server.py` | 173 | `port: int = 6666` — Python default matches |

### 2.5 Connection Authorization

| # | Source | Line(s) | Exact Code | What It Proves |
|---|--------|---------|------------|----------------|
| E19 | `legacy-js/js/starwing.js` | 40 | `let authorizedClients = Array();` | IP whitelist (empty at start) |
| E20 | `legacy-js/js/starwing.js` | 87-94 | `if(authorizedClients.indexOf(socket.remoteAddress) !== -1){...} else { socket.destroy(); }` | Unauthorized TCP connections are **immediately destroyed** |
| E21 | `legacy-js/js/starwing.js` | 345-359 | `POST /matching/server` handler pushes `x-galaxy-real-ip` to `authorizedClients` | IPs authorized via HTTP first, then TCP |

### 2.6 Socket Event Handlers

| # | Source | Line(s) | Event | Behavior |
|---|--------|---------|-------|----------|
| E22 | `legacy-js/js/starwing.js` | 96 | `socket.on('data', ...)` | Main message receive handler |
| E23 | `legacy-js/js/starwing.js` | 303-310 | `socket.on('error', ...)` | Ignores `ECONNRESET`, logs others |
| E24 | `legacy-js/js/starwing.js` | 311-315 | `socket.on('timeout', ...)` | Calls `socket.end('Timed out!')` |
| E25 | `legacy-js/js/starwing.js` | 317-320 | `socket.on('end', ...)` | Logs end event |
| E26 | `legacy-js/js/starwing.js` | 321-338 | `socket.on('close', ...)` | Logs bytes read/written, removes from `activeGameServers` |
| E27 | `legacy-js/js/starwing.js` | 339-341 | `socket.on('connection', ...)` | Logs new connection |

### 2.7 Protobuf Message Format

| # | Source | Line(s) | What It Proves |
|---|--------|---------|----------------|
| E28 | `legacy-js/js/starwing.js` | 63 | `pbMessageRoot.lookupType("starwing.PbMessage")` — uses `starwing.PbMessage` envelope |
| E29 | `legacy-js/js/starwing.js` | 70 | `PMessage.encode(outMessage).finish()` — protobuf encoding |
| E30 | `legacy-js/js/starwing.js` | 108 | `PMessage.decode(incomingPB)` — protobuf decoding |
| E31 | `server/app/protocol/proto/starwingMessage.proto` | 4-40 | `message PbMessage { int64 packetId = 1; int64 messageType = 2; ... oneof Message { ... } }` — envelope structure confirmed |

### 2.8 Handler Dispatch

| # | Source | Line(s) | What It Proves |
|---|--------|---------|----------------|
| E32 | `legacy-js/js/starwing.js` | 117 | `switch (parseInt(decoded.messageType))` — dispatch by messageType |
| E33 | `legacy-js/js/starwing.js` | 118-123 | `case 0x66:` — Ping handler |
| E34 | `legacy-js/js/starwing.js` | 222-294 | `case 200:` — RequestEntryMatching handler |
| E35 | `legacy-js/js/starwing.js` | 125-215 | `case 208/210/214/216:` — Burst mode handlers |
| E36 | `server/app/tcp_server.py` | 39-47 | `_handlers: dict[int, HandlerFunc]` + `register_handler()` — registry pattern matches legacy switch/case |

---

## 3. Parameter Comparison: Legacy vs Python

| Parameter | Legacy (JS) | Python | Match? | Evidence |
|-----------|-------------|--------|--------|----------|
| Port | 6666 | 6666 | ✅ | E2, E17, E18 |
| Bind address | 0.0.0.0 | 0.0.0.0 | ✅ | E16, tcp_server.py:172 |
| Framing | 4-byte uint32 LE length prefix | 4-byte uint32 LE length prefix | ✅ | E6-E9, codec.py:63,79 |
| Byte order | Little-endian | Little-endian | ✅ | E10-E13 |
| Message envelope | `starwing.PbMessage` protobuf | `starwing.PbMessage` protobuf | ✅ | E28-E31 |
| Dispatch method | `switch(messageType)` | Registry dict | ✅ | E32-E36, tcp_server.py:143 |
| Ping type | 0x66 | 0x66 | ✅ | E33, tcp_server.py:89 |
| Read chunk size | `data` event (all available) | 65536 bytes | ⚠️ | See §4.1 |
| Timeout behavior | `socket.end('Timed out!')` | `break` (closes connection) | ⚠️ | See §4.2 |
| Max frame size | No explicit limit | 1 MiB | ⚠️ | See §4.3 |
| Authorization | IP whitelist via HTTP POST | Not implemented | ⚠️ | See §4.4 |

---

## 4. Remaining Unknowns

### 4.1 Read Chunk Size
- **Legacy:** `socket.on('data')` delivers whatever the OS缓冲区 has — could be partial or multiple frames.
- **Python:** Reads exactly 65536 bytes per `reader.read()` call.
- **Impact:** The Python incremental buffering (lines 103-157) correctly handles partial frames, so this is functionally equivalent. Not a discrepancy.

### 4.2 Timeout Behavior
- **Legacy:** `socket.on('timeout')` at line 311 calls `socket.end('Timed out!')` — sends a TCP FIN with a message.
- **Python:** `asyncio.wait_for(..., timeout=settings.pb_timeout)` raises `TimeoutError`, which triggers `break` and `writer.close()` — sends a TCP FIN without a message body.
- **Impact:** Minor difference. The legacy sends a string payload on timeout; the Python sends a bare FIN. The arcade cabinet's behavior on receiving either is unknown.

### 4.3 Maximum Payload Size
- **Legacy:** No explicit max. Relies on Node.js `Buffer` limits (~2 GiB).
- **Python:** `MAX_FRAME_SIZE = 1 * 1024 * 1024` (1 MiB) at `codec.py:40` and `tcp_server.py:42`.
- **Impact:** The 1 MiB limit is a safety constraint not present in legacy. Real Starwing messages are small (typically <1 KiB). Unlikely to cause issues.

### 4.4 Connection Authorization
- **Legacy:** TCP connections require prior HTTP POST to `/matching/server` to whitelist the IP (`starwing.js:87-94`, `345-359`).
- **Python:** No IP authorization on TCP connections.
- **Impact:** Security gap. In production, unauthorized clients could connect. Not an issue for local development.

### 4.5 Socket Timeout Duration
- **Legacy:** `socket.on('timeout')` exists but `socket.setTimeout()` is never called in the source. The default Node.js socket timeout is `0` (no timeout), meaning the timeout handler may never fire unless the OS or kernel sets one.
- **Python:** `settings.pb_timeout = 30.0` seconds (config.py:13).
- **Impact:** The Python server actively times out idle connections after 30s; the legacy may never time out. This is likely an improvement.

### 4.6 `activeGameServers` Cleanup
- **Legacy:** `socket.on('close')` at line 328-332 filters `activeGameServers` to remove the disconnected connection.
- **Python:** No equivalent tracking. The `activeGameServers` array in legacy was for tracking dedicated game server connections (separate from cabinets).
- **Impact:** Not needed until dedicated server support is implemented.

---

## 5. Verdict

### Was a raw TCP server part of the legacy system?
**YES.** Definitively confirmed by `net.createServer` at `starwing.js:80`, listening on port 6666 at `starwing.js:342`.

### What port was it on?
**6666.** Confirmed by `starwing.js:29`, `starwing.js:31`, `starwing.js:342`.

### What was the framing protocol?
**4-byte unsigned integer, little-endian, encoding the byte length of the protobuf payload, followed by the raw protobuf bytes.** Confirmed by `starwing.js:71-73` (encode) and `starwing.js:101,104` (decode).

### What was the byte order?
**Little-endian.** Confirmed by `writeUInt32LE` (starwing.js:72) and `readUIntLE` (starwing.js:101).

### What was the maximum payload size?
**Unknown / no explicit limit in legacy.** Python enforces 1 MiB as a safety limit. No evidence of a legacy limit.

### What was the timeout behavior?
**Legacy has a timeout handler (`socket.on('timeout')`) but never calls `socket.setTimeout()`, so it likely never fires.** Python uses 30 seconds as a configurable default.

### What was the connection close behavior?
**Legacy calls `socket.end()` on timeout, `socket.destroy()` on unauthorized connections, and logs bytes read/written on `close` event.** Python calls `writer.close()` + `await writer.wait_closed()` on all disconnect paths.

---

## 6. Classification

| Component | Status |
|-----------|--------|
| TCP server (port, bind, framing) | **SOURCE_VERIFIED** |
| Byte order (LE) | **SOURCE_VERIFIED** |
| Message envelope (PbMessage protobuf) | **SOURCE_VERIFIED** |
| Ping handler (0x66) | **SOURCE_VERIFIED** |
| Handler dispatch pattern | **SOURCE_VERIFIED** |
| Timeout duration (30s) | **EXPERIMENTAL** (not in legacy source) |
| Max frame size (1 MiB) | **EXPERIMENTAL** (not in legacy source) |
| IP authorization | **NOT_IMPLEMENTED** (present in legacy) |
| `activeGameServers` tracking | **NOT_IMPLEMENTED** (present in legacy) |
