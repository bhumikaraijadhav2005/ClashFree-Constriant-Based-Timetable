@echo off
setlocal

:: Ensure Python is in PATH for this session
set "PATH=C:\Users\Admin\AppData\Local\Programs\Python\Python311;C:\Users\Admin\AppData\Local\Programs\Python\Python311\Scripts;%PATH%"

echo ========================================================
echo Starting ClashFree Timetable System...
echo ========================================================

start "ClashFree Backend (Flask)" cmd /k "set PATH=C:\Users\Admin\AppData\Local\Programs\Python\Python311;C:\Users\Admin\AppData\Local\Programs\Python\Python311\Scripts;%%PATH%% && python backend/app.py"
start "ClashFree Frontend (React Vite)" cmd /k "cd frontend && npm run dev"

timeout /t 3 >nul
start http://localhost:5173

echo.
echo ClashFree is running!
echo Backend:  http://127.0.0.1:5000
echo Frontend: http://localhost:5173
echo.
