# Cabinet Capture Runbook

## Overview

The raw capture mode records HTTP request/response pairs for cabinet network debugging.
It is **disabled by default** and must be explicitly enabled.

## Prerequisites

- Run the server on an **isolated network** (no internet-facing exposure).
- Ensure the capture directory is **outside tracked source** (default: `../cabinet-captures/`).
- Verify disk space — each capture writes a `.meta.json` sidecar and optional `.req.bin`/`.resp.bin` files.

## Safe Isolated Network Recommendation

| Requirement | Detail |
|---|---|
| Network isolation | Cabinet traffic must not route through public internet |
| Firewall rules | Block inbound from untrusted sources |
| VPN or air-gap | Preferred for production captures |
| Local-only binding | Bind server to `127.0.0.1` or private VLAN |

## Server Startup with Capture

```bash
# Enable capture via environment variable
export STARWING_CAPTURE_ENABLED=1
export STARWING_CAPTURE_DIR=/path/to/cabinet-captures

# Start the server
cd server
python -m uvicorn app.main:app --host 0.0.0.0 --port 4001
```

Or enable at runtime via Python:

```python
from app.capture import enable_capture
from pathlib import Path

enable_capture(Path("/path/to/captures"))
```

## Capture Enablement / Disablement

| Action | Method |
|---|---|
| Enable at startup | Set `STARWING_CAPTURE_ENABLED=1` |
| Enable at runtime | `enable_capture(optional_dir)` |
| Disable at runtime | `disable_capture()` |
| Check status | `is_capture_enabled()` |
| Get directory | `get_capture_dir()` |

## Verification Steps

1. Confirm capture is enabled:
   ```python
   from app.capture import is_capture_enabled, get_capture_dir
   assert is_capture_enabled() is True
   assert get_capture_dir() is not None
   ```

2. Send a test request to the server.

3. Check for `.meta.json` files in the capture directory:
   ```bash
   ls -la /path/to/cabinet-captures/*.meta.json
   ```

4. Validate a sidecar file:
   ```python
   import json
   from pathlib import Path

   meta = json.loads(Path("captures/capture_...meta.json").read_text())
   assert "correlation_id" in meta
   assert "request_body_sha256" in meta
   assert "response_body_sha256" in meta
   ```

## File Naming Convention

```
capture_{ISO8601-UTC}_{short-uuid}.meta.json
capture_{ISO8601-UTC}_{short-uuid}.req.bin     (optional)
capture_{ISO8601-UTC}_{short-uuid}.resp.bin    (optional)
```

Example:
```
capture_20260826T143022.123456Z_a1b2c3d4.meta.json
capture_20260826T143022.123456Z_a1b2c3d4.req.bin
capture_20260826T143022.123456Z_a1b2c3d4.resp.bin
```

## Redaction Procedures

The following fields are **automatically redacted** in captured metadata:

| Field | Redaction |
|---|---|
| `Authorization` header | Replaced with `***` |
| `Cookie` header | Replaced with `***` |
| `x-galaxy-api-id` header | Replaced with `***` |
| `password` header | Replaced with `***` |
| `token` header | Replaced with `***` |
| `secret` header | Replaced with `***` |
| Cabinet IDs (10+ digit numbers) | Replaced with `***` |

**Before sharing captures**, verify redaction:
```python
from app.capture import redact_headers, redact_cabinet_id

# Check headers
assert redact_headers({"Authorization": "Bearer xyz"}) == {"Authorization": "***"}

# Check cabinet IDs
assert "12345678901234" not in redact_cabinet_id("cabinet 12345678901234")
```

## Packaging for Analysis

```bash
# Create a tarball of captures (excludes raw binaries by default)
tar czf cabinet-captures-$(date +%Y%m%d).tar.gz /path/to/cabinet-captures/

# Or zip
zip -r cabinet-captures-$(date +%Y%m%d).zip /path/to/cabinet-captures/
```

Include only `.meta.json` files for general analysis.
Include `.req.bin`/`.resp.bin` only when raw protocol inspection is needed.

## Git Exclusion

The capture directory is **not** inside the repository source tree.
The `.gitignore` already excludes `*.db` and common artifacts.

If captures end up inside the repo accidentally:
```bash
git rm -r --cached cabinet-captures/
echo "cabinet-captures/" >> .gitignore
```

## Rollback to Legacy Server

1. Disable capture:
   ```python
   from app.capture import disable_capture
   disable_capture()
   ```

2. Stop the Python server.

3. Restart the legacy Node.js server:
   ```bash
   cd legacy-js
   node server.js
   ```

4. Verify legacy server is responding:
   ```bash
   curl -X POST http://localhost:4001/health
   ```

## Emergency Stop

If capture is causing performance issues or disk pressure:

```python
from app.capture import disable_capture
disable_capture()
```

Or set environment variable and restart:
```bash
export STARWING_CAPTURE_ENABLED=0
# Restart server
```

The server continues operating normally with capture disabled.
No data loss occurs — existing capture files remain on disk.
