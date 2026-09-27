@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

echo ========================================
echo  Cloudflare named tunnel: api.kinih.xyz
echo ========================================
echo.
echo Backend should be running at http://127.0.0.1:8000
echo Keep this window open.
echo.

where cloudflared >nul 2>&1
if errorlevel 1 (
  if exist "E:\JerrySoftware\cloudflared\cloudflared.exe" (
    set "CF=E:\JerrySoftware\cloudflared\cloudflared.exe"
  ) else (
    echo cloudflared not found
    pause
    exit /b 1
  )
) else (
  set "CF=cloudflared"
)

if not exist "%USERPROFILE%\.cloudflared\config.yml" (
  echo Missing config.yml. Run scripts\setup-kinih-tunnel.bat first.
  pause
  exit /b 1
)

"%CF%" tunnel run rent-api
pause
endlocal
