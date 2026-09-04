@echo off
echo y | certutil -addstore -f Root "%~dp0cert3_nesys_jp.pem"
echo y | certutil -addstore -f Root "%~dp0cert2_nesys_jp.pem"
echo y | certutil -addstore -f CA "%~dp0cert3_nesys_jp.pem"
echo y | certutil -addstore -f CA "%~dp0cert2_nesys_jp.pem"
echo y | certutil -addstore -f My "%~dp0cert3_nesys_jp.pem"
echo y | certutil -addstore -f My "%~dp0cert2_nesys_jp.pem"
echo DONE
