@echo off
REM Frontend startup wrapper for PoultryGuardAI

set "SCRIPT_DIR=%~dp0"

echo.
echo 🐔 PoultryGuardAI - Frontend Startup
echo =====================================
echo.

call "%SCRIPT_DIR%scripts\start-frontend.bat"
