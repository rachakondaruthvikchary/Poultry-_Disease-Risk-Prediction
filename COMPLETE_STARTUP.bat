@echo off
REM PoultryGuardAI - Complete Startup Script
REM This script will guide you through starting the application

echo.
echo ========================================================
echo   POULTRYGUARDAI - COMPLETE STARTUP
echo ========================================================
echo.

echo STATUS CHECK
echo ============
echo.

REM Check if Backend exists
if not exist "%~dp0Backend\app\main.py" (
    echo [ERROR] Backend not found!
    pause
    exit /b 1
)

if exist "%~dp0Backend\poultryguard.db" (
    echo [OK] Database found
) else (
    echo [WARN] Database NOT found - will be created on first start
)

if exist "%~dp0AI\models\poultry_cnn.keras" (
    echo [OK] CNN Model found
) else (
    echo [INFO] CNN Model not found - backend will use fallback prediction
)

if exist "%~dp0AI\models\isolation_forest.pkl" (
    echo [OK] Risk Model found
) else (
    echo [INFO] Risk Model not found - backend will use heuristic prediction
)

echo.
echo [OK] Starting services...
echo.

REM Start Backend with proper venv activation
echo STARTING SERVICES
echo =================
echo.
echo Starting Backend API (port 8000)...
start "PoultryGuardAI - Backend" cmd /k "cd /d "%~dp0Backend" && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting Frontend UI (port 3000)...
start "PoultryGuardAI - Frontend" cmd /k "cd /d "%~dp0Frontend" && npm run dev"

echo.
echo ========================================================
echo   SERVICES STARTED!
echo ========================================================
echo.
echo ACCESS POINTS:
echo   Frontend:     http://localhost:3000
echo   API Docs:     http://localhost:8000/docs
echo   API Health:   http://localhost:8000/api/health
echo.
echo LOGIN CREDENTIALS:
echo   Email:        test@test.com
echo   Password:     test1234
echo.
echo NOTES:
echo   - Keep both terminal windows open
echo   - Close any terminal to stop services
echo   - Check backend terminal for errors
echo.
pause
