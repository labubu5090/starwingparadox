@echo off
setlocal enabledelayedexpansion
rem ============================================================
rem  Starwing mock-server stack launcher
rem  Starts (each skipped if its port/pipe is already in use):
rem    1. HTTP :4001  via uvicorn app.main:app        (server\.venv)
rem    2. HTTP :80    via tools\g30_proxy.py          (server\.venv)
rem    3. TCP  :6666  via server -m app.tcp_server    (server\.venv)
rem    4. NESYS pipe   \\.\pipe\nesys_games           (system python)
rem  Re-running this file is safe: busy ports are skipped, so the
rem  double-stack problem cannot recur. Ctrl+C in this window stops
rem  the children started by this run.
rem  Game is NOT launched (use ..\AcrGame\open game.bat).
rem ============================================================

set "ROOT=C:\Users\KAHO\Pictures\Starwing"
set "PY=%ROOT%\server\.venv\Scripts\python.exe"

if not exist "%PY%" (
    echo [ERROR] venv python not found: %PY%
    pause
    exit /b 1
)

echo [Starwing] starting mock-server stack (ports 4001/80/6666 + NESYS pipe)...
"%PY%" "%ROOT%\tools\g112_fullstack.py" --server-only

echo.
echo [Starwing] server stack stopped.
pause