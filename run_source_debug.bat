@echo off
cd /d "%~dp0"

echo ============================================
echo AudioCheckPC - SOURCE DEBUG
echo ============================================
echo.
echo Incoming TCP data will appear here.
echo.

python main.py

pause
