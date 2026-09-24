@echo off
echo ========================================================
echo Starting Frontend (Vite React UI on Port 5173)
echo ========================================================
cd /d "%~dp0..\frontend"
npm run dev
pause
