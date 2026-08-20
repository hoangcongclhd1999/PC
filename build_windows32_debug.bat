@echo off
setlocal
cd /d "%~dp0"

echo Building DEBUG version with console...
echo.

python -c "import struct,sys; bits=struct.calcsize('P')*8; print('Architecture:',bits,'bit'); sys.exit(0 if bits==32 else 2)"
if errorlevel 2 (
    echo ERROR: Python must be 32-bit.
    pause
    exit /b 2
)

python -m pip install pyinstaller

if exist build_debug rmdir /s /q build_debug
if exist dist_debug rmdir /s /q dist_debug
if exist AudioCheckPC_Debug.spec del /q AudioCheckPC_Debug.spec

python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --onefile ^
    --console ^
    --name AudioCheckPC_Debug ^
    --workpath build_debug ^
    --distpath dist_debug ^
    main.py

echo.
echo Run this to see RX logs:
echo dist_debug\AudioCheckPC_Debug.exe
pause
