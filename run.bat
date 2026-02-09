@echo off
echo ========================================
echo Voice Command AI - Quick Launcher
echo ========================================
echo.

python run.py

if errorlevel 1 (
    echo.
    echo Press any key to exit...
    pause >nul
)