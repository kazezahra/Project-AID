@echo off
REM Autism Pre-Screening Tool - Quick Start Script for Windows

echo.
echo ========================================
echo ^| Autism Pre-Screening Tool - Quick Start
echo ^| Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)
echo [OK] Python found

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed
    exit /b 1
)
echo [OK] pip found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
pip install -q -r app\api\requirements.txt
echo [OK] Dependencies installed

REM Check for .env file
if not exist ".env" (
    echo Creating .env file...
    (
        echo FLASK_ENV=development
        echo FLASK_DEBUG=1
        echo GROQ_API_KEY=your_api_key_here
    ) > .env
    echo [OK] .env file created - please update GROQ_API_KEY
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application:
echo.
echo 1. Update .env file with your API keys
echo.
echo 2. In one terminal, run the backend:
echo    python -m flask --app app.api.app run --host 0.0.0.0 --port 5000
echo.
echo 3. In another terminal, serve the frontend:
echo    cd frontend\AID-FYP
echo    python -m http.server 8000
echo.
echo 4. Open http://localhost:8000 in your browser
echo.
echo Or use Docker:
echo    docker-compose up
echo.
pause
