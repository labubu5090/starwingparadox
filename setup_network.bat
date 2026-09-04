@echo off
echo ====================================
echo  NESYS Network Setup (Run as Admin)
echo ====================================
echo.

echo 1. Installing certificate to Trusted Root...
certutil -addstore -f Root "%~dp0server\certs\nesys_all.pem"
certutil -addstore -f Root "%~dp0server\certs\cert3_nesys_jp.pem"
certutil -addstore -f Root "%~dp0server\certs\cert2_nesys_jp.pem"
echo.

echo 2. Setting WinHTTP proxy to route through local stub...
netsh winhttp set proxy proxy-server="http=127.0.0.1:80;https=127.0.0.1:443" bypass-list="localhost;127.0.0.1;dev.starwing.jp"
echo.

echo 3. Flushing DNS...
ipconfig /flushdns
echo.

echo ====================================
echo  Setup complete! You can close this.
echo ====================================
pause
