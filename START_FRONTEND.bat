@echo off
REM Start DocuSage Frontend
echo ========================================
echo Starting DocuSage Frontend
echo ========================================
echo.

cd frontend

echo Starting frontend development server...
echo Frontend will be available at: http://localhost:5173
echo.

start "DocuSage Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Frontend server started successfully!
echo ========================================
echo.
echo Press any key to return...
pause >nul
