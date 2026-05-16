@echo off
REM PoultryGuardAI - Complete Startup Script
REM This script will guide you through starting the application

echo.
echo ╔═════════════════════════════════════════════════════════════╗
echo ║  🐔 POULTRYGUARDAI - COMPLETE STARTUP                      ║
echo ╚═════════════════════════════════════════════════════════════╝
echo.

echo STATUS CHECK
echo ============
echo.

REM Check if models exist
if exist "AI\models\poultry_cnn.keras" (
    echo ✓ CNN Model found
) else (
    echo ✗ CNN Model NOT found - Training in progress...
    echo   Wait for AI training to complete before starting services
    echo.
    pause
    exit /b 1
)

if exist "AI\models\isolation_forest.pkl" (
    echo ✓ Risk Model found
) else (
    echo ✗ Risk Model NOT found
    exit /b 1
)

if exist "Backend\poultryguard.db" (
    echo ✓ Database found
) else (
    echo ✗ Database NOT found - Run: python Backend\init_db.py
    pause
    exit /b 1
)

echo.
echo ✓ All components ready!
echo.

REM Start services
echo STARTING SERVICES
echo =================
echo.
echo Opening 3 terminals for:
echo   1. Backend API (port 8000)
echo   2. Frontend UI (port 3000)
echo   3. Log Monitor
echo.

timeout /t 2

REM Terminal 1: Backend
start "PoultryGuardAI - Backend" cmd /k "cd Backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

REM Terminal 2: Frontend
start "PoultryGuardAI - Frontend" cmd /k "cd Frontend && npm run dev"

echo.
echo ╔═════════════════════════════════════════════════════════════╗
echo ║  🚀 SERVICES STARTED!                                       ║
echo ╚═════════════════════════════════════════════════════════════╝
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
echo   - Check backends terminal for errors
echo.
pause
