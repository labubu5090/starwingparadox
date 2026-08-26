# Single-Cabinet Deployment Runbook

## Preconditions

- Python 3.10+ installed and in PATH
- PostgreSQL running locally (port 5432)
- Project cloned to `C:\Users\KAHO\Pictures\Starwing`
- PowerShell 5.1+ (Windows)
- No other services bound to ports 4001 (HTTP) or 6666 (TCP)

## 1. Database Startup

```powershell
# Verify PostgreSQL is running
.\tools\postgresql\check-postgresql.ps1

# Create test database (first time only)
.\tools\postgresql\create-test-database.ps1
```

## 2. Schema Verification

```powershell
# Run Alembic migrations
cd server
alembic upgrade head

# Verify tables exist
psql -h localhost -U starwing_test_user -d starwing_test -c "\dt"
```

## 3. Environment Variables

Copy the example environment and customize:

```powershell
Copy-Item config\single-cabinet.example.env config\.env
# Edit config\.env with your database credentials
```

Required variables:

| Variable | Description | Default |
|---|---|---|
| `TEST_DATABASE_URL` | PostgreSQL connection string | Required |
| `HOST` | Bind address | `127.0.0.1` |
| `PORT` | HTTP port | `4001` |
| `PB_PORT` | TCP protobuf port | `6666` |
| `CAPTURE_ENABLED` | Enable request capture | `false` |

## 4. Server Startup

```powershell
# Start with config file
.\tools\cabinet\start-single-cabinet-server.ps1 -ConfigPath config\.env

# Or start with defaults
.\tools\cabinet\start-single-cabinet-server.ps1
```

The script will:
- Refuse to start if already running (checks PID file and port)
- Write logs to `runtime/starwing-single-cabinet.log`
- Save process ID to `runtime/starwing-single-cabinet.pid`
- Perform initial health check

## 5. Health Check

```powershell
# Automated verification
.\tools\cabinet\verify-single-cabinet-server.ps1

# Manual check
Invoke-RestMethod http://127.0.0.1:4001/health
Invoke-RestMethod http://127.0.0.1:4001/ready
```

Expected responses:
- `/health`: `{"status": "ok"}`
- `/ready`: `{"status": "ready", "database": "ok"}`

## 6. TCP Verification

```powershell
# Check TCP port is listening
Get-NetTCPConnection -LocalPort 6666 -ErrorAction SilentlyContinue | Where-Object {$_.State -eq "Listen"}
```

If TCP is disabled (`PB_ENABLED=false`), port 6666 will not be active. This is expected.

## 7. Cabinet Network Placeholder

For real cabinet testing, connect the cabinet to the same network segment:

1. Ensure cabinet is on isolated VLAN (not internet-facing)
2. Configure cabinet to point to this server's IP
3. Verify firewall allows ports 4001 and 6666
4. Test connectivity from cabinet

**Do not expose the server to untrusted networks.**

## 8. Capture Enablement/Disablement

### Enable Capture

```powershell
# Via environment variable (in config\.env)
# Set CAPTURE_ENABLED=true

# Or enable at runtime via Python
python -c "from app.capture import enable_capture; enable_capture()"
```

### Disable Capture

```powershell
# Via environment variable
# Set CAPTURE_ENABLED=false

# Or disable at runtime
python -c "from app.capture import disable_capture; disable_capture()"
```

### Verify Capture Status

```powershell
python -c "from app.capture import is_capture_enabled, get_capture_dir; print(f'Enabled: {is_capture_enabled()}, Dir: {get_capture_dir()}')"
```

## 9. Shutdown

```powershell
.\tools\cabinet\stop-single-cabinet-server.ps1
```

The script will:
- Stop the server process using stored PID
- Fall back to port-based detection if PID file missing
- Verify the port is freed

## 10. Rollback

If the server fails to start or causes issues:

1. Stop the server:
   ```powershell
   .\tools\cabinet\stop-single-cabinet-server.ps1
   ```

2. Check logs for errors:
   ```powershell
   Get-Content runtime\starwing-single-cabinet.log -Tail 50
   Get-Content runtime\starwing-single-cabinet.log.err -Tail 50
   ```

3. Reset database if needed:
   ```powershell
   .\tools\postgresql\reset-test-database.ps1
   ```

4. Restore original `.env` from backup

## 11. Log Collection

```powershell
# Server logs
Get-Content runtime\starwing-single-cabinet.log

# Error logs
Get-Content runtime\starwing-single-cabinet.log.err

# Capture logs (if enabled)
Get-ChildItem .\captures\*.meta.json | Select-Object -First 5
```

## 12. Database Backup

```powershell
# Backup before testing
pg_dump -h localhost -U starwing_test_user starwing_test > backup_$(Get-Date -Format yyyyMMdd).sql

# Restore if needed
psql -h localhost -U starwing_test_user starwing_test < backup_20260826.sql
```

## 13. Emergency Stop

If the server becomes unresponsive:

```powershell
# Force kill by PID
$pid = Get-Content runtime\starwing-single-cabinet.pid -ErrorAction SilentlyContinue
if ($pid) { Stop-Process -Id $pid -Force }

# Or kill by port
Get-NetTCPConnection -LocalPort 4001 -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Clean up PID file
Remove-Item runtime\starwing-single-cabinet.pid -Force -ErrorAction SilentlyContinue
```

## Security Notes

- Server binds to `127.0.0.1` by default (localhost only)
- No Windows firewall rules are modified
- No DNS entries are modified
- Credentials are never hard-coded in scripts
- Capture is disabled by default
- All capture files are written outside the source tree