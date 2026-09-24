@echo off
setlocal
title Smart Farming - All Services
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_all.ps1" %*
if %ERRORLEVEL% neq 0 pause