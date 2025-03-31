# WZF - Windows Fuzzy Finder Installer
# This script installs WZF and sets up the 'wzf' command

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges to install properly." -ForegroundColor Yellow
    Write-Host "Please run PowerShell as administrator and try again." -ForegroundColor Yellow
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Define installation directory
$installDir = "$env:ProgramFiles\WZF"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Create installation directory if it doesn't exist
if (-not (Test-Path -Path $installDir)) {
    Write-Host "Creating installation directory: $installDir" -ForegroundColor Cyan
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.6 or higher from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# Install required Python packages
Write-Host "Installing required Python packages..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install colorama keyboard fuzzywuzzy python-Levenshtein

# Copy the main script to the installation directory
Write-Host "Copying files to installation directory..." -ForegroundColor Cyan
Copy-Item -Path "$scriptDir\wzf.py" -Destination "$installDir\wzf.py" -Force

# Create a batch file to run the Python script
$batchContent = "@echo off`r`npython `"$installDir\wzf.py`" %*"
Set-Content -Path "$installDir\wzf.bat" -Value $batchContent

# Add the installation directory to the system PATH if it's not already there
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (-not $currentPath.Contains($installDir)) {
    Write-Host "Adding installation directory to system PATH..." -ForegroundColor Cyan
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$installDir", "Machine")
}

# Create a PowerShell profile directory if it doesn't exist
$profileDir = Split-Path -Parent $PROFILE
if (-not (Test-Path -Path $profileDir)) {
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
}

# Add an alias to the PowerShell profile
$aliasLine = "function wzf { & '$installDir\wzf.bat' @args }"
$profileContent = ""
if (Test-Path -Path $PROFILE) {
    $profileContent = Get-Content -Path $PROFILE -Raw
}

if (-not $profileContent.Contains("function wzf")) {
    Write-Host "Adding 'wzf' alias to PowerShell profile..." -ForegroundColor Cyan
    Add-Content -Path $PROFILE -Value "`n# WZF - Windows Fuzzy Finder"
    Add-Content -Path $PROFILE -Value $aliasLine
}

Write-Host "`nWZF has been successfully installed!" -ForegroundColor Green
Write-Host "You can now use the 'wzf' command in a new PowerShell window." -ForegroundColor Green
Write-Host "Usage examples:" -ForegroundColor Cyan
Write-Host "  wzf                  - Search in current directory" -ForegroundColor White
Write-Host "  wzf -p C:\Users      - Search in specific directory" -ForegroundColor White
Write-Host "  wzf -a               - Search all drives (admin only)" -ForegroundColor White
Write-Host "`nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
