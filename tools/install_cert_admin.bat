@echo off
setlocal

REM ============================================================
REM  Generate and install NESYS fake cert into Windows Root store
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
echo  NESYS Certificate - Generate ^& Install
echo ============================================
echo.

REM --- Step 1: Generate certificate ---
echo [1/3] Generating certificate...
python "%~dp0gen_cert.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Certificate generation failed.
    echo   Make sure 'cryptography' is installed: pip install cryptography
    pause
    exit /b 1
)
echo.

REM --- Step 2: Import into Root store ---
echo [2/3] Importing into LocalMachine\Root store...
certutil -addstore -f Root "%~dp0certs\nesys_cert.der"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] certutil import failed.
    pause
    exit /b 1
)
echo.

REM --- Step 3: Verify ---
echo [3/3] Verifying installation...
certutil -store Root cert3.nesys.jp
echo.

echo ============================================
echo   CERT INSTALLED
echo
echo   The :443 stub must load:
echo     tools\certs\nesys_bundle.pem
echo
echo   Verify with:
echo     certutil -store Root cert3.nesys.jp
echo ============================================
echo.
pause
