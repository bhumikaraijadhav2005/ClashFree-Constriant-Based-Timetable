@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
)

python run.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to start with python. Press any key to see error details...
    pause
)
