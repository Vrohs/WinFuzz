# WZF - Windows Fuzzy Finder Installer (Executable Version)
# This script installs the WZF executable and sets up the 'wzf' command

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "    WZF - Windows Fuzzy Finder - Installation" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script requires administrator privileges to install properly." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run PowerShell as administrator:" -ForegroundColor Yellow
    Write-Host "  1. Right-click on PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host "  2. Navigate to the directory containing this script" -ForegroundColor Yellow
    Write-Host "  3. Run: .\install_exe.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Define installation directory
$installDir = "$env:ProgramFiles\WZF"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check if the executable exists
if (-not (Test-Path -Path "$scriptDir\wzf.exe")) {
    Write-Host "ERROR: The WZF executable (wzf.exe) was not found in the current directory." -ForegroundColor Red
    Write-Host ""
    Write-Host "You need to build the executable first:" -ForegroundColor Yellow
    Write-Host "  1. Make sure Python 3.6+ is installed" -ForegroundColor Yellow
    Write-Host "  2. Run the build script: python build_exe.py" -ForegroundColor Yellow
    Write-Host "  3. Then run this installer again" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternatively, you can use the build_and_install.bat file which handles both steps." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "Step 1: Setting up installation directory..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

# Create installation directory if it doesn't exist
if (-not (Test-Path -Path $installDir)) {
    Write-Host "Creating installation directory: $installDir" -ForegroundColor White
    try {
        New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    } catch {
        Write-Host "ERROR: Failed to create installation directory." -ForegroundColor Red
        Write-Host "Reason: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please make sure you have administrator privileges." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
}

# Copy the executable to the installation directory
Write-Host "Copying WZF executable to installation directory..." -ForegroundColor White
try {
    Copy-Item -Path "$scriptDir\wzf.exe" -Destination "$installDir\wzf.exe" -Force
} catch {
    Write-Host "ERROR: Failed to copy the executable to the installation directory." -ForegroundColor Red
    Write-Host "Reason: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please make sure you have administrator privileges and the file is not in use." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "Step 2: Updating system PATH..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

# Add the installation directory to the system PATH if it's not already there
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (-not $currentPath.Contains($installDir)) {
    Write-Host "Adding installation directory to system PATH..." -ForegroundColor White
    try {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir", "Machine")
    } catch {
        Write-Host "ERROR: Failed to update the system PATH." -ForegroundColor Red
        Write-Host "Reason: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please make sure you have administrator privileges." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to exit..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
} else {
    Write-Host "Installation directory is already in the system PATH." -ForegroundColor White
}

Write-Host ""
Write-Host "Step 3: Setting up PowerShell alias..." -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

# Create a PowerShell profile directory if it doesn't exist
$profileDir = Split-Path -Parent $PROFILE
if (-not (Test-Path -Path $profileDir)) {
    Write-Host "Creating PowerShell profile directory..." -ForegroundColor White
    try {
        New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    } catch {
        Write-Host "ERROR: Failed to create PowerShell profile directory." -ForegroundColor Red
        Write-Host "Reason: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "The 'wzf' command may not work properly." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to continue anyway..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
}

# Add an alias to the PowerShell profile
$aliasLine = "function wzf { & '$installDir\wzf.exe' @args }"
$profileContent = ""
if (Test-Path -Path $PROFILE) {
    try {
        $profileContent = Get-Content -Path $PROFILE -Raw -ErrorAction SilentlyContinue
    } catch {
        $profileContent = ""
    }
}

if (-not $profileContent -or -not $profileContent.Contains("function wzf")) {
    Write-Host "Adding 'wzf' alias to PowerShell profile..." -ForegroundColor White
    try {
        Add-Content -Path $PROFILE -Value "`n# WZF - Windows Fuzzy Finder"
        Add-Content -Path $PROFILE -Value $aliasLine
    } catch {
        Write-Host "ERROR: Failed to update PowerShell profile." -ForegroundColor Red
        Write-Host "Reason: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "You can still use WZF by running the full path: $installDir\wzf.exe" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Press any key to continue anyway..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
} else {
    Write-Host "The 'wzf' alias is already in your PowerShell profile." -ForegroundColor White
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "    WZF has been successfully installed!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now use the 'wzf' command in a new PowerShell window." -ForegroundColor White
Write-Host "(You must open a new PowerShell window for the changes to take effect)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Usage examples:" -ForegroundColor Cyan
Write-Host "  wzf                  - Search in current directory" -ForegroundColor White
Write-Host "  wzf -p C:\Users      - Search in specific directory" -ForegroundColor White
Write-Host "  wzf -a               - Search all drives (admin only)" -ForegroundColor White
Write-Host "  wzf -n               - Disable caching for fresh results" -ForegroundColor White
Write-Host "  wzf -c               - Clear the cache before starting" -ForegroundColor White
Write-Host "  wzf -w 8             - Set number of worker threads" -ForegroundColor White
Write-Host ""
Write-Host "If you encounter any issues, please refer to the Troubleshooting" -ForegroundColor White
Write-Host "section in the README.md file." -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
