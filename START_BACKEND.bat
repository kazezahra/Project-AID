@echo off
REM Autism Prescreening Tool - Startup Script
REM Run this script from Windows command prompt or PowerShell

echo.
echo ============================================================
echo   AUTISM PRE-SCREENING TOOL - Startup
echo ============================================================
echo.

REM Get the project root directory
setlocal
cd /d "%~dp0"
set PROJECT_ROOT=%cd%

echo [INFO] Project root: %PROJECT_ROOT%
echo.

REM Check if Python is installed
echo [CHECK] Verifying Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] %PYTHON_VERSION% found
echo.

REM Check virtual environment
echo [CHECK] Creating/activating virtual environment...
if not exist "%PROJECT_ROOT%\venv" (
    echo [INFO] Creating virtual environment...
    python -m venv "%PROJECT_ROOT%\venv"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call "%PROJECT_ROOT%\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [CHECK] Installing dependencies...
pip install -q -r "%PROJECT_ROOT%\app\api\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    echo [INFO] Try running manually: pip install -r "%PROJECT_ROOT%\app\api\requirements.txt"
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Verify imports
echo [CHECK] Verifying Python modules...
python -c "import flask, flask_cors, pandas, sklearn, joblib, reportlab, groq; print('[OK] All modules available')" 2>nul
if errorlevel 1 (
    echo [WARNING] Some modules may be missing, but Flask should work
)
echo.

REM Start Flask application
echo [INFO] Starting Flask backend on http://localhost:5000
echo.
echo ============================================================
echo   BACKEND RUNNING - Keep this window open!
echo   Access frontend at: file:///%PROJECT_ROOT%\frontend\AID-FYP\index.html
echo   OR use Python web server: python -m http.server 8000
echo ============================================================
echo.

cd /d "%PROJECT_ROOT%\app\api"
python app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Flask failed to start
    echo [INFO] Check the error messages above
    pause
)

pause
