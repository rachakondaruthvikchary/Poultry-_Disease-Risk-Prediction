@echo off
REM Backend startup wrapper for PoultryGuardAI

set "SCRIPT_DIR=%~dp0"

echo.
echo 🐔 PoultryGuardAI - Backend Startup
echo =====================================
echo.

call "%SCRIPT_DIR%scripts\start-backend.bat"
