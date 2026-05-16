@echo off
echo =====================================
echo  Database Initialization
echo =====================================
echo.

REM Switch to project root (parent of scripts folder)
cd /d "%~dp0.."

if not exist Backend\venv (
    echo Virtual environment not found!
    echo Run start-backend.bat first.
    pause
    exit /b 1
)
if not exist Backend\venv\Scripts\activate.bat (
    echo Activation script not found: Backend\venv\Scripts\activate.bat
    pause
    exit /b 1
)

call Backend\venv\Scripts\activate.bat

echo Initializing database tables...
python Database\migrations\init_db.py
if ERRORLEVEL 1 (
    echo [ERROR] Database initialization script failed with exit code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ Database initialized!
pause
