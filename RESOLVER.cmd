@echo off
setlocal
chcp 65001 >nul
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0windows\resolve.ps1" %*
set "DLPS_RESULT=%ERRORLEVEL%"
if "%~1"=="" pause
exit /b %DLPS_RESULT%
