#!/usr/bin/env python3
"""
WZF - Windows Fuzzy Finder
A lightning-fast fuzzy finder for Windows, inspired by fzf.
"""

import os
import sys
import argparse
import re
import subprocess
from pathlib import Path
import ctypes
import pickle
import hashlib
import multiprocessing
import threading
import queue
import time
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache

try:
    import colorama
    from colorama import Fore, Style
    import keyboard
    from rapidfuzz import process, fuzz
    import win32api
    import win32con
    import psutil
except ImportError:
    print("Required packages not found. Please run: pip install colorama keyboard rapidfuzz pywin32 psutil")
    sys.exit(1)

# Initialize colorama
colorama.init()

# Set process priority to high for better performance
try:
    p = psutil.Process(os.getpid())
    p.nice(psutil.HIGH_PRIORITY_CLASS)
except:
    pass

class WZF:
    def __init__(self):
        self.files = []
        self.filtered_files = []
        self.query = ""
        self.selected_index = 0
        self.page_size = 10
        self.page_start = 0
        self.running = True
        self.exclude_dirs = ['.git', 'node_modules', '__pycache__', 'venv', '.venv', '.env', '$Recycle.Bin', 'System Volume Information', 'Windows.old']
        self.exclude_files = ['.gitignore', '.DS_Store', 'Thumbs.db', 'desktop.ini']
        self.max_depth = 10  # Default max directory depth
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.wzf_cache')
        self.file_index = {}
        self.filename_index = {}
        self.search_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.search_thread = None
        self.use_cache = True
        self.cache_ttl = 86400  # Cache time-to-live in seconds (24 hours)
        self.worker_count = max(1, multiprocessing.cpu_count() - 1)

        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except:
                self.use_cache = False

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def get_cache_path(self, path):
        """Generate a cache file path based on the input path."""
        if path is None:
            path = os.getcwd()
        path_hash = hashlib.md5(path.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"wzf_cache_{path_hash}.pkl")

    def load_cache(self, path):
        """Load file index from cache if available and not expired."""
        if not self.use_cache:
            return None

        cache_path = self.get_cache_path(path)
        if not os.path.exists(cache_path):
            return None

        # Check if cache is expired
        cache_time = os.path.getmtime(cache_path)
        if time.time() - cache_time > self.cache_ttl:
            return None

        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            print(f"{Fore.GREEN}Loaded {len(cache_data['files'])} files from cache{Style.RESET_ALL}")
            return cache_data
        except:
            return None

    def save_cache(self, path, data):
        """Save file index to cache."""
        if not self.use_cache:
            return

        cache_path = self.get_cache_path(path)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
        except:
            pass

    def scan_directory(self, directory, depth=0, queue=None):
        """Scan a directory for files recursively."""
        if depth > self.max_depth:
            return []

        try:
            files = []
            dirs_to_scan = []

            # Fast scan using os.scandir
            try:
                entries = list(os.scandir(directory))
            except (PermissionError, OSError):
                return []

            # Process files first (faster)
            for entry in entries:
                try:
                    if entry.is_file():
                        if entry.name not in self.exclude_files:
                            file_path = entry.path
                            files.append(file_path)
                            # Pre-compute filename for faster searching later
                            filename = os.path.basename(file_path).lower()
                            self.filename_index[file_path] = filename
                    elif entry.is_dir() and entry.name not in self.exclude_dirs:
                        dirs_to_scan.append(entry.path)
                except (PermissionError, OSError):
                    continue

            # Process subdirectories with threading for better performance
            if dirs_to_scan and depth < self.max_depth:
                if len(dirs_to_scan) > 4:  # Only use threading for multiple directories
                    with ThreadPoolExecutor(max_workers=min(len(dirs_to_scan), self.worker_count)) as executor:
                        results = list(executor.map(lambda d: self.scan_directory(d, depth + 1), dirs_to_scan))
                    for result in results:
                        files.extend(result)
                else:
                    for dir_path in dirs_to_scan:
                        files.extend(self.scan_directory(dir_path, depth + 1))

            # Report progress for top-level scans
            if depth == 0 and queue is not None:
                queue.put((directory, len(files)))

            return files
        except (PermissionError, OSError):
            if depth == 0 and queue is not None:
                queue.put((directory, 0))
            return []

    def scan_drives(self):
        """Scan all available drives on Windows using Win32 API for better performance."""
        try:
            drives = []
            # Use Win32 API for faster drive detection
            drive_bits = win32api.GetLogicalDrives()
            for i in range(26):  # A-Z
                if drive_bits & (1 << i):
                    drive_letter = chr(65 + i) + ":\\"
                    # Skip CD/DVD drives and network drives for performance
                    drive_type = win32api.GetDriveType(drive_letter)
                    if drive_type == win32con.DRIVE_FIXED or drive_type == win32con.DRIVE_REMOVABLE:
                        drives.append(drive_letter)
            return drives
        except:
            # Fallback to standard method
            drives = []
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for letter in range(65, 91):  # A-Z
                if bitmask & 1:
                    drives.append(chr(letter) + ":\\")
                bitmask >>= 1
            return drives

    def progress_reporter(self, total_dirs):
        """Report indexing progress."""
        dirs_completed = 0
        total_files = 0
        start_time = time.time()
        last_update = 0

        while dirs_completed < total_dirs:
            try:
                directory, file_count = self.progress_queue.get(timeout=0.1)
                dirs_completed += 1
                total_files += file_count

                # Update progress at most once per second
                current_time = time.time()
                if current_time - last_update >= 1.0:
                    elapsed = current_time - start_time
                    files_per_second = int(total_files / elapsed) if elapsed > 0 else 0
                    print(f"\r{Fore.CYAN}Indexed {total_files} files ({files_per_second}/sec) - {dirs_completed}/{total_dirs} locations scanned...{Style.RESET_ALL}", end="")
                    last_update = current_time

            except queue.Empty:
                continue

        # Final update
        elapsed = time.time() - start_time
        files_per_second = int(total_files / elapsed) if elapsed > 0 else 0
        print(f"\r{Fore.GREEN}Indexed {total_files} files in {elapsed:.2f} seconds ({files_per_second}/sec){Style.RESET_ALL}")

    def index_files(self, path=None, all_drives=False):
        """Index files from the specified path or all drives with caching."""
        print(f"{Fore.CYAN}Indexing files...{Style.RESET_ALL}")
        start_time = time.time()

        # Try to load from cache first
        if not all_drives:
            path = path or os.getcwd()
            cache_data = self.load_cache(path)
            if cache_data:
                self.files = cache_data['files']
                self.filename_index = cache_data['filename_index']
                return

        # Set up progress reporting
        self.progress_queue = queue.Queue()

        if all_drives:
            drives = self.scan_drives()
            print(f"{Fore.YELLOW}Scanning drives: {', '.join(drives)}{Style.RESET_ALL}")

            # Start progress reporter thread
            progress_thread = threading.Thread(target=self.progress_reporter, args=(len(drives),))
            progress_thread.daemon = True
            progress_thread.start()

            # Use process pool for better performance across multiple drives
            with ProcessPoolExecutor(max_workers=self.worker_count) as executor:
                scan_tasks = []
                for drive in drives:
                    scan_tasks.append(executor.submit(self.scan_directory, drive, 0, self.progress_queue))

                self.files = []
                for task in scan_tasks:
                    try:
                        result = task.result()
                        self.files.extend(result)
                    except:
                        pass
        else:
            path = path or os.getcwd()
            print(f"{Fore.YELLOW}Scanning directory: {path}{Style.RESET_ALL}")

            # Start progress reporter thread
            progress_thread = threading.Thread(target=self.progress_reporter, args=(1,))
            progress_thread.daemon = True
            progress_thread.start()

            self.files = self.scan_directory(path, queue=self.progress_queue)

        # Wait for progress reporter to finish
        progress_thread.join()

        # Save to cache if not scanning all drives
        if not all_drives:
            cache_data = {
                'files': self.files,
                'filename_index': self.filename_index
            }
            self.save_cache(path, cache_data)

    def async_search(self):
        """Background thread for asynchronous searching."""
        while True:
            query = self.search_queue.get()
            if query is None:  # Sentinel to stop the thread
                break

            # Start with empty results
            results = []

            # If query is empty, return top files
            if not query:
                self.result_queue.put(self.files[:1000])
                continue

            # Simple case: direct substring match (fast)
            if len(query) <= 2:
                query_lower = query.lower()
                # Use pre-computed filename index for faster matching
                results = [f for f in self.files if query_lower in self.filename_index.get(f, os.path.basename(f).lower())]
                self.result_queue.put(results[:1000])
                continue

            # For medium-length queries, use faster contains matching with pre-filtering
            if len(query) <= 4:
                query_lower = query.lower()
                candidates = []

                # First pass: quick pre-filtering
                for file in self.files:
                    filename = self.filename_index.get(file, os.path.basename(file).lower())
                    if all(c in filename for c in query_lower):
                        candidates.append(file)

                # Second pass: more accurate substring matching
                results = [f for f in candidates if query_lower in self.filename_index.get(f, os.path.basename(f).lower())]
                self.result_queue.put(results[:1000])
                continue

            # For longer queries, use rapidfuzz for better fuzzy matching
            query_lower = query.lower()

            # Pre-filter candidates to reduce the search space
            candidates = []
            for file in self.files:
                filename = self.filename_index.get(file, os.path.basename(file).lower())
                if all(c in filename for c in query_lower):
                    candidates.append(file)

            # If we have too many candidates, limit them
            if len(candidates) > 10000:
                candidates = candidates[:10000]

            # Use rapidfuzz for faster, more accurate fuzzy matching
            if candidates:
                # Extract filenames for matching
                filenames = [os.path.basename(f).lower() for f in candidates]

                # Use process.extract for batch processing (much faster)
                matches = process.extract(query_lower, filenames, limit=1000, scorer=fuzz.partial_ratio, score_cutoff=65)

                # Map back to full paths
                results = [candidates[filenames.index(match[0])] for match in matches]

            self.result_queue.put(results)

    def filter_files(self):
        """Filter files based on the current query using async search."""
        # Start the search thread if it's not running
        if self.search_thread is None or not self.search_thread.is_alive():
            self.search_thread = threading.Thread(target=self.async_search)
            self.search_thread.daemon = True
            self.search_thread.start()

        # Put the query in the search queue
        while not self.search_queue.empty():
            try:
                self.search_queue.get_nowait()
            except queue.Empty:
                break
        self.search_queue.put(self.query)

        # Wait for results with a short timeout
        try:
            self.filtered_files = self.result_queue.get(timeout=0.1)
        except queue.Empty:
            # If no results yet, keep previous results
            pass

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

    def run(self, path=None, all_drives=False, use_cache=True):
        """Run the fuzzy finder."""
        self.use_cache = use_cache

        # Check if running in Docker
        in_docker = os.path.exists('/.dockerenv')

        if in_docker and all_drives:
            print(f"{Fore.RED}Warning: Scanning all drives is not supported in Docker mode.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please use the -p option to specify a directory within the mounted volume.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Example: wzf -p /data{Style.RESET_ALL}")
            time.sleep(3)
            return

        if all_drives and not self.is_admin():
            print(f"{Fore.RED}Warning: For full drive scanning, it's recommended to run as administrator.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Some directories may not be accessible.{Style.RESET_ALL}")
            time.sleep(2)

        # Start the search thread
        self.search_thread = threading.Thread(target=self.async_search)
        self.search_thread.daemon = True
        self.search_thread.start()

        # Index files
        self.index_files(path, all_drives)

        # Initial filter
        self.search_queue.put(self.query)
        try:
            self.filtered_files = self.result_queue.get(timeout=0.5) or self.files[:1000]
        except queue.Empty:
            self.filtered_files = self.files[:1000]

        # Main loop
        while self.running:
            self.display_results()
            self.handle_input()

        # Clean up
        self.search_queue.put(None)  # Signal search thread to stop
        self.search_thread.join(timeout=0.5)
        colorama.deinit()

