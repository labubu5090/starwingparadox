# Starwing Paradox 網絡架構報告 (IDA/反向分析結果)

> 基於 exe 偏差 `AcrGame-Win64-Shipping.exe` (build 70571) 重構嘅 `message.proto` +
> 代碼字串池 + 當前 Python server 實現嘅逆向分析。
> **未對 exe / DB / server 做任何修改。**

---

## 一、遊戲網絡架構總覽

```
[Client 1]  ─────────────┐
[Client 2]  ─────────────┼──► TCP 6666 (UAcrProtocol / NESYS) ──► [Matching Server]
[Client 3]  ─────────────┤                                                │
[Client 4]  ─────────────┘                                                │
                                                                          │
  ┌───────────────────────────────────────────────────────────────────────┘
  │
  │  NotifyMatchMade → gives DedicatedServer.address to all clients
  │
  ├─► [Dedicated Server (UE4 NM_DedicatedServer)]
  │         ▲
  │         │ TCP 6666 (same protocol)
  │         │
  └─── Client 1~4 各自連入 DS，開始 2on2 battle
```

**所有 4 個 client 都連去同一部 matching server；匹配完成後，全部連去 DS（由 matching server 指定地址）。**

---

## 二、關鍵組件

### 1. Matching Server (NESYS / GameServer)

- **通訊協議**: 自定長度前綴 protobuf，走 **TCP 6666**
- **類名**: `UAcrProtocol`（同時用嚟同 Matching Server 及 Dedicated Server 通訊）
- **Config**: `.ini` 內 `MatchingServer address:...`，或 NESYS 系統資訊，或 command line `-DefaultMatchingServerAddress`
- **Proto 定義**: `message.proto`（内嵌喺 exe，完整重構如下節）
- **Message IDs（節錄）**:

| MessageId | Name | Direction |
|-----------|------|-----------|
| 200 | RequestEntryMatching | Client→Server |
| 201 | ResponseEntryMatching | Server→Client |
| 202 | RequestCancelMatching | Client→Server |
| 206 | RequestJoinMatching | Client→Server |
| 301 | NotifyMatchUpdated | Server→Client |
| **302** | **NotifyMatchMade** | **Server→Client** |
| 304 | NotifyMatchBegin | Server→Client |
| 500 | RequestRegisterDedicatedServer | DS→Server |
| 501 | ResponseRegisterDedicatedServer | Server→DS |
| 601 | NotifyMatchOpen | Server→DS |
| 700 | RequestAssignMatch | Server→DS |
| 704 | RequestEnterMatch | Client→DS |
| 901 | NotifyMatchError | Server→Client |

- **匹配流程**: Client 送出 `RequestEntryMatching` → Server 畀 timeout → `NotifyMatchMade` (302) → `NotifyMatchBegin` (304) → Client 連 DS

### 2. Dedicated Server (DS)

- **執行模式**: 同一個 `AcrGame-Win64-Shipping.exe` 以 UE4 `NM_DedicatedServer` headless 模式執行（無畫面、無輸入）
- **角色**: UE4 authoritative server host（`NM_DedicatedServer` 字串多次出現於 log 格式）
- **啟動後**: 透過 `RequestRegisterDedicatedServer` (500) 向 Matching Server 註冊自己嘅 IP / address
- **收到 MatchOpen 後**: 開始承載 battle，等候客戶端 `RequestEnterMatch` (704)
- **address 通知**: `NotifyMatchMade` (302) 入面有 `DedicatedServer{address, state, version, language}`，Client 據此連入
- **Port**: `DedicatedServer` message **無 port 欄位** → 推斷為同一 NESYS port (6666)（因為 `DedicatedServer` 地址用嚟開新 `UAcrProtocol` 連線，而 `UAcrProtocol` 嘅 port 喺 config 全局設定）

### 3. HTTP API

- **用途**: Mission / gacha / card / shop 等 REST API
- **Port**: 本機 `4001`（透過 `hosts` 檔重定向 `dev.starwing.jp` → 127.0.0.1:80 → proxy 到 4001）
- **Client 用法**: Mission claim / reward 等 web request

---

## 三、完整 Proto 定義（重構自 exe 內嵌 `FileDescriptorProto`）

