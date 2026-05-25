@echo off
echo =====================================
echo  PoultryGuard AI - Backend API
echo =====================================
echo.

REM Ensure Backend folder exists relative to scripts folder
if not exist "%~dp0..\Backend\." (
    echo [ERROR] Backend folder not found: "%~dp0..\Backend"
    exit /b 1
)
cd /d "%~dp0..\Backend"

if not exist venv (
    echo Creating virtual environment...
    where python >nul 2>&1
    if ERRORLEVEL 1 (
        echo [ERROR] Python not found in PATH. Install Python 3.10+ and retry.
        exit /b 1
    )
    python -m venv venv
    if ERRORLEVEL 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if "%VIRTUAL_ENV%"=="" (
    echo [ERROR] Virtual environment activation failed. Aborting to avoid using global Python.
    exit /b 1
)

if not exist .env (
    if exist .env.example (
        echo Creating .env file from example...
        copy .env.example .env
        echo.
        echo IMPORTANT: Edit Backend\.env with your settings!
        echo.
        pause
    ) else (
        echo [ERROR] .env.example not found. Please create .env before starting.
        exit /b 1
    )
)

echo Installing dependencies...
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found in Backend folder.
    exit /b 1
)
pip install -r requirements.txt
if ERRORLEVEL 1 (
    echo.
    echo [WARN] Some packages failed to install. This is usually OK.
    echo [WARN] The backend will still work with built-in fallback features.
    echo.
)

echo.
echo Starting Backend API Server...
echo Server will be at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.

if "%HOST%"=="" set HOST=127.0.0.1
REM Default to localhost for development; use 0.0.0.0 only for Docker or explicit exposure
uvicorn app.main:app --reload --host %HOST% --port 8000
