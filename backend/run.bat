@echo off
echo ============================================================
echo     DocuSage Backend API Server
echo ============================================================
echo.
echo Configuration:
echo   - API endpoint: http://localhost:8000
echo   - API docs: http://localhost:8000/docs
echo   - Database: Not configured (DB features disabled)
echo   - Cerebras API: Not configured (LLM features disabled)
echo.
echo Note: To enable database, start PostgreSQL with:
echo   docker-compose up -d db
echo.
echo Starting server...
echo.
cd /d "%~dp0"
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
