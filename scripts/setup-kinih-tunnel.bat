@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

echo ========================================
echo  Setup Cloudflare named tunnel
echo  Domain: api.kinih.xyz -^> 127.0.0.1:8000
echo ========================================
echo.
echo Step 1/4: Login (browser will open)...
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

"%CF%" tunnel login
if errorlevel 1 (
  echo Login failed
  pause
  exit /b 1
)

echo.
echo Step 2/4: Create tunnel rent-api (ignore error if already exists)...
"%CF%" tunnel create rent-api

echo.
echo Step 3/4: Route DNS api.kinih.xyz -^> tunnel...
echo Make sure kinih.xyz DNS is managed by Cloudflare first.
"%CF%" tunnel route dns rent-api api.kinih.xyz

echo.
echo Step 4/4: Write config.yml ...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0write-cloudflare-config.ps1"
if errorlevel 1 (
  echo Failed to write config.yml
  pause
  exit /b 1
)

echo.
echo Done. Next:
echo   1. Start backend (start.bat)
echo   2. Run scripts\start-named-tunnel.bat
echo   3. Open https://api.kinih.xyz/health
echo   4. WeChat MP admin: add api.kinih.xyz as request/uploadFile/downloadFile domain
echo.
pause
endlocal
