# WZF - Windows Fuzzy Finder

A lightning-fast file search tool for Windows 10/11, inspired by the popular `fzf` tool on Linux. Optimized for maximum performance with advanced caching and multi-threading.

![WZF Demo](https://via.placeholder.com/800x400?text=WZF+Demo+Screenshot)

## 🚀 Quick Install

1. **Right-click** on PowerShell and select **"Run as administrator"**
2. Navigate to the folder where you downloaded/cloned this repository
3. Run the installer:
   ```
   .\install.ps1
   ```
4. That's it! You can now use the `wzf` command in any new PowerShell window.

## 🔍 How to Use

After installation, open a new PowerShell window and use the `wzf` command:

```powershell
# Search in current directory
wzf

# Search in a specific directory
wzf -p C:\Users\YourName\Documents

# Search across all drives (requires admin privileges)
wzf -a

# Limit search depth (default is 10)
wzf -d 5

# Disable caching for fresh results
wzf -n

# Clear the cache before starting
wzf -c

# Set number of worker threads/processes
wzf -w 8
```

## ⌨️ Keyboard Controls

| Key           | Action                        |
|---------------|-------------------------------|
| Type text     | Filter files as you type      |
| ↑ / ↓         | Navigate through results      |
| Page Up/Down  | Navigate pages of results     |
| Enter         | Open selected file            |
| Esc           | Exit WZF                      |

## 🔧 Requirements

- Windows 10 or 11
- Python 3.6 or higher (will be checked during installation)
- Administrator privileges (for installation only)

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

**Q: I installed WZF but the `wzf` command is not recognized.**
A: Open a new PowerShell window. The changes to your profile only apply to new sessions.

**Q: The search is slow when scanning all drives.**
A: Scanning all drives can take time. Try limiting the search depth with `-d` or search specific directories instead.

**Q: I'm getting permission errors when searching.**
A: Some system directories require administrator privileges. Run PowerShell as administrator or exclude those directories.

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgements

- Inspired by [fzf](https://github.com/junegunn/fzf)
- Built with Python and love for Windows users
