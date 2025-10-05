@echo off
echo ============================================================
echo   DocuSage - Starting Backend Server
echo ============================================================
echo.
echo Backend will start at: http://localhost:8000
echo API Docs will be at: http://localhost:8000/docs
echo.
echo Features enabled:
echo   [OK] SQLite Database
echo   [OK] Cerebras AI Analysis (REAL ANALYSIS!)
echo   [OK] File Upload
echo   [OK] Document Processing
echo   [OK] Plain English Translation
echo   [OK] Doctor Question Generation
echo.
echo AI Model: Llama 3.1-8b (via Cerebras)
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd /d "%~dp0"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause
