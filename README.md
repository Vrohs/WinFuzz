# WZF - Windows Fuzzy Finder

A lightning-fast file search tool for Windows 10/11, inspired by the popular `fzf` tool on Linux. Find files instantly across your system with fuzzy matching and a simple keyboard interface.

![WZF Demo](https://via.placeholder.com/800x400?text=WZF+Demo+Screenshot)

## What is WZF?

WZF (Windows Fuzzy Finder) is a command-line tool that helps you quickly find files on your Windows system. Key features:

- **Lightning Fast**: Optimized algorithms and multi-threading for speed
- **Fuzzy Search**: Find files even with partial or misspelled queries
- **Simple Interface**: Just type to search, use arrow keys to navigate
- **Zero Dependencies**: Standalone executable with no requirements
- **Full System Search**: Search specific folders or entire drives

## 🚀 Quick Install (One-Click)

WZF comes with a simple one-click installer that creates a standalone executable:

1. **Download** this repository ([Download ZIP](https://github.com/yourusername/wzf/archive/refs/heads/main.zip) or clone it)
2. **Extract** the ZIP file if you downloaded it
3. **Double-click** on the `build_and_install.bat` file
4. **Confirm** any security prompts that appear
   - If you see a Windows SmartScreen warning, click "More info" then "Run anyway"
   - When prompted for administrator privileges, click "Yes"
5. **Wait** for the installation to complete (you'll see a success message)
6. **Open** a new PowerShell window
7. **Type** `wzf` to start using the tool

> **Note**: This method creates a standalone executable with no dependencies - you don't need to install Python or any packages!

> **Prerequisite**: Python 3.6+ must be installed for the build step. If you don't have Python installed, see the [Python Installation Guide](#python-installation-guide) below.

## 🔄 Manual Installation

If you prefer to install manually, choose one of these options:

### Option 1: Build and Install the Executable

1. Make sure Python 3.6+ is installed (see [Python Installation Guide](#python-installation-guide) if needed)
2. Open a command prompt in the repository folder
3. Run the build script to create the executable:
   ```
   python build_exe.py
   ```
   - This will install PyInstaller and other required packages if they're not already installed
   - You should see "Build completed successfully!" when it's done
   - If you see any errors, check the [Troubleshooting](#troubleshooting) section
4. **Right-click** on PowerShell and select **"Run as administrator"**
5. Navigate to the repository folder
6. Run the installer:
   ```
   .\install_exe.ps1
   ```
   - You should see "WZF has been successfully installed!" when it's done

### Option 2: Traditional Python Installation

1. Make sure Python 3.6+ is installed (see [Python Installation Guide](#python-installation-guide) if needed)
2. Open a command prompt in the repository folder
3. Install the required packages:
   ```
   pip install colorama keyboard rapidfuzz pywin32 psutil
   ```
4. **Right-click** on PowerShell and select **"Run as administrator"**
5. Navigate to the repository folder
6. Run the standard installer:
   ```
   .\install.ps1
   ```
   - You should see "WZF has been successfully installed!" when it's done

## 🔍 How to Use

After installation, open a new PowerShell window and use the `wzf` command.

> **Important**: If the `wzf` command is not recognized, you may need to close and reopen your PowerShell window for the changes to take effect.

### Basic Usage:

```powershell
# Search across all drives (default behavior)
wzf

# Search only in current directory
wzf -l

# Search in a specific directory
wzf -p C:\Users\YourName\Documents

# Limit search depth (default is 10)
wzf -d 5

# Disable caching for fresh results
wzf -n

# Clear the cache before starting
wzf -c

# Set number of worker threads/processes
wzf -w 8
```

> **Note**: For best results when searching all drives, run PowerShell as administrator to ensure access to all directories.

## ⌨️ Keyboard Controls

| Key           | Action                        |
|---------------|-------------------------------|
| Type text     | Filter files as you type      |
| ↑ / ↓         | Navigate through results      |
| Page Up/Down  | Navigate pages of results     |
| Enter         | Open selected file            |
| Esc           | Exit WZF                      |
| Backspace     | Delete last character         |

### Search Tips

- Type part of a filename to find matching files
- Searches are case-insensitive
- You don't need to type the exact filename - fuzzy matching will find similar matches
- For better performance when searching large directories, use more specific search terms

## 🔧 Requirements

- Windows 10 or 11
- Python 3.6 or higher (for building the executable only, not needed to run it)
- Administrator privileges (for installation only)

## Python Installation Guide

If you don't have Python installed and need it to build the executable:

1. Download Python from the [official website](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check the box that says "Add Python to PATH" during installation
4. Complete the installation
5. Verify the installation by opening a command prompt and typing:
   ```
   python --version
   ```
   You should see the Python version number (e.g., "Python 3.9.5")

> **Note**: If you see "'python' is not recognized as an internal or external command", you may need to restart your computer or manually add Python to your PATH.

## ⚡ Performance Features

- **Smart Caching**: Indexes are cached for 24 hours for lightning-fast startup
- **Multi-threading**: Utilizes all available CPU cores for parallel scanning
- **Asynchronous Search**: Searches happen in the background for responsive UI
- **Optimized Algorithms**: Uses RapidFuzz for the fastest possible fuzzy matching
- **Intelligent Pre-filtering**: Dramatically reduces the search space before fuzzy matching
- **Progress Reporting**: Real-time updates during file indexing

## 🛠️ Manual Installation

If the automatic installer doesn't work for you:

1. Make sure Python 3.6+ is installed and in your PATH
2. Install required packages:
   ```
   pip install colorama keyboard rapidfuzz pywin32 psutil
   ```
3. Copy `wzf.py` to a directory in your PATH
4. Create a batch file or PowerShell alias to run it

## ❓ Troubleshooting

### Common Issues and Solutions

**Q: I installed WZF but the `wzf` command is not recognized.**
A: This happens because PowerShell needs to be restarted to recognize new commands.
   - Close all PowerShell windows
   - Open a new PowerShell window
   - Try the `wzf` command again
   - If it still doesn't work, check if the installation completed successfully

**Q: I get an error when running build_and_install.bat**
A: This could be due to several reasons:
   - **Python not installed**: Install Python 3.6+ and make sure it's in your PATH
   - **Permission issues**: Right-click and select "Run as administrator"
   - **Antivirus blocking**: Temporarily disable your antivirus or add an exception
   - **Specific error messages**: Check the error message for details on what went wrong

**Q: The search is slow when scanning all drives.**
A: Scanning all drives can take time, especially on systems with many files.
   - Try limiting the search depth: `wzf -d 5`
   - Search specific directories instead: `wzf -p C:\Users\YourName\Documents`
   - Use more specific search terms to filter results faster

**Q: I'm getting permission errors when searching.**
A: Some system directories require administrator privileges.
   - Run PowerShell as administrator when using WZF
   - Or exclude system directories by using specific paths

**Q: I'm having issues building the executable.**
A: Building the executable requires Python and proper permissions.
   - Make sure Python 3.6+ is installed and in your PATH
   - Run `python --version` to verify Python is installed correctly
   - Try installing PyInstaller manually: `pip install pyinstaller`
   - If you continue to have issues, try the traditional installation method using `install.ps1`

**Q: Windows SmartScreen is blocking the executable.**
A: This is a security feature of Windows for new/unknown executables.
   - Click "More info" on the warning dialog
   - Then click "Run anyway" to proceed
   - This only happens the first time you run the executable

**Q: The executable crashes or doesn't work properly.**
A: This could be due to missing dependencies or compatibility issues.
   - Try the traditional Python installation method instead
   - Check if your antivirus is blocking the executable
   - Run the executable from a command prompt to see any error messages

### Error Messages and Solutions

**Error: "Python is not recognized as an internal or external command"**
Solution: Python is not installed or not in your PATH. Install Python and make sure to check "Add Python to PATH" during installation.

**Error: "Permission denied" during installation**
Solution: You need administrator privileges. Right-click on PowerShell and select "Run as administrator".

**Error: "Failed to create process" when building the executable**
Solution: This could be due to antivirus blocking PyInstaller. Temporarily disable your antivirus or add an exception.

**Error: "Module not found" when building the executable**
Solution: A required Python package is missing. Run `pip install -r requirements.txt` to install all dependencies.

## 💾 Standalone Executable Benefits

- **Zero Dependencies**: No need to install Python or any packages
- **Simple Installation**: Just run the installer and you're done
- **Portable**: The executable can be copied to any Windows system
- **Fast Startup**: No Python interpreter overhead
- **Clean Installation**: Everything is contained in a single executable

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgements

- Inspired by [fzf](https://github.com/junegunn/fzf)
- Built with Python and love for Windows users
- Packaged as a standalone executable for hassle-free installation
