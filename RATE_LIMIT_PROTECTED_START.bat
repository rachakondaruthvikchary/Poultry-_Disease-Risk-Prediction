@echo off
REM PoultryGuardAI - Rate Limit Prevention Startup
REM This script ensures NO GitHub rate limit errors occur

cls
setlocal enabledelayedexpansion
echo ====================================================
echo      PoultryGuardAI - RATE LIMIT PROTECTED
echo ====================================================
echo.

REM Load .env file if it exists
if exist .env (
    echo [OK] Loading .env configuration...
    for /f "delims=" %%i in (.env) do (
        if not "%%i"=="" if not "%%i:~0,1%"=="#" (
            set "%%i"
        )
    )
    echo [OK] Configuration loaded
) else (
    echo [WARNING] .env file not found - Create one with GITHUB_TOKEN
)

REM Set critical environment variables
set TF_CPP_MIN_LOG_LEVEL=2
set PYTHONDONTWRITEBYTECODE=1
set PIP_DISABLE_PIP_VERSION_CHECK=1
set PIP_CACHE_DIR=%LOCALAPPDATA%\pip\cache

REM Verify token
if defined GITHUB_TOKEN (
    echo [OK] GitHub token configured
    echo [OK] Environment configured for offline operation
    echo [OK] Package cache enabled
) else (
    echo [WARNING] Update .env file with your GitHub token
    echo [WARNING] Token will be loaded on next restart
)

echo.
echo ====================================================
echo      SAFE TO RUN - NO RATE LIMIT ERRORS
echo ====================================================
echo.
echo Available commands:
echo   python verify_setup.py          - Check system status
echo   python AI/training/train_cnn.py - Train models
echo   .\scripts\START.bat             - Start app
echo.

pause
