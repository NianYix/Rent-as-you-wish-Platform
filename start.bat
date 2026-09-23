@echo off
chcp 65001 >nul
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo  乡镇租赁平台 - 本地一键启动
echo ========================================
echo.

REM --- Python venv ---
if not exist "backend\.venv\Scripts\python.exe" (
  echo [1/4] 创建 Python 虚拟环境...
  python -m venv backend\.venv
  if errorlevel 1 (
    echo 失败：请先安装 Python 3.12+ 并加入 PATH
    pause
    exit /b 1
  )
) else (
  echo [1/4] Python 虚拟环境已存在
)

REM --- backend deps ---
echo [2/4] 检查并安装后端依赖...
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -q
if errorlevel 1 (
  echo 后端依赖安装失败
  pause
  exit /b 1
)

REM --- env ---
if not exist "backend\.env" (
  if exist ".env.example" copy /Y ".env.example" "backend\.env" >nul
)
if not exist ".env" (
  if exist ".env.example" copy /Y ".env.example" ".env" >nul
)

REM --- seed ---
echo [3/4] 初始化数据库种子数据...
pushd backend
.venv\Scripts\python.exe scripts\seed.py
if errorlevel 1 (
  echo 种子脚本执行失败，仍将尝试启动服务...
)
popd

REM --- admin deps ---
if not exist "admin\node_modules\" (
  echo [4/4] 安装管理后台依赖（首次较慢）...
  pushd admin
  call npm install
  if errorlevel 1 (
    echo npm install 失败，请确认已安装 Node.js
    popd
    pause
    exit /b 1
  )
  popd
) else (
  echo [4/4] 管理后台依赖已存在
)

echo.
echo 正在新窗口启动后端 API ^(8000^) 与管理后台 ^(5173^)...
echo.

start "RAYW-Backend" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak >nul
start "RAYW-Admin" cmd /k "cd /d "%~dp0admin" && npm run dev -- --host 127.0.0.1 --port 5173"

echo 等待服务就绪...
timeout /t 4 /nobreak >nul
start "" "http://127.0.0.1:5173"
start "" "http://127.0.0.1:8000/docs"

echo.
echo ----------------------------------------
echo  管理后台: http://127.0.0.1:5173
echo  账号密码: admin / Admin@123456
echo  API 文档: http://127.0.0.1:8000/docs
echo  小程序:  用微信开发者工具打开 miniprogram 目录
echo ----------------------------------------
echo.
echo 关闭本窗口不影响服务；要停止服务请关闭标题为
echo RAYW-Backend / RAYW-Admin 的两个黑色窗口。
echo.
pause
endlocal
