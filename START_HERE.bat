@echo off
title Intent OS - Smart Launcher
color 0A
cls
echo.
echo  ╔════════════════════════════════════════╗
echo  ║    Intent OS - Smart Launcher          ║
echo  ╚════════════════════════════════════════╝
echo.

REM Check if setup is complete
if not exist ".setup_complete" (
    echo  First time setup required...
    echo  Opening GUI Setup Wizard...
    echo.
    python gui_setup.py
    goto end
)

echo  Starting Intent OS...
echo.
python run.py

:end
if errorlevel 1 (
    echo.
    echo  ❌ Failed to start
    echo.
    pause
)

exit