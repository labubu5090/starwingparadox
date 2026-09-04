@echo off
echo Installing NESYS certificates...
certutil -addstore -f Root "%~dp0cert3_nesys_jp.pem"
certutil -addstore -f Root "%~dp0cert2_nesys_jp.pem"
certutil -addstore -f My "%~dp0cert3_nesys_jp.pem"
certutil -addstore -f My "%~dp0cert2_nesys_jp.pem"
echo Done!
pause
