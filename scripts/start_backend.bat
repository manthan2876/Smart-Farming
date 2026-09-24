@echo off
echo ========================================================
echo Starting Server 1: Main Backend API (Port 8000)
echo ========================================================
cd /d "%~dp0..\backend"
".venv\Scripts\uvicorn.exe" src.app.main:app --host 127.0.0.1 --port 8000 --reload
pause
