#!/bin/bash

echo "Starting Attendance Management System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed"
        echo "Please install Python from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python found! Checking dependencies..."

# Try to run the simple version first
echo
echo "Attempting to start Simple Attendance Management System..."
$PYTHON_CMD app_simple.py

# If that fails, try to install requirements
if [ $? -ne 0 ]; then
    echo
    echo "Failed to start. Trying to install requirements..."
    pip install opencv-python numpy pandas matplotlib openpyxl pillow
    echo
    echo "Retrying..."
    $PYTHON_CMD app_simple.py
fi