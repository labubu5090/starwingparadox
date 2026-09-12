@echo off
setlocal
rem ============================================================
rem  One-key Starwing: servers + NESYS pipe + open game + patch
rem  Runs tools\g112_fullstack.py (no --server-only):
rem    1. HTTP :4001 uvicorn     (skipped if port busy)
rem    2. HTTP :80   proxy       (skipped if port busy)
rem    3. TCP  :6666 matching    (skipped if port busy)
rem    4. NESYS pipe             (skipped if pipe exists)
rem    5. g79 keepalive = launch game + apply ALL patches
rem       (card mount, drive rewire, etc.) + watch log
rem  Safe to re-run; keep the window open, Ctrl+C stops all.
rem ============================================================
set "ROOT=C:\Users\KAHO\Pictures\Starwing"
set "PY=C:\Users\KAHO\AppData\Local\Programs\Python\Python310\python.exe"

cd /d "%ROOT%"
echo [Starwing] one-key startup: servers + NESYS pipe + game + patch...
"%PY%" "%ROOT%\tools\g112_fullstack.py"
echo.
echo [Starwing] stack stopped.
pause