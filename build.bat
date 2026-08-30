@echo off
echo ========================================
echo   STORM CALCULATOR - Build Script
echo ========================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
)

echo [*] Building STORM CALCULATOR...
echo.

pyinstaller --onefile --windowed --icon=stormcalculator.ico --name="STORM CALCULATOR" --add-data "stormcalculator.ico;." --clean stormcalculator.py

echo.
if exist "dist\STORM CALCULATOR.exe" (
    echo [+] Build successful!
    echo [+] Output: dist\STORM CALCULATOR.exe
    echo.
    echo [*] Copying to current directory...
    copy "dist\STORM CALCULATOR.exe" "STORM CALCULATOR.exe" >nul
    echo [+] Done! STORM CALCULATOR.exe is ready.
) else (
    echo [-] Build failed. Check errors above.
)

echo.
pause
