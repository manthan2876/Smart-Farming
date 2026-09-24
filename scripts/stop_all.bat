@echo off
echo ========================================================
echo Stopping All Smart Farming Services...
echo ========================================================

echo Stopping Uvicorn / ARQ / Python workers...
taskkill /f /im uvicorn.exe 2>nul
taskkill /f /im arq.exe 2>nul

echo Stopping Vite / Node processes...
taskkill /f /im node.exe 2>nul

echo Stopping Flutter / Dart processes...
taskkill /f /im dart.exe 2>nul

echo.
echo ========================================================
echo All services stopped cleanly.
echo ========================================================
pause
