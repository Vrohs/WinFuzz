#!/usr/bin/env python3
"""
WZF - Windows Fuzzy Finder
A simple and fast fuzzy finder for Windows, inspired by fzf.
"""

import os
import sys
import argparse
import re
import subprocess
from pathlib import Path
import ctypes
from concurrent.futures import ThreadPoolExecutor
import time

try:
    import colorama
    from colorama import Fore, Style
    import keyboard
    from fuzzywuzzy import fuzz
except ImportError:
    print("Required packages not found. Please run: pip install colorama keyboard fuzzywuzzy")
    sys.exit(1)

# Initialize colorama
colorama.init()

class WZF:
    def __init__(self):
        self.files = []
        self.filtered_files = []
        self.query = ""
        self.selected_index = 0
        self.page_size = 10
        self.page_start = 0
        self.running = True
        self.exclude_dirs = ['.git', 'node_modules', '__pycache__', 'venv', '.venv', '.env']
        self.exclude_files = ['.gitignore', '.DS_Store', 'Thumbs.db']
        self.max_depth = 10  # Default max directory depth

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def scan_directory(self, directory, depth=0):
        """Scan a directory for files recursively."""
        if depth > self.max_depth:
            return []
        
        try:
            files = []
            for entry in os.scandir(directory):
                if entry.is_dir():
                    if entry.name not in self.exclude_dirs:
                        files.extend(self.scan_directory(entry.path, depth + 1))
                elif entry.is_file() and entry.name not in self.exclude_files:
                    files.append(entry.path)
            return files
        except (PermissionError, OSError):
            return []

    def scan_drives(self):
        """Scan all available drives on Windows."""
        drives = []
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for letter in range(65, 91):  # A-Z
            if bitmask & 1:
                drives.append(chr(letter) + ":\\")
            bitmask >>= 1
        return drives

    def index_files(self, path=None, all_drives=False):
        """Index files from the specified path or all drives."""
        print(f"{Fore.CYAN}Indexing files...{Style.RESET_ALL}")
        start_time = time.time()
        
        if all_drives:
            drives = self.scan_drives()
            print(f"{Fore.YELLOW}Scanning drives: {', '.join(drives)}{Style.RESET_ALL}")
            
            with ThreadPoolExecutor(max_workers=min(len(drives), 4)) as executor:
                results = list(executor.map(self.scan_directory, drives))
            
            for result in results:
                self.files.extend(result)
        else:
            path = path or os.getcwd()
            print(f"{Fore.YELLOW}Scanning directory: {path}{Style.RESET_ALL}")
            self.files = self.scan_directory(path)
        
        elapsed = time.time() - start_time
        print(f"{Fore.GREEN}Indexed {len(self.files)} files in {elapsed:.2f} seconds{Style.RESET_ALL}")

    def filter_files(self):
        """Filter files based on the current query."""
        if not self.query:
            self.filtered_files = self.files[:1000]  # Limit to 1000 files when no query
            return

        # Simple case: direct substring match (fast)
        if len(self.query) <= 3:
            query_lower = self.query.lower()
            self.filtered_files = [f for f in self.files if query_lower in os.path.basename(f).lower()]
            return

        # More complex fuzzy matching for longer queries
        scored_files = []
        query_lower = self.query.lower()
        
        for file in self.files:
            filename = os.path.basename(file)
            
            # Quick pre-filter: if any character in query isn't in the filename, skip
            if not all(c in filename.lower() for c in query_lower):
                continue
                
            # Calculate fuzzy match score
            score = fuzz.partial_ratio(query_lower, filename.lower())
            if score > 60:  # Only keep reasonable matches
                scored_files.append((file, score))
        
        # Sort by score (descending)
        scored_files.sort(key=lambda x: x[1], reverse=True)
        self.filtered_files = [f[0] for f in scored_files[:1000]]  # Limit to top 1000 matches

    def display_results(self):
        """Display the filtered results."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}WZF - Windows Fuzzy Finder{Style.RESET_ALL}")
        print(f"Search: {Fore.GREEN}{self.query}{Style.RESET_ALL}")
        print(f"Found {len(self.filtered_files)} matches\n")

        if not self.filtered_files:
            print(f"{Fore.YELLOW}No matches found.{Style.RESET_ALL}")
            return

        end_index = min(self.page_start + self.page_size, len(self.filtered_files))
        
        for i in range(self.page_start, end_index):
            file_path = self.filtered_files[i]
            file_name = os.path.basename(file_path)
            dir_name = os.path.dirname(file_path)
            
            if i == self.selected_index:
                print(f"{Fore.BLACK}{Style.BRIGHT}{Fore.WHITE}> {file_name}{Style.RESET_ALL} {Fore.BLUE}({dir_name}){Style.RESET_ALL}")
            else:
                print(f"  {Fore.WHITE}{file_name}{Style.RESET_ALL} {Fore.BLUE}({dir_name}){Style.RESET_ALL}")
        
        if len(self.filtered_files) > self.page_size:
            current_page = (self.page_start // self.page_size) + 1
            total_pages = (len(self.filtered_files) + self.page_size - 1) // self.page_size
            print(f"\n{Fore.CYAN}Page {current_page}/{total_pages} - Use PgUp/PgDn to navigate{Style.RESET_ALL}")
        
        print("\nControls:")
        print(f"{Fore.YELLOW}↑/↓{Style.RESET_ALL}: Navigate, {Fore.YELLOW}Enter{Style.RESET_ALL}: Select, {Fore.YELLOW}Esc{Style.RESET_ALL}: Quit")

    def handle_input(self):
        """Handle keyboard input."""
        event = keyboard.read_event()
        
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'esc':
                self.running = False
            elif event.name == 'up':
                self.selected_index = max(0, self.selected_index - 1)
                if self.selected_index < self.page_start:
                    self.page_start = max(0, self.page_start - self.page_size)
            elif event.name == 'down':
                self.selected_index = min(len(self.filtered_files) - 1, self.selected_index + 1)
                if self.selected_index >= self.page_start + self.page_size:
                    self.page_start = min(len(self.filtered_files) - 1, self.page_start + self.page_size)
            elif event.name == 'page up':
                self.page_start = max(0, self.page_start - self.page_size)
                self.selected_index = self.page_start
            elif event.name == 'page down':
                self.page_start = min(len(self.filtered_files) - 1, self.page_start + self.page_size)
                self.selected_index = self.page_start
            elif event.name == 'enter':
                if self.filtered_files and 0 <= self.selected_index < len(self.filtered_files):
                    selected_file = self.filtered_files[self.selected_index]
                    print(f"\n{Fore.GREEN}Selected: {selected_file}{Style.RESET_ALL}")
                    
                    # Open the file with default application
                    try:
                        os.startfile(selected_file)
                    except Exception as e:
                        print(f"{Fore.RED}Error opening file: {e}{Style.RESET_ALL}")
                    
                    time.sleep(1)  # Give user a moment to see the selection
                    self.running = False
            elif event.name == 'backspace':
                self.query = self.query[:-1]
                self.filter_files()
                self.selected_index = 0
                self.page_start = 0
            elif len(event.name) == 1 or event.name == 'space':
                char = ' ' if event.name == 'space' else event.name
                self.query += char
                self.filter_files()
                self.selected_index = 0
                self.page_start = 0

    def run(self, path=None, all_drives=False):
        """Run the fuzzy finder."""
        if all_drives and not self.is_admin():
            print(f"{Fore.RED}Warning: For full drive scanning, it's recommended to run as administrator.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Some directories may not be accessible.{Style.RESET_ALL}")
            time.sleep(2)
            
        self.index_files(path, all_drives)
        self.filter_files()
        
        while self.running:
            self.display_results()
            self.handle_input()
        
        # Clean up
        colorama.deinit()

def main():
    parser = argparse.ArgumentParser(description='WZF - Windows Fuzzy Finder')
    parser.add_argument('-p', '--path', help='Path to search in (default: current directory)')
    parser.add_argument('-a', '--all-drives', action='store_true', help='Search all drives (requires admin privileges)')
    parser.add_argument('-d', '--max-depth', type=int, default=10, help='Maximum directory depth to search')
    args = parser.parse_args()
    
    wzf = WZF()
    wzf.max_depth = args.max_depth
    wzf.run(args.path, args.all_drives)

if __name__ == "__main__":
    main()