def main():
    # Check if running in Docker
    in_docker = os.path.exists('/.dockerenv')

    parser = argparse.ArgumentParser(description='WZF - Windows Fuzzy Finder')
    parser.add_argument('-p', '--path', help='Path to search in (default: current directory or /data in Docker)')
    parser.add_argument('-a', '--all-drives', action='store_true', help='Search all drives (requires admin privileges, not available in Docker)')
    parser.add_argument('-d', '--max-depth', type=int, default=10, help='Maximum directory depth to search')
    parser.add_argument('-n', '--no-cache', action='store_true', help='Disable file index caching')
    parser.add_argument('-c', '--clear-cache', action='store_true', help='Clear the cache before starting')
    parser.add_argument('-w', '--workers', type=int, help='Number of worker threads/processes to use')
    parser.add_argument('-v', '--version', action='store_true', help='Show version information')
    args = parser.parse_args()

    # Show version and exit if requested
    if args.version:
        print("WZF - Windows Fuzzy Finder v1.0.0")
        print("Optimized for maximum performance with Docker support")
        sys.exit(0)

    # Set default path for Docker
    if in_docker and not args.path:
        args.path = '/data'

    # Clear cache if requested
    if args.clear_cache:
        cache_dir = os.path.join(os.path.expanduser('~'), '.wzf_cache')
        if os.path.exists(cache_dir):
            print(f"{Fore.YELLOW}Clearing cache...{Style.RESET_ALL}")
            for file in os.listdir(cache_dir):
                if file.startswith("wzf_cache_"):
                    try:
                        os.remove(os.path.join(cache_dir, file))
                    except:
                        pass

    wzf = WZF()
    wzf.max_depth = args.max_depth

    # Set worker count if specified
    if args.workers:
        wzf.worker_count = max(1, args.workers)

    wzf.run(args.path, args.all_drives, not args.no_cache)

if __name__ == "__main__":
    main()
