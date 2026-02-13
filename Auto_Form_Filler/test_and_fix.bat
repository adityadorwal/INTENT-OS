@echo off
echo ========================================
echo Auto Form Filler - Test and Fix
echo ========================================
echo.

echo Step 1: Testing Chrome connection...
echo.
python test_connection.py

echo.
echo ========================================
echo If the test passed, you can now use the form filler!
echo If it failed, follow the troubleshooting steps shown above.
echo ========================================
echo.
pause
