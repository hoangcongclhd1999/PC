@echo off
setlocal
cd /d "%~dp0"

echo ============================================
echo   AudioCheckPC - Windows 32-bit BUILD
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found.
    echo Install a 32-bit Python first.
    pause
    exit /b 1
)

echo Checking Python architecture...
python -c "import struct,sys; bits=struct.calcsize('P')*8; print('Python:',sys.version); print('Architecture:',bits,'bit'); sys.exit(0 if bits==32 else 2)"
if errorlevel 2 (
    echo.
    echo ERROR: This Python is NOT 32-bit.
    echo Install Windows x86 / 32-bit Python and run this file again.
    pause
    exit /b 2
)

echo.
echo Checking Tkinter...
python -c "import tkinter; print('Tkinter OK - Tk', tkinter.TkVersion)"
if errorlevel 1 (
    echo ERROR: Tkinter is missing from this Python installation.
    pause
    exit /b 3
)

echo.
echo Installing/updating PyInstaller...
python -m pip install --upgrade pip
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: PyInstaller installation failed.
    pause
    exit /b 4
)

echo.
echo Removing old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist AudioCheckPC.spec del /q AudioCheckPC.spec

echo.
echo Building 32-bit EXE...
python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name AudioCheckPC ^
    main.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED.
    pause
    exit /b 5
)

echo.
echo ============================================
echo BUILD DONE
echo ============================================
echo.
echo EXE:
echo %CD%\dist\AudioCheckPC.exe
echo.
start "" "%CD%\dist"
pause
