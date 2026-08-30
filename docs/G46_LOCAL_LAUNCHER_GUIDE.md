# Starwing Local Launcher — Operator Guide

**Version**: G46  
**Platform**: Windows 10/11 (Python 3.10, PyQt5)

---

## Quick Start

### 1. Prerequisites
- Python 3.10 with venv
- PyQt5 installed
- D: drive mapped (`subst D: "X:\StarwingParadox\D DRIVE CONTENTS"`)
- Hosts file: `127.0.0.1 dev.starwing.jp`

### 2. Launch
```bash
cd tools/local_launcher
python app.py
```

### 3. First Run
1. The launcher performs environment checks
2. Review the status cards
3. Click **Start Server Stack** to launch HTTP, proxy, and TCP
4. Click **Start Controller** to activate the mapper
5. Click **Activate Local Profile** to create a session
6. Click **Launch Game** to start Starwing

## Status Cards

| Card | Description |
|------|-------------|
| Environment | All 12 checks (critical: D drive, OpenKey, Game Config) |
| HTTP Server | Port 4001 status |
| HTTP Proxy | Port 80 status |
| TCP Matching | Port 6666 status |
| Game | Game executable status |
| Profile | Local profile session status |
| Controller | XInput/XIAPI mapper status |
| NESYS | Authentication, certificates, production matching (all Unavailable) |

## Action Buttons

| Button | Action |
|--------|--------|
| Start Server Stack | Launches HTTP server, proxy, TCP matching |
| Start Controller | Activates controller mapper |
| Activate Local Profile | Creates local profile session |
| Launch Game | Starts AcrGame-Win64-Shipping.exe |
| Emergency Stop | Stops all owned processes |
| Refresh | Re-runs environment checks |

## Session Logging

Logs are saved to `tools/local_launcher/sessions/`:
- `events.jsonl` — Timestamped event log
- `summary.json` — Session summary
- `proxy.log` — Proxy output
- `matching.log` — TCP matching output

## Safety Notes

- **NESYS status is always "Unavailable"** — this is expected
- **No online features** are available
- **No NESiCA card** is required or claimed
- **Emergency Stop** terminates only owned processes (HTTP, proxy, TCP, game)
- **Session logs** may contain sensitive information — review before sharing

## Troubleshooting

### "Environment Check Failed"
- Ensure D: drive is mapped
- Verify OpenKey.json exists
- Check DefaultGame.ini paths

### "Port Already in Use"
- Close other applications using ports 80, 4001, or 6666
- Use Emergency Stop to kill previous launcher instances

### "Game Launch Failed"
- Verify game executable exists at expected path
- Check game logs at `C:\Users\KAHO\AppData\Local\AcrGame\Saved\Logs\`

### "Controller Not Detected"
- Connect XInput controller before launching
- Check controller mapper logs
