@echo off
echo ============================================================
echo   DocuSage - Starting Frontend Server
echo ============================================================
echo.
echo Frontend will start at: http://localhost:5174
echo.
echo Features:
echo   [OK] Dashboard with file upload
echo   [OK] Landing page with animations
echo   [OK] Connected to backend API
echo.
echo First time? Running 'npm install' first...
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0"
call npm install
call npm run dev

pause
