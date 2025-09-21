@echo off
echo Starting Attendance Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found! Checking dependencies...

REM Try to run the simple version first
echo.
echo Attempting to start Simple Attendance Management System...
python app_simple.py

REM If that fails, try to install requirements
if errorlevel 1 (
    echo.
    echo Failed to start. Trying to install requirements...
    pip install opencv-python numpy pandas matplotlib openpyxl pillow
    echo.
    echo Retrying...
    python app_simple.py
)

pause