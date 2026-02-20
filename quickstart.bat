@echo off
echo ==========================================
echo Tennis Academy - Quick Start Script
echo ==========================================
echo.

REM Check if Python is installed
set PYTHON_CMD=python
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Python is not installed. Please install Python 3 first.
        exit /b 1
    )
)

echo Step 1: Creating virtual environment...
%PYTHON_CMD% -m venv venv

echo Step 2: Activating virtual environment...
call venv\Scripts\activate

echo Step 3: Installing dependencies...
pip install -r requirements.txt

echo Step 4: Initializing database...
python -c "from app import init_db; init_db(); print('Database initialized!')"

echo.
echo Step 5: Would you like to add demo data? (y/n)
set /p response=""
if /i "%response%"=="y" (
    python demo_data.py
)

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To start the application:
echo   1. Set your email credentials:
echo      set SENDER_EMAIL=your-email@gmail.com
echo      set SENDER_PASSWORD=your-app-password
echo.
echo   2. Run the app:
echo      python app.py
echo.
echo   3. Open browser and go to:
echo      http://localhost:5000
echo.
echo   4. First time setup:
echo      Visit http://localhost:5000/setup to create admin account
echo.
echo ==========================================
pause
