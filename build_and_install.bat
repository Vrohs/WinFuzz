@echo off
setlocal enabledelayedexpansion
color 0B

echo ============================================================
echo    WZF - Windows Fuzzy Finder - Build and Install
echo ============================================================
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ERROR: Python is not installed or not in your PATH.
    echo.
    echo Please install Python 3.6 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo After installing Python, run this script again.
    echo.
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%V in ('python -c "import sys; print(sys.version_info[0])"') do set PYTHON_VERSION=%%V
if %PYTHON_VERSION% LSS 3 (
    color 0C
    echo ERROR: Python 3.6+ is required, but you have Python %PYTHON_VERSION% installed.
    echo.
    echo Please install Python 3.6 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Step 1: Building the executable...
echo ------------------------------------------------------------
echo This may take a few minutes. Please be patient.
echo.

python build_exe.py
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo ERROR: Failed to build the executable.
    echo.
    echo Possible reasons:
    echo  - Missing Python packages
    echo  - Insufficient permissions
    echo  - Antivirus blocking PyInstaller
    echo.
    echo Please check the error messages above for more details.
    echo You can also try the manual installation method described in the README.
    echo.
    pause
    exit /b 1
)

echo.
echo Step 2: Installing WZF...
echo ------------------------------------------------------------
echo This step requires administrator privileges.
echo You will see a UAC prompt - please click "Yes" to continue.
echo.

powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0install_exe.ps1\"' -Verb RunAs"
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo ERROR: Failed to start the installation process.
    echo.
    echo Please try running the install_exe.ps1 script manually as administrator:
    echo  1. Right-click on PowerShell and select "Run as administrator"
    echo  2. Navigate to this directory
    echo  3. Run: .\install_exe.ps1
    echo.
    pause
    exit /b 1
)

color 0A
echo.
echo ------------------------------------------------------------
echo Build and install process initiated.
echo.
echo If you see a success message in the administrator PowerShell window,
echo WZF has been successfully installed!
echo.
echo You can now open a new PowerShell window and type 'wzf' to start using it.
echo.
echo If you encounter any issues, please refer to the Troubleshooting
echo section in the README.md file.
echo ------------------------------------------------------------
echo.
pause
