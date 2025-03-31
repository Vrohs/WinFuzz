#!/usr/bin/env python3
"""
Build script for WZF - Windows Fuzzy Finder
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
import platform
import time

# ANSI colors for Windows
if platform.system() == "Windows":
    try:
        import colorama
        colorama.init()
        GREEN = colorama.Fore.GREEN
        RED = colorama.Fore.RED
        YELLOW = colorama.Fore.YELLOW
        CYAN = colorama.Fore.CYAN
        RESET = colorama.Style.RESET_ALL
    except ImportError:
        GREEN = ""
        RED = ""
        YELLOW = ""
        CYAN = ""
        RESET = ""
else:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def print_header():
    """Print a nice header for the build script"""
    print(f"{CYAN}============================================================{RESET}")
    print(f"{CYAN}    WZF - Windows Fuzzy Finder - Build Script{RESET}")
    print(f"{CYAN}============================================================{RESET}")
    print()

def check_requirements():
    """Check if required packages are installed"""
    print(f"{CYAN}Step 1: Checking and installing required packages...{RESET}")
    print(f"{CYAN}------------------------------------------------------------{RESET}")

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print(f"{RED}ERROR: Python 3.6 or higher is required.{RESET}")
        print(f"{YELLOW}You are using Python {python_version.major}.{python_version.minor}.{python_version.micro}{RESET}")
        print("\nPlease install a newer version of Python and try again.")
        sys.exit(1)
    else:
        print(f"Using Python {python_version.major}.{python_version.minor}.{python_version.micro} - {GREEN}OK{RESET}")

    # Check for PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller {PyInstaller.__version__} is already installed - {GREEN}OK{RESET}")
    except ImportError:
        print(f"{YELLOW}PyInstaller is not installed. Installing now...{RESET}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print(f"PyInstaller installed successfully - {GREEN}OK{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{RED}ERROR: Failed to install PyInstaller.{RESET}")
            print(f"{RED}Error details: {e}{RESET}")
            print(f"\n{YELLOW}Please try installing it manually:{RESET}")
            print("pip install pyinstaller")
            sys.exit(1)

    # Check for other required packages
    required_packages = ["colorama", "keyboard", "rapidfuzz", "pywin32", "psutil"]
    for package in required_packages:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            print(f"{package} {version} is already installed - {GREEN}OK{RESET}")
        except ImportError:
            print(f"{YELLOW}{package} is not installed. Installing now...{RESET}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"{package} installed successfully - {GREEN}OK{RESET}")
            except subprocess.CalledProcessError as e:
                print(f"{RED}ERROR: Failed to install {package}.{RESET}")
                print(f"{RED}Error details: {e}{RESET}")
                print(f"\n{YELLOW}Please try installing it manually:{RESET}")
                print(f"pip install {package}")
                sys.exit(1)

    print(f"\nAll required packages are installed - {GREEN}OK{RESET}")

def build_executable():
    """Build the standalone executable"""
    print(f"\n{CYAN}Step 2: Building WZF executable...{RESET}")
    print(f"{CYAN}------------------------------------------------------------{RESET}")
    print("This may take a few minutes. Please be patient.\n")

    # Check if wzf.py exists
    if not os.path.exists("wzf.py"):
        print(f"{RED}ERROR: wzf.py not found in the current directory.{RESET}")
        print(f"{YELLOW}Make sure you are running this script from the repository root directory.{RESET}")
        sys.exit(1)

    # Create spec file with icon and other options
    print("Creating PyInstaller specification file...")
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['wzf.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['win32api', 'win32con'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='wzf',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
    """

    try:
        with open("wzf.spec", "w") as f:
            f.write(spec_content)
        print(f"Specification file created - {GREEN}OK{RESET}")
    except Exception as e:
        print(f"{RED}ERROR: Failed to create specification file.{RESET}")
        print(f"{RED}Error details: {e}{RESET}")
        sys.exit(1)

    # Build the executable
    print("\nBuilding executable with PyInstaller...")
    print("(This may take several minutes)")
    start_time = time.time()

    try:
        # Redirect output to a file to avoid cluttering the console
        with open("build_log.txt", "w") as log_file:
            subprocess.check_call(
                [sys.executable, "-m", "PyInstaller", "wzf.spec", "--clean"],
                stdout=log_file,
                stderr=subprocess.STDOUT
            )
        elapsed = time.time() - start_time
        print(f"Build process completed in {elapsed:.1f} seconds - {GREEN}OK{RESET}")
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"{RED}ERROR: Failed to build the executable after {elapsed:.1f} seconds.{RESET}")
        print(f"{RED}Error details: {e}{RESET}")
        print(f"\n{YELLOW}Check build_log.txt for detailed error information.{RESET}")
        print(f"\n{YELLOW}Common issues:{RESET}")
        print(f"{YELLOW}1. Antivirus blocking PyInstaller{RESET}")
        print(f"{YELLOW}2. Insufficient permissions{RESET}")
        print(f"{YELLOW}3. Missing dependencies{RESET}")
        sys.exit(1)

    # Copy the executable to the current directory
    print("\nCopying executable to current directory...")
    if os.path.exists("dist/wzf.exe"):
        try:
            shutil.copy("dist/wzf.exe", "wzf.exe")
            print(f"Executable copied to current directory: wzf.exe - {GREEN}OK{RESET}")
        except Exception as e:
            print(f"{RED}ERROR: Failed to copy the executable.{RESET}")
            print(f"{RED}Error details: {e}{RESET}")
            print(f"{YELLOW}The executable is still available at dist/wzf.exe{RESET}")
            sys.exit(1)
    else:
        print(f"{RED}ERROR: Executable not found in dist directory.{RESET}")
        print(f"{YELLOW}Check build_log.txt for detailed error information.{RESET}")
        sys.exit(1)

    # Check if the executable is valid
    print("\nVerifying executable...")
    try:
        # Just check if the file exists and has a reasonable size
        size = os.path.getsize("wzf.exe") / (1024 * 1024)  # Size in MB
        if size < 1:
            print(f"{YELLOW}WARNING: Executable size is suspiciously small ({size:.2f} MB).{RESET}")
            print(f"{YELLOW}The build may not have completed correctly.{RESET}")
        else:
            print(f"Executable size: {size:.2f} MB - {GREEN}OK{RESET}")
    except Exception as e:
        print(f"{RED}ERROR: Failed to verify the executable.{RESET}")
        print(f"{RED}Error details: {e}{RESET}")

    print(f"\n{GREEN}Build completed successfully!{RESET}")

def main():
    """Main function"""
    print_header()

    # Check if running on Windows
    if platform.system() != "Windows":
        print(f"{RED}ERROR: This build script is designed for Windows only.{RESET}")
        print(f"{YELLOW}You are running on {platform.system()}.{RESET}")
        sys.exit(1)

    try:
        # Check for required packages
        check_requirements()

        # Build the executable
        build_executable()

        print(f"\n{CYAN}============================================================{RESET}")
        print(f"{GREEN}Build process completed successfully!{RESET}")
        print(f"{CYAN}============================================================{RESET}")
        print("\nNext steps:")
        print(f"{CYAN}1. Run the installation script:{RESET} .\install_exe.ps1")
        print(f"{CYAN}2. Open a new PowerShell window and type:{RESET} wzf")
        print("\nIf you encounter any issues, please refer to the Troubleshooting")
        print("section in the README.md file.")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Build process cancelled by user.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}ERROR: An unexpected error occurred.{RESET}")
        print(f"{RED}Error details: {e}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()