完整 647 行 proto 已存於：
`C:\Users\KAHO\AppData\Local\Temp\opencode\message.proto.reconstructed.txt`

關鍵消息結構：

```protobuf
// PbMessage: 訊息封包
message PbMessage {
  int64 id = 1;             // 消息類型 ID（見上述 messageId）
  enum type = 2;
  uint64 sessionId = 3;
  // ... 各 message type oneof ...
}

// NotifyMatchMade: 匹配成功通知
message NotifyMatchMade {
  Match match = 1;                // 雙方陣容、gameMode (ModeNormal/Mode2on2)、vsCpu 等
  DedicatedServer server = 2;     // DS 地址（address/version/state）
  enum type = 3;
  GameMode gameMode = 4;
  uint32 stageId = 5;
}

// DedicatedServer
message DedicatedServer {
  uint32 id = 1;
  enum state = 2;          // Initializing=0, Idle=1, Applying=2, Loading=3, Battle=4, Closing=5
  string address = 3;      // DS IP 地址（無 port 欄位 → port 隱含為 NESYS port）
  string version = 4;      // "70571"
  int64 startupTime = 5;
  string language = 6;
}

// Match
message Match {
  uint64 id = 1;
  enum state = 2;
  enum playMode = 3;       // NationalMatch/CooperationMatch/NonePlayMode
  repeated Team team = 7;
  bool vsCpu = 13;         // true = 對 AI
  enum gameMode = 18;      // ModeNormal=0, Mode2on2=1
  ...
}

enum GameMode { ModeNormal = 0; Mode2on2 = 1; }
```

---

## 四、Client 連線決策流程（從字串池還原）

```
[UAcrProtocol::Connect]
 ├─ "I am DedicatedServer."                     → DS 模式，向 matching server 註冊
 ├─ "Connect to MatchingServer address from NESYS:%s" → 用 NESYS 系統提供嘅地址
 ├─ "MatchingServer address from Config:%s"      → 用 .ini config
 ├─ "Connect to No config address:%s"            → fallback
 ├─ "Use GetNesysInfo address:%s ENesysGameServerType:%s" → NESYS info
 └─ "Use Connect to address:%s"                 → 最終使用嘅地址

[收到 NotifyMatchMade (302)]
 └─ "Address:%s" (ds.address) → 開新 UAcrProtocol 連線到 DS 地址
     └─ 送出 RequestEnterMatch (704) → 收到 ResponseEnterMatch → 進入 battle
```

---

## 五、2on2 跨機連入指南

### 問題：3 個朋友要點連入嚟？

**答：所有人必須連去同一部 matching server + DS。**

### 要做嘅步驟

| 角色 | 設定 | 通訊 |
|------|------|------|
| **Host (你)** | 開 Matching Server + DS + HTTP proxy | TCP 6666 + TCP 6666(DS) + port 80/4001 |
| **Friend 1~3** | Client 模式，config 指向 Host | 連 Host:6666 (matching) + Host:6666 (DS) + Host:80 (HTTP) |

### 同一隻 Server？**是**

- 4 個 client 嘅 matching address 設定必須指向**同一部 matching server**（你部機嘅 IP）
- DS 地址由 matching server 分配（`NotifyMatchMade` 嘅 `server.address` 欄位），4 個 client 都會自動連去同一部 DS

### VPN 需求？

| 情況 | 方案 |
|------|------|
| 同一 LAN (同一 WiFi/路由器) | 直接用 LAN IP (192.168.x.x)，唔使 VPN |
| 跨網絡（唔同寬頻/唔同地方） | **需要 VPN**：Tailscale / ZeroTier / Hamachi |
| 有公網 IP + 想 port forward | 可行但麻煩（要開 6666 + 80 兩個 port） |

**推薦方案：Tailscale（免費、零設定、自動 NAT 穿越）**

