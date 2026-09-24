@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo  Cloudflare Tunnel - expose API :8000
echo ========================================
echo.
echo 请先确保后端已启动: http://127.0.0.1:8000/health
echo.

where cloudflared >nul 2>&1
if errorlevel 1 (
  if exist "E:\JerrySoftware\cloudflared\cloudflared.exe" (
    set "CF=E:\JerrySoftware\cloudflared\cloudflared.exe"
  ) else (
    echo 未找到 cloudflared，请安装或加入 PATH
    pause
    exit /b 1
  )
) else (
  set "CF=cloudflared"
)

echo 正在启动临时公网隧道 (trycloudflare.com)...
echo 启动成功后会显示 https://xxxx.trycloudflare.com
echo 把该地址填进 miniprogram\utils\config.js 的 HOSTS.public
echo 并把 MODE 改成 public
echo.
echo 同时更新 backend\.env 的 PUBLIC_BASE_URL 为同一地址（图片才能在手机显示）
echo.
echo 按 Ctrl+C 可停止隧道
echo ----------------------------------------
echo.

"%CF%" tunnel --url http://127.0.0.1:8000

pause
endlocal
