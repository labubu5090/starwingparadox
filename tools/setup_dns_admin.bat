@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  NESYS DNS Interceptor Setup (requires Administrator)
REM
REM  1. Stops SharedAccess (ICS) which holds UDP port 53
REM  2. Disables SharedAccess so it doesn't restart
REM  3. Sets DNS to 127.0.0.1 on the active adapter
REM  4. Launches dns_intercept.py on port 53
REM ============================================================

REM --- Self-elevation check ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges...
    PowerShell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

echo ============================================
echo  NESYS DNS Interceptor - Setup
echo ============================================
echo.

REM --- Detect active adapter (one with a default gateway) ---
set "ADAPTER="
for /f "tokens=4*" %%a in ('netsh interface show interface ^| findstr /i "Connected Dedicated"') do (
    set "CANDIDATE=%%b"
    for /f "tokens=3" %%g in ('netsh interface ip show config name="!CANDIDATE!" 2^>nul ^| findstr /i "Default Gateway"') do (
        if not "%%g"=="None" if not "%%g"=="" (
            set "ADAPTER=!CANDIDATE!"
        )
    )
)

if "!ADAPTER!"=="" (
    echo [WARNING] Could not auto-detect active adapter.
    echo   Defaulting to "Wi-Fi". Edit the ADAPTER variable in this file if wrong.
    set "ADAPTER=Wi-Fi"
)
echo Active adapter: !ADAPTER!
echo.

REM --- Save current DNS config ---
echo Saving current DNS config to tools\dns_backup.txt ...
netsh interface ip show config name="!ADAPTER!" > "%~dp0dns_backup.txt" 2>&1
echo   Saved.
echo.

REM --- Step 1: Stop SharedAccess ---
echo [1/5] Stopping SharedAccess (ICS)...
sc stop SharedAccess >nul 2>&1
timeout /t 2 /nobreak >nul
echo   Done.
echo.

REM --- Step 2: Disable SharedAccess so it doesn't come back ---
echo [2/5] Disabling SharedAccess auto-start...
sc config SharedAccess start= disabled >nul 2>&1
echo   Done.
echo.

REM --- Step 3: Verify port 53 is free ---
echo [3/5] Verifying UDP port 53 is free...
set "PORT53_USED=0"
for /f "tokens=5" %%p in ('netstat -ano -p UDP 2^>nul ^| findstr ":53 "') do (
    set "PORT53_PID=%%p"
    set "PORT53_USED=1"
)
if "!PORT53_USED!"=="1" (
    echo.
    echo   [ERROR] UDP port 53 is STILL held by PID !PORT53_PID!
    echo   SharedAccess may need more time to release, or another service grabbed it.
    echo.
    pause
    exit /b 1
)
echo   Port 53 is free.
echo.

REM --- Step 4: Set DNS to 127.0.0.1 ---
echo [4/5] Setting DNS to 127.0.0.1 on "!ADAPTER!"...
netsh interface ip set dns name="!ADAPTER!" static 127.0.0.1 primary
if %errorlevel% neq 0 (
    echo   [ERROR] Failed to set DNS. Check adapter name.
    pause
    exit /b 1
)
echo   Done.
echo.

REM --- Step 5: Flush DNS cache ---
echo [5/5] Flushing DNS cache...
ipconfig /flushdns
echo.

REM --- Launch DNS interceptor ---
echo Starting DNS interceptor...
start "DNS-Intercept" /min python "%~dp0dns_intercept.py"
timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo   PATH 1 ACTIVE
echo
echo   DNS interceptor is running.
echo   cert3.nesys.jp -> 127.0.0.1
echo   cert2.nesys.jp -> 127.0.0.1
echo   proxy.nesys.jp -> 127.0.0.1
echo   data.nesys.jp  -> 127.0.0.1
echo   nesys.taito.co.jp -> 127.0.0.1
echo.
echo   Verify with:
echo     nslookup cert3.nesys.jp 127.0.0.1
echo.
echo   Now restart the game.
echo ============================================
echo.
pause