安裝步驟（每人一部機）：
1. 全員安裝 [Tailscale](https://tailscale.com/download)
2. 登入同一個 Tailscale 帳號 → 全部出現喺同一個虛擬 LAN
3. Host 機：開 matching server (port 6666) + DS + HTTP proxy (port 80/4001)
4. Friend 機：hosts 檔加 `100.x.x.x dev.starwing.jp`（Tailscale 虛擬 IP），INI 設 matching address
5. 各人 client 自動連 Host 嘅 matching + DS

### 專用 Server 端口總覽

| Port | 用途 | Protocol |
|------|------|----------|
| 6666 | NESYS Matching Server | TCP (length-prefix protobuf) |
| 6666 | Dedicated Server（同 port，不同 IP / 不同 process） | TCP + UE4 net |
| 80 | HTTP proxy (→ 4001) | HTTP |
| `\\.\pipe\nesys_games` | NesiCa card reader（本地 only） | Named Pipe |
| 4001 | Python API server | HTTP |

---

## 六、當前 Dev Server 實現狀態

### 已實現
- ✅ TCP 6666 matching server：基本 `RequestEntryMatching` → `NotifyMatchMade` (VsCPU)
- ✅ HTTP API：mission / reward / gacha / card 全部正常
- ✅ 真機連線測試成功（VsCPU 本地 battle）

### 未實現（若要真正 2on2 跨機對戰）
- ❌ **真實匹配**：目前只有 VsCPU（一人類隊 + CPU 對手），無真正 4 人配對
- ❌ **DS 進程管理**：未啟動 dedicated server 進程，無 `RequestRegisterDedicatedServer` 處理
- ❌ **完整流程**：未實現 `NotifyMatchOpen` → `RequestAssignMatch` → `RequestEnterMatch` → `NotifyMatchBegin` → Battle
- ❌ **DS 地址分派**：matching server 未 send `DedicatedServer` field in `NotifyMatchMade`

### 若要實現真 2on2，需要
1. Matching server 實現真正嘅 4 人匹配（把 4 個 client 編入 2 個 Team，gameMode=Mode2on2）
2. 啟動 DS（可能用同一個 exe 以 headless 模式，config 開 NM_DedicatedServer）
3. DS 向 matching server 註冊（`RequestRegisterDedicatedServer`，帶 address/version）
4. Matching server 分派 DS（`NotifyMatchMade` 帶 `server.address` + `RequestAssignMatch` 到 DS）
5. 4 個 client 連去 DS（`RequestEnterMatch`）→ battle 開始

---

## 七、技術細節補充

### GameMode 區分
- `ModeNormal (0)` = 一般對戰
- `Mode2on2 (1)` = 2on2 對戰

### PlayMode
- `NonePlayMode (0)` = 未設定
- `NationalMatch (100/0x64)` = 全國對戰（街機模式）
- `CooperationMatch (101/0x65)` = 合作模式（協力）

### DedicatedServer State
| Value | 狀態 |
|-------|------|
| 0 | Initializing（初始化中） |
| 1 | Idle（待機，可接 match） |
| 2 | Applying（應用 match 中） |
| 3 | Loading（載入中） |
| 4 | Battle（戰鬥進行中） |
| 5 | Closing（關閉中） |

### vsCPU 標記
Match 入面 `vsCpu` (bool)：`true` = 對 CPU（本地模擬），`false` = 真人對戰（需要 DS）。

---

## 八、相關檔案

| 檔案 | 說明 |
|------|------|
| `C:\Users\KAHO\AppData\Local\Temp\opencode\message.proto.reconstructed.txt` | 完整重構嘅 message.proto（647 行） |
| `tools/ida_g21/targets/AcrGame-Win64-Shipping.exe` | 分析對象 (SHA256: `ce4c89054bf7c4d833ee8af455a485ac401eead12a80ffc077663a768fd47dc4`) |
| `tools/ida/string_analysis_results.json` | 字串元數據 |
| `server/app/handlers_matching.py` | 當前 matching server（僅 VsCPU） |
| `server/app/protocol/registry.py` | Message type 對照 |
| `docs/STARWING_MASTER.md` | 官方 protocol 文件（§TCP Commands） |
| `legacy-js/js/starwing.js` | Legacy matching stub |
| `C:\Users\KAHO\AppData\Local\Temp\opencode\disas.py` | 反彙編腳本 |
| `C:\Users\KAHO\AppData\Local\Temp\opencode\disas2.py` | 反彙編腳本 (with rip strings) |

---

*報告完成，未對任何系統做修改。*
*分析基於：exe 內嵌 protobuf descriptor 重構 + 字串池上下文 + server 現有實現交叉驗證。*
