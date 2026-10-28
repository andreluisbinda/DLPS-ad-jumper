@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\prepare.ps1" %*
set "DLPS_RESULT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %DLPS_RESULT%
