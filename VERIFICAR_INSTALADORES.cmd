@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\verify-installers.ps1"
set "DLPS_RESULT=%ERRORLEVEL%"
pause
exit /b %DLPS_RESULT%
