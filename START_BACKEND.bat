@echo off
REM Start DocuSage Backend Server
echo ========================================
echo Starting DocuSage Backend Server
echo ========================================
echo.

cd backend

echo Checking if backend is already running...
curl http://localhost:8000 >nul 2>&1
if %errorlevel%==0 (
    echo Backend is already running at http://localhost:8000
    echo.
    pause
    exit /b 0
)

echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API docs available at: http://localhost:8000/docs
echo.

start "DocuSage Backend" cmd /k "python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo ========================================
echo Backend server started successfully!
echo ========================================
echo.
echo Press any key to return...
pause >nul
