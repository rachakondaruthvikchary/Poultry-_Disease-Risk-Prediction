@echo off
echo =====================================
echo  PoultryGuard AI - Frontend Startup
echo =====================================
echo.

if not exist "%~dp0..\Frontend\." (
    echo [ERROR] Frontend folder not found: "%~dp0..\Frontend"
    exit /b 1
)
cd /d "%~dp0..\Frontend"

if not exist node_modules (
    echo Installing dependencies...
    call npm install
)

if not exist .env.local (
    if exist .env.example (
        echo Creating .env.local from example...
        copy .env.example .env.local
    ) else (
        echo [ERROR] .env.example not found in Frontend. Please create .env.local manually.
        exit /b 1
    )
)

echo.
echo Starting Next.js development server...
echo App will be at: http://localhost:3000
echo.

start "PoultryGuard Frontend" cmd /k "cd /d "%~dp0..\Frontend" && npm run dev"

timeout /t 8 /nobreak >nul

echo Opening browser...
start "" "http://localhost:3000"
