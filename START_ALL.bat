@echo off
REM Start Complete DocuSage Application
echo ========================================
echo Starting Complete DocuSage Application
echo ========================================
echo.

echo This will start:
echo   1. Backend API Server (Port 8000)
echo   2. Frontend Dev Server (Port 5173)
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

echo.
echo [1/2] Starting Backend Server...
cd backend
start "DocuSage Backend" cmd /k "python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 3 >nul

echo [2/2] Starting Frontend Server...
cd ..\frontend
start "DocuSage Frontend" cmd /k "npm run dev"

timeout /t 2 >nul

echo.
echo ========================================
echo Both servers started successfully!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
echo Open your browser and navigate to:
echo http://localhost:5173
echo.
echo Press any key to exit this window...
echo (The servers will keep running in separate windows)
pause >nul
