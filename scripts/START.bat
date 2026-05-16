@echo off
REM PoultryGuard AI - Startup Script for Windows
REM This script starts both the backend and frontend servers

echo.
echo  ========================================
echo  PoultryGuard AI - System Startup
echo  ========================================
echo.

REM Kill any existing processes started by previous runs of this script
echo [1/3] Cleaning up existing PoultryGuard windows...
taskkill /F /FI "WINDOWTITLE eq PoultryGuard Backend" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq PoultryGuard Frontend" >nul 2>&1
timeout /t 2 /nobreak >nul

REM Start Backend
echo [2/3] Starting Backend Server (port 8000)...
if not exist "%~dp0..\Backend\." (
  echo [ERROR] Backend folder not found: "%~dp0..\Backend"
  exit /b 1
)
cd /d "%~dp0..\Backend"
if not exist ".\venv\Scripts\activate.bat" (
  echo [ERROR] Virtualenv activation script not found: .\venv\Scripts\activate.bat
  exit /b 1
)
call .\venv\Scripts\activate.bat
if "%HOST%"=="" set HOST=127.0.0.1
start "PoultryGuard Backend" cmd /k "python -m uvicorn app.main:app --host %HOST% --port 8000 --workers 1"
timeout /t 5 /nobreak >nul

REM Start Frontend
echo [3/3] Starting Frontend Server (port 3000)...
if not exist "%~dp0..\Frontend\." (
  echo [ERROR] Frontend folder not found: "%~dp0..\Frontend"
  exit /b 1
)
cd /d "%~dp0..\Frontend"
start "PoultryGuard Frontend" cmd /k "npm run start -- -p 3000"
timeout /t 5 /nobreak >nul

echo [4/4] Verifying servers...
timeout /t 3 /nobreak >nul

powershell -Command ^
  "$backend = try { (Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 3).StatusCode } catch { 'offline' }; " ^
  "$frontend = try { (Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 3).StatusCode } catch { 'offline' }; " ^
  "if ($backend -eq 200 -and $frontend -eq 200) { Write-Host 'SUCCESS: All systems running!' -ForegroundColor Green; Write-Host 'Access at: http://localhost:3000' -ForegroundColor Cyan; exit 0 } else { Write-Host \"Backend: $backend, Frontend: $frontend\" -ForegroundColor Red; exit 2 }"

if %ERRORLEVEL% EQU 0 (
  echo.
  echo  ========================================
  echo  PoultryGuard AI - Ready!
  echo  ========================================
  echo.
  echo  Access the application at:
  echo   -> http://localhost:3000
  echo.
  echo  API Documentation:
  echo   -> http://localhost:8000/docs
  echo.
  pause
  echo.
  echo  ========================================
  echo  Startup Complete
  echo  ========================================
  echo.
  pause
) else (
  echo [ERROR] One or more services failed verification. See above for details.
  exit /b %ERRORLEVEL%
)
