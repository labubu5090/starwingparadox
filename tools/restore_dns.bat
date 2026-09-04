@echo off
REM Restore DNS settings to DHCP (original)
echo Restoring DNS to DHCP...
for /f "tokens=4*" %%a in ('netsh interface show interface ^| findstr /i "Connected"') do (
    set IFACE=%%b
)
echo Interface: %IFACE%
netsh interface ip set dns "%IFACE%" dhcp
ipconfig /flushdns
echo DNS restored to DHCP.
pause
