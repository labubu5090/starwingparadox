# Safe First Launch Plan

## 1. Prerequisites

| Requirement | Status |
|-------------|--------|
| Game content present | `X:\StarwingParadox` (40GB) |
| All DLLs present | Confirmed |
| MSVC runtimes present | Confirmed |
| D3D11 present | Confirmed |
| Python backend ready | `server/app/main.py` |
| TCP server ready | `server/app/tcp_server.py` (port 4001) |
| SQLite database ready | Auto-created on startup |
| NoHDDUnload.dll present | Present (77KB) |

## 2. Safe Launch Steps

### Step 1: Start Backend Server

```powershell
cd C:\Users\KAHO\Pictures\Starwing\server
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify: HTTP 200 at `http://localhost:8000/`

### Step 2: Verify TCP Listener

```powershell
netstat -an | findstr "4001"
```

Should show `LISTENING` on port 4001.

### Step 3: Launch Game (Launcher)

```powershell
cd "X:\StarwingParadox\WindowsNoEditor"
.\AcrGame.exe
```

The launcher (`AcrGame.exe`, 161KB) will:
1. Load XINPUT1_3.dll
2. Optionally launch NesysService.exe
3. Start `AcrGame-Win64-Shipping.exe`

### Step 4: Or Launch Shipping Binary Directly

```powershell
cd "X:\StarwingParadox\WindowsNoEditor"
.\AcrGame\Binaries\Win64\AcrGame-Win64-Shipping.exe
```

## 3. Expected Behavior

1. **Game launches** at 1920x1080 fullscreen (configurable)
2. **Connects to** `127.0.0.1:4001` (our server) for game server
3. **Connects to** `127.0.0.1:6666` for NESYS service (if started)
4. **Card reader** initializes (if NESiCA card present)
5. **Test mode** accessible via TEST switch

## 4. Safety Measures

| Risk | Mitigation |
|------|------------|
| Game crashes on startup | No data loss (no save data exists) |
| Server overload | Our server uses SQLite (no external DB) |
| Port conflict | Port 4001 is free (verified in preflight) |
| Missing DLLs | All DLLs confirmed present |
| Permission denied | Game content is readable |

## 5. Rollback Plan

If anything goes wrong:
1. Close the game window
2. Kill `AcrGame-Win64-Shipping.exe` if still running
3. Our server continues running independently
4. No data loss (SQLite DB is in `server/data/`)

## 6. First Connection Capture

When the game connects for the first time:
1. Our TCP server accepts the connection
2. Game sends initial handshake
3. We log the complete packet (hex + ASCII)
4. We respond with NOT_IMPLEMENTED
5. We capture all data for analysis
