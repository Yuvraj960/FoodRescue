@echo off
echo ===================================================
echo   FoodRescue Platform - Local Development Launcher
echo ===================================================
echo.

:: Ensure python virtual environment is used
set PYTHON_EXE=backend\venv\Scripts\python.exe

if not exist %PYTHON_EXE% (
    echo [INFO] Creating Python virtual environment...
    python -m venv backend\venv
    backend\venv\Scripts\pip install -r backend\requirements.txt
)

:: Seed database if not yet created
if not exist backend\foodrescue.db (
    echo [INFO] Initializing database and seeding realistic demo records...
    %PYTHON_EXE% backend\seed_data.py
)

echo [INFO] Starting Flask backend on http://localhost:5000...
start "FoodRescue Backend" cmd /k "%PYTHON_EXE% backend\run.py"

echo [INFO] Starting Vue 3 Frontend on http://localhost:5173...
cd frontend
start "FoodRescue Frontend" cmd /k "npm run dev"
cd ..

echo.
echo [SUCCESS] FoodRescue platform running!
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
pause
