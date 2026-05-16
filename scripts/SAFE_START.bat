@echo off
REM PoultryGuardAI - Safe Startup Script
REM Sets up all required environment variables before running

setlocal enabledelayedexpansion

echo.
echo ===================================
echo PoultryGuardAI - Startup Configuration
echo ===================================
echo.

REM Set GitHub Token (keep it private)
if not defined GITHUB_TOKEN (
    echo [WARNING] GitHub token not set. Skipping GitHub API features...
) else (
    echo [OK] GitHub token configured
)

REM Verify pip configuration
echo [INFO] Verifying pip configuration...
if exist "%LOCALAPPDATA%\pip\pip.ini" (
    echo [OK] pip.ini found - Using cached packages
) else (
    echo [WARNING] pip.ini not found - Packages will be installed as needed
)

REM Test if requirements can be installed
echo [INFO] Testing package manager...
python -m pip list --format=columns | find "tensorflow" >nul
if %errorlevel% equ 0 (
    echo [OK] TensorFlow already installed - No API calls needed
) else (
    echo [INFO] Will install packages from cache
)

REM Set critical environment variables
set TF_CPP_MIN_LOG_LEVEL=2
set PIP_CACHE_DIR=%LOCALAPPDATA%\pip\cache
set PYTHONUNBUFFERED=1

echo [OK] Environment configured safely
echo [INFO] Python logging reduced, pip cache configured
echo.
echo Ready to start services...
echo.

REM Now proceed with normal startup
pause
