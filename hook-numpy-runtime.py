"""
Runtime hook for PyInstaller to fix numpy import issues.
This hook ensures numpy can be imported correctly in the frozen application.
"""
import sys
import os

# Remove any numpy source paths from sys.path
sys.path = [p for p in sys.path if 'numpy' not in p.lower() or 'site-packages' in p.lower()]

# Ensure the application's base directory is in the path
if hasattr(sys, '_MEIPASS'):
    # Running as PyInstaller bundle
    base_path = sys._MEIPASS
    
    # Add the base path to sys.path if not already there
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    # Set environment variable to prevent numpy from detecting source directory
    os.environ['NUMPY_MADVISE_HUGEPAGE'] = '0'
