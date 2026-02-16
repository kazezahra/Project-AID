@echo off
REM Open Frontend in Default Browser
REM This script serves the frontend and opens it in your browser

setlocal
cd /d "%~dp0"
set PROJECT_ROOT=%cd%
set FRONTEND_PATH=%PROJECT_ROOT%\frontend\AID-FYP
set FRONTEND_FILE=%FRONTEND_PATH%\index.html

if not exist "%FRONTEND_FILE%" (
    echo [ERROR] Frontend file not found: %FRONTEND_FILE%
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   AUTISM PRE-SCREENING TOOL - Frontend Server
echo ============================================================
echo.
echo [INFO] Frontend path: %FRONTEND_PATH%
echo [INFO] Starting web server on http://localhost:8000
echo [INFO] Frontend URL: http://localhost:8000/index.html
echo.
echo [IMPORTANT] Make sure Flask backend is running!
echo [IMPORTANT] Starting at http://localhost:5000
echo.
echo [INFO] Press Ctrl+C to stop the server
echo.

cd /d "%FRONTEND_PATH%"
python -m http.server 8000

pause
