@echo off
title Intent OS - One-Click Setup
color 0B
cls

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                                                          ║
echo  ║          🎤 INTENT OS - ONE-CLICK SETUP                 ║
echo  ║                                                          ║
echo  ║     No CMD needed! Everything in GUI!                   ║
echo  ║                                                          ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  Starting GUI Setup Wizard...
echo  Please wait...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo  ❌ Python not found!
    echo.
    echo  Please install Python 3.8+ from:
    echo  https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit
)

REM Start GUI setup (no console window)
start "Intent OS Setup" pythonw gui_setup.py

REM Wait a moment
timeout /t 2 >nul

echo  ✅ Setup wizard opened!
echo.
echo  Follow the steps in the GUI window.
echo  This window will close automatically.
echo.
timeout /t 3 >nul

exit
