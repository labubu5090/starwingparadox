@echo off
echo ============================================
echo  NESYS Certificate Setup (Run as Admin)
echo ============================================
echo.

REM 1. Add hosts file entries
echo Adding hosts file entries...
findstr /C:"cert3.nesys.jp" C:\Windows\System32\drivers\etc\hosts >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo. >> C:\Windows\System32\drivers\etc\hosts
    echo # NESYS stub for StarwingParadox >> C:\Windows\System32\drivers\etc\hosts
    echo 127.0.0.1 cert3.nesys.jp >> C:\Windows\System32\drivers\etc\hosts
    echo 127.0.0.1 cert2.nesys.jp >> C:\Windows\System32\drivers\etc\hosts
    echo 127.0.0.1 proxy.nesys.jp >> C:\Windows\System32\drivers\etc\hosts
    echo 127.0.0.1 data.nesys.jp >> C:\Windows\System32\drivers\etc\hosts
    echo 127.0.0.1 nesys.taito.co.jp >> C:\Windows\System32\drivers\etc\hosts
    echo Hosts entries added.
) else (
    echo Hosts entries already exist.
)
echo.

REM 2. Install certificates
echo Installing certificates into Windows cert stores...
certutil -addstore -f Root "%~dp0certs\nesys_all.pem"
certutil -addstore -f CA "%~dp0certs\nesys_all.pem"
certutil -addstore -f My "%~dp0certs\nesys_all.pem"
echo.

REM 3. Flush DNS cache
ipconfig /flushdns
echo.

echo ============================================
echo  Setup complete! Close this window.
echo  Then start the NESYS cert stub:
echo  python tools\nesys_cert_stub.py
echo ============================================
pause
