@echo off
echo Starting Scholarship Discovery System...

:: Ensure we are in the correct directory
cd /d "%~dp0"

:: Check if virtual environment exists
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo [!] Virtual environment not found. Please install requirements first.
    pause
    exit /b
)

:: Start the FastAPI Web Server in a new window
echo [*] Launching FastAPI Web Server...
start "Scholarship API Server" cmd /k ".\venv\Scripts\activate.bat && uvicorn src.api:app --host 127.0.0.1 --port 8000"

:: Wait a brief moment for the server to spin up
timeout /t 3 /nobreak >nul

:: Start the Scheduler Automation Background Job in a new window
echo [*] Launching Background Automation Scheduler...
start "Scholarship Background Crawler (Automation)" cmd /k ".\venv\Scripts\activate.bat && python scheduler.py"

echo.
echo [+] All systems running!
echo [+] You can access the Web Dashboard at: http://127.0.0.1:8000
echo [+] You can access the API Docs at: http://127.0.0.1:8000/docs
echo.
pause
