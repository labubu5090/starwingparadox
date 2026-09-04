@echo off
echo Adding firewall rules...

REM Block game from reaching ANY external IP on port 443
netsh advfirewall firewall add rule name="NESYS_BlockExternal443" dir=out action=block protocol=TCP remoteport=443 remoteip=any program="X:\StarwingParadox\WindowsNoEditor\AcrGame-Win64-Shipping.exe" enable=yes

REM Also block the launcher
netsh advfirewall firewall add rule name="NESYS_BlockExternal443_Launcher" dir=out action=block protocol=TCP remoteport=443 remoteip=any program="X:\StarwingParadox\WindowsNoEditor\AcrGame.exe" enable=yes

REM Allow localhost on 443
netsh advfirewall firewall add rule name="NESYS_AllowLocalhost443" dir=out action=allow protocol=TCP remoteport=443 remoteip=127.0.0.1 program="X:\StarwingParadox\WindowsNoEditor\AcrGame-Win64-Shipping.exe" enable=yes
netsh advfirewall firewall add rule name="NESYS_AllowLocalhost443_Launcher" dir=out action=allow protocol=TCP remoteport=443 remoteip=127.0.0.1 program="X:\StarwingParadox\WindowsNoEditor\AcrGame.exe" enable=yes

echo Done!
pause
