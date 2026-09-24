@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo  Rent As You Wish - local start
echo ========================================
echo.

set "ROOT=%~dp0"
set "PY=%ROOT%backend\.venv\Scripts\python.exe"
set "BACKEND=%ROOT%backend"
set "ADMIN=%ROOT%admin"

REM --- Python venv ---
if not exist "%PY%" (
  echo [1/4] Creating Python venv...
  python -m venv "%BACKEND%\.venv"
  if errorlevel 1 (
    echo Failed: install Python 3.12+ and add to PATH
    pause
    exit /b 1
  )
) else (
  echo [1/4] Python venv OK
)

REM --- backend deps ---
echo [2/4] Installing backend deps...
"%PY%" -m pip install -r "%BACKEND%\requirements.txt" -q
if errorlevel 1 (
  echo Backend pip install failed
  pause
  exit /b 1
)

REM --- env ---
if not exist "%BACKEND%\.env" (
  if exist "%ROOT%.env.example" copy /Y "%ROOT%.env.example" "%BACKEND%\.env" >nul
)
if not exist "%ROOT%.env" (
  if exist "%ROOT%.env.example" copy /Y "%ROOT%.env.example" "%ROOT%.env" >nul
)

REM --- seed ---
echo [3/4] Seeding database...
pushd "%BACKEND%"
"%PY%" scripts\seed.py
if errorlevel 1 echo Seed failed, will still try to start services...
popd

REM --- admin deps ---
if not exist "%ADMIN%\node_modules\" (
  echo [4/4] Installing admin deps first time, please wait...
  pushd "%ADMIN%"
  call npm.cmd install
  if errorlevel 1 (
    echo npm install failed, install Node.js first
    popd
    pause
    exit /b 1
  )
  popd
) else (
  echo [4/4] Admin deps OK
)

echo.
echo Starting Backend :8000 and Admin :5173 ...
echo.

REM Use /D to set working dir - avoid nested quotes breaking paths
start "RAYW-Backend" /D "%BACKEND%" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak >nul
start "RAYW-Admin" /D "%ADMIN%" cmd /k "npm.cmd run dev -- --host 127.0.0.1 --port 5173"

echo Waiting for services...
timeout /t 5 /nobreak >nul
start "" "http://127.0.0.1:5173/"
start "" "http://127.0.0.1:8000/docs"

echo.
echo ----------------------------------------
echo  Admin:  http://127.0.0.1:5173
echo  Login:  admin / Admin@123456
echo  API:    http://127.0.0.1:8000/docs
echo  MiniProgram: open miniprogram/ in WeChat DevTools
echo ----------------------------------------
echo.
echo Close RAYW-Backend / RAYW-Admin windows to stop services.
echo.
pause
endlocal
