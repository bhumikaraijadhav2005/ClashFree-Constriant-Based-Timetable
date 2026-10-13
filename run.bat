@echo off
setlocal

:: If run from parent directory, enter project folder
if exist "ClashFree-Constriant-Based-Timetable" (
    cd "ClashFree-Constriant-Based-Timetable"
)

echo ========================================================
echo Starting ClashFree Timetable System...
echo ========================================================

:: Check Python availability
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found in system PATH. Attempting user AppData...
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
)

:: Start Flask Backend Server in a new terminal window
echo Starting Flask Backend Server on port 5000...
start "ClashFree Backend (Flask)" cmd /k "python backend/app.py"

:: Start React Vite Frontend Server in a new terminal window
echo Starting React Vite Frontend Server on port 5173...
start "ClashFree Frontend (React Vite)" cmd /k "cd frontend && npm run dev"

timeout /t 3 >nul
start http://localhost:5173

echo.
echo ========================================================
echo ClashFree is running!
echo Backend API:  http://127.0.0.1:5000
echo Frontend UI:  http://localhost:5173
echo ========================================================
echo.
