@echo off
echo ========================================================
echo Starting Mobile App (Flutter - Chrome Device)
echo ========================================================
cd /d "%~dp0..\mobile"
flutter run -d chrome %*
pause
