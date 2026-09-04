# G47 — Definitive code-level root cause: `GetNesysGameServerHttpIP` empty

Date: 2026-09-01. Tool: IDA Professional 9.3 on `AcrGame-Win64-Shipping.exe` (g47c/g47d analysis runs).

## Summary

The offline cycle is now confirmed at the disassembly level. While NESYS reports online
(`bNesysServerLive=1`), the game's matching-address selection is **hard-pinned to the
`GetNesysInfo` code path**, which reads the NESYS game-server `HttpIP` field that is **never
populated** by our fake pipe stack. The result is the malformed `http://` matching URL and the
subsequent offline / shop-closed state. The only valid-address path (`[None]` / config / INI)
is gated to the **offline** NESYS state, so *online NESYS* and *valid address* are mutually
exclusive under the current constraints (no binary patch, no fabricated cert flags).

## Key functions decoded (all offsets VAs in the Shipping exe)

### 1. `UCPP_HttpRequester::GetHostAddress` = `sub_142C36160`
Logs `MatchingServerType[%s]`, `GetNesysGameServerHttpIP is empty.`, `SHORT_MOCK_URL`,
`Address[%s]`, `HostURL[%s]` (CPP_HttpRequester.cpp:239/245/252/256/287).

- If `ENesysGameServerType` is the GetNesysInfo path (`v50` set):
  - `v26 = sub_142C64490(v9)`  → reads `GetNesysGameServerHttpIP` (empty).
  - Builds `HostURL = "http://" + <that IP>`  → `http://` when empty. **This is the failure.**
- Else (NOT GetNesysInfo):
  - `Src = L"dev.starwing.jp/mock"` (SHORT_MOCK_URL).
  - `HostURL = http://dev.starwing.jp/mock`  → this is the working-looking mock URL seen in
    offline runs; it then goes through `POST /matching/server` → our `127.0.0.1:6666`.

### 2. `UAcrProtocol::Connect` = `sub_142BCB6E0` (AcrProtocol.cpp)
Reads `ENesysGameServerType` from the nesys game-server object.
- Type `GetNesysInfo`(1)/`GetNetworkConfig`(2) → address copied from `&v95` (the NesysInfo);
  logs `"Use GetNesysInfo address:%s ENesysGameServerType:%s"` → empty in practice.
- `[None]`(0) → logs `"Error No MatchingServer so initialize Nesys before."` (boot error path).
- Config path gated by `byte_148EE1804` flag → logs
  `"Use Config(.ini)MatchingServer address:%s"`, sets connect-type INI/2, reads
  `qword_148EE17B8` config address.
- Final "Decide connect type": NESYS(0) / NONE(1) / INI(2).

### 3. `GetNesysGameServerHttpIP` reader = `sub_142C64490`
`v1 = *(nesysObject + 384)`; if null returns the empty string buffer at `nesysObject+1608`;
else copies HttpIP from `v1 + 128`. **The `+384` info pointer is NULL → empty.** Small wrapper
`sub_142D90F40` copies this value out for callers.

### 4. `SetNesysGameServerInfo` = `sub_142D52C60` & getter `sub_142D49DE0`
UE reflection UFUNCTION wrappers over a class member named `"info"`. They resolve members
`"info"` / `"ReturnValue"` and invoke via reflection. The only caller of both is
`sub_142D0A060` — the **NesysControl class member-property registration dispatcher** (registers
all `NesysControl` fields such as `m_nesysWork`, `NesysSendIncomeString`,
`NesysControlCriticalMessage`, plus the per-member getter/setter UFUNCTIONs). No local/non-RPC
path populates `info`/HttpIP with a real value in our stack.

## MAJOR REFRAME (g47e) — the config-address flag is set by the matching HTTP response

`UWebServerWork::SetConnectAddress` = `sub_142C93310` (WebServerWork.cpp:276):
```c
byte_148EE1804 = 1;                                    // arms the use-config path
sub_141D6EC10(&qword_148EE17C8, &qword_148EE17B8);     // save old
sub_141D6EC10(&qword_148EE17B8, a2);                   // set config address = a2  ← response IP
log "UWebServerWork::SetConnectAddress / address[%s]"
```
`UWebServerWork::OnReceiveResponseMatchingServer` = `sub_142C8FD30` (WebServerWork.cpp:3200/3202):
```c
if ( a2 /*HTTP success*/ ) {
    sub_142C93310(a1, a3+8);        // SetConnectAddress(response IP) → byte_148EE1804=1 + qword_148EE17B8=IP
    byte_148EE1806 = (new != old);  // "Change[%d]"
}
log "OnReceiveResponseMatchingServer / _IsSuccess[%d] IPAddress[%s]"   // = observed "_IsSuccess[0] IPAddress[]"
```

**Reframe / key insight:** In `UAcrProtocol::Connect`, `byte_148EE1804` is checked FIRST (line 776).
If it is 1, the config address `qword_148EE17B8` is used REGARDLESS of NESYS type. And
`byte_148EE1804` is set ONLY by `SetConnectAddress`, which is called ONLY on a *successful*
matching-server HTTP response (`_IsSuccess=1`).

