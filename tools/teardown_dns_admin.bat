@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  NESYS DNS Interceptor Teardown (requires Administrator)
REM
REM  1. Kills the DNS interceptor process
REM  2. Restores DNS to DHCP
REM  3. Re-enables SharedAccess
REM ============================================================

REM --- Self-elevation check ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges...
    PowerShell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

echo ============================================
echo  NESYS DNS Interceptor - Teardown
echo ============================================
echo.

REM --- Detect adapter (same logic as setup) ---
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
    echo [WARNING] Could not auto-detect adapter. Defaulting to "Wi-Fi".
    set "ADAPTER=Wi-Fi"
)
echo Active adapter: !ADAPTER!
echo.

REM --- Step 1: Kill DNS interceptor ---
echo [1/4] Stopping DNS interceptor...
taskkill /FI "WINDOWTITLE eq DNS-Intercept*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq DNS-Intercept*" /F >nul 2>&1
REM Also kill any python process running dns_intercept.py
for /f "tokens=2" %%p in ('tasklist /fi "imagename eq python.exe" /fo list 2^>nul ^| findstr "PID:"') do (
    wmic process where "ProcessId=%%p" get CommandLine 2>nul | findstr "dns_intercept" >nul 2>&1
    if !errorlevel! equ 0 (
        echo   Killing PID %%p
        taskkill /PID %%p /F >nul 2>&1
    )
)
echo   Done.
echo.

REM --- Step 2: Restore DNS to DHCP ---
echo [2/4] Restoring DNS to DHCP on "!ADAPTER!"...
netsh interface ip set dns name="!ADAPTER!" dhcp
echo   Done.
echo.

REM --- Step 3: Re-enable SharedAccess ---
echo [3/4] Re-enabling SharedAccess...
sc config SharedAccess start= demand >nul 2>&1
sc start SharedAccess >nul 2>&1
echo   Done.
echo.

REM --- Step 4: Flush DNS cache ---
echo [4/4] Flushing DNS cache...
ipconfig /flushdns
echo.

echo ============================================
echo   DNS restored to DHCP.
echo   SharedAccess re-enabled.
echo   DNS interceptor stopped.
echo.
echo   If you saved dns_backup.txt, you can
echo   compare with: netsh interface ip show config
echo ============================================
echo.
pause
