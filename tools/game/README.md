# Game Launch Tools

Safe launch wrappers for Starwing Paradox game.

## Scripts

| Script | Purpose |
|--------|---------|
| `start-game.ps1` | Start game with safety checks |
| `stop-game.ps1` | Stop game and server |
| `preflight-game.ps1` | Pre-flight checks |

## Usage

### Pre-flight Check
```powershell
.\preflight-game.ps1
```

### Start Game
```powershell
.\start-game.ps1
.\start-game.ps1 -SkipServer
.\start-game.ps1 -Windowed
.\start-game.ps1 -Windowed -Resolution "1280x720"
```

### Stop Game
```powershell
.\stop-game.ps1
```

## Parameters

### start-game.ps1

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| SkipServer | Switch | False | Skip starting backend server |
| Windowed | Switch | False | Force windowed mode |
| Resolution | String | "1920x1080" | Set resolution |

## Safety Features

- Verifies game files before launch
- Checks network port availability
- Monitors game process
- Graceful shutdown on Ctrl+C
- Server cleanup on exit