So the online dead-lock is a **self-reinforcing circle**:
1. Online → `GetHostAddress` uses `[GetNesysInfo]` → `GetNesysGameServerHttpIP` empty → URL `http://`.
2. HTTP `http:///matching/server` fails → `_IsSuccess[0]` → `SetConnectAddress` NOT called.
3. `byte_148EE1804` stays 0, `qword_148EE17B8` stays empty.
4. `UAcrProtocol::Connect` → flag 0 → NESYS(empty) path.

Tail-call in handler: `return sub_142C806E0(a1+1856, a2, a3)`.
`sub_142CA1360` re-checks `qword_148EE17B8` against an incoming value when change flag set, then calls `sub_142C8BDD0`.

**Therefore the true fix target is NOT "force NESYS offline" but "make the matching HTTP request
succeed while online"** — which arms `byte_148EE1804=1` and populates `qword_148EE17B8`, letting
`UAcrProtocol::Connect` use the config path even with NESYS online. G46 `-UseConfigMatchingServer`
is a *different* flag (does NOT set `byte_148EE1804`), which is why it was ignored.

Open question being pursued: how the game constructs/reaches the matching-server HTTP request in
online mode (does it ever connect despite `http://`), and whether it can be satisfied.

## RESOLUTION (g47e/g47f + live online boot, 2026-09-01) — request fails locally, no wire traffic

**`SetConnectAddress` is called ONLY from `OnReceiveResponseMatchingServer` on success.**
(g47f xrefs: SetConnectAddress has exactly 1 caller = sub_142C8FD30; OnReceiveResponseMatchingServer
has exactly 1 caller = sub_142C528D0, the matching-response HTTP callback.) Success = the HTTP
matching request returned a real response with a body containing `"ip_addr"`. There is **no** config
file, command-line flag, or other writer that arms `byte_148EE1804`/`qword_148EE17B8`. G46
`-UseConfigMatchingServer` is a different flag and does NOT arm these.

**Live online boot (10:08, capture started, game launched with pipe stub ONLINE) — exact sequence:**
```
42.282  BeginPlay / MyAddress[26.0.115.38:0000]
43.171  UCPP_HttpRequester::GetHostAddress / MatchingServerType[GetNesysInfo]
43.171  UCPP_HttpRequester::GetHostAddress / GetNesysGameServerHttpIP is empty.
43.171  Address[]
43.171  HostURL[http://]                                  ← empty-host URL
43.176  UOnlineObserverWork::SetHttpSuccess bNesysServerLive[1] ... bHttpSuccess[0]
43.176  UWebServerWork::OnReceiveResponseMatchingServer / _IsSuccess[0] IPAddress[]
43.176  UOnlineObserverWork::OnReceiveMatchingServer / bChangeServer[0] IsSuccess[0] IPAddress[]
43.177  ACPP_GameModeBoot::OnReceiveMatchingServer / IsSuccess[0] IPAddress[]
```
Timing: URL built at 43.171 → fail callback at 43.176 (~5 ms), with **no socket/connector log line in
between**. The empty-host `http://` fails locally in the HTTP client before any connection is made,
producing zero network traffic, so it can never be intercepted/satisfied. (The started capture was
force-killed and corrupted/unreadable; the log timing alone is conclusive that no matching request
hit the wire.)

## FINAL DECISION (investigate-more fork closed)

Under the standing constraints (**no binary patch** + **do not fabricate cert/auth flags**), there is
**no reachable path** to populate the online matching address:
- `bNesysServerLive=1` forces `MatchingServerType[GetNesysInfo]` → needs `GetNesysGameServerHttpIP`.
- `GetNesysGameServerHttpIP` reads `info` struct at `*(nesysObject+384)` which is NULL; set only by a
  genuine cert-authenticated NESYS game-server-info response (G45: not fabricatable).
- The only address that works (config `qword_148EE17B8`) is armed only by a successful matching HTTP
  response, which requires a valid URL, which requires the above — circular, unreachable online.
- The 5 ms local failure confirms the empty-host request never reaches the network.

**Net:** "online NESYS" and "valid matching server" are proven mutually exclusive without relaxing a
constraint. Options remain: (a) allow a copy-only binary patch to force the `[None]`/config path while
keeping NESYS online, or (b) run NESYS offline (proven playable per G34) and accept non-"online"
NESYS icon/shop.

## Conclusion / blocker (pre-reframe)
`*(nesysObject+384)` (game-server `info` struct containing Http/Tcp IP) is populated **only**
via a genuine NESYS game-server-info network response (cert-authenticated `RequestNetworkInfo`
/ `SetNesysGameServerInfo`). The fake pipe stub cannot satisfy that (G45: do not fabricate
cert/auth flags), and binary patching is prohibited. Therefore while NESYS is online the
address is guaranteed empty, while the working config/`[None]` address path is available only
when NESYS is offline. The "online NESYS + valid matching address" combination is not reachable
under the stated constraints.

## Decisional fork for the user
1. Keep NESYS online and accept offline outcome (no change possible without patch/fabrication).
2. Run NESYS offline and use the proven playable config/`[None]` path (G34 report) — gives
   real local play but NESYS icon/shop not "online".
3. Revisit constraints: allow a controlled binary patch (copy-only exe, user runs the patched
   copy) or allow fabricating the `info` struct population to test full online flow.
