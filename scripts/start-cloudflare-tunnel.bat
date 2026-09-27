@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

echo ========================================
echo  Cloudflare Tunnel + auto write config
echo ========================================
echo.
echo  Will start cloudflared to :8000
echo  Then write URL into:
echo    miniprogram\utils\config.js  (MODE=public, HOSTS.public)
echo    backend\.env  PUBLIC_BASE_URL
echo.
echo  Make sure backend is running first.
echo  Press Ctrl+C to stop the tunnel.
echo ----------------------------------------
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-cloudflare-tunnel.ps1"
set ERR=%ERRORLEVEL%
echo.
if not "%ERR%"=="0" echo Tunnel failed, exit code %ERR%
pause
exit /b %ERR%
