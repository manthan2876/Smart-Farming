@echo off
echo ========================================================
echo Starting Server 2: Model Inference Server (Port 8001)
echo ========================================================
cd /d "%~dp0..\model_service"
"..\backend\.venv\Scripts\uvicorn.exe" main:app --host 127.0.0.1 --port 8001 --reload
pause
