@echo off
echo =====================================
echo  Train AI Models
echo =====================================
echo.

REM Run from project root
cd /d "%~dp0.."

if not exist Backend\venv (
    echo Virtual environment not found!
    echo Run start-backend.bat first.
    pause
    exit /b 1
)
if not exist Backend\venv\Scripts\activate.bat (
    echo Activation script missing: Backend\venv\Scripts\activate.bat
    exit /b 1
)

call Backend\venv\Scripts\activate.bat
if "%VIRTUAL_ENV%"=="" (
    echo [ERROR] Virtual environment activation failed.
    exit /b 1
)

echo Training CNN model...
python AI\training\train_cnn.py
if ERRORLEVEL 1 (
    echo [ERROR] CNN training failed with exit code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

echo.
echo Training Risk model...
python AI\training\train_risk_model.py
if ERRORLEVEL 1 (
    echo [ERROR] Risk model training failed with exit code %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ Models trained and saved to AI\models\
pause
