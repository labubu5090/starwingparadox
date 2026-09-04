@echo off
setlocal

REM ============================================================
REM  Remove NESYS fake cert from Windows Root store
REM  Must run as Administrator.
REM ============================================================

REM --- Self-elevation ---
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges...
    PowerShell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

echo ============================================
echo  NESYS Certificate - Uninstall
echo ============================================
echo.

echo Removing cert3.nesys.jp from Root store...
certutil -delstore Root cert3.nesys.jp
echo.

echo Fake nesys cert removed from Root store.
echo.
pause
