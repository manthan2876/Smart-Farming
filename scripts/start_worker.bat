@echo off
echo ========================================================
echo Starting ARQ Background Worker (Redis Job Queue)
echo ========================================================
cd /d "%~dp0..\backend"
set PYTHONIOENCODING=utf-8
".venv\Scripts\arq.exe" src.app.worker.WorkerSettings
pause
