# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Google Maps Scraper
Builds a standalone Windows executable with icon
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Import required modules to get their paths
try:
    import customtkinter
    import playwright
    import numpy
    import pandas
except ImportError as e:
    print(f"Error: Required module not found: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Get absolute paths
project_root = Path('.').absolute()
src_path = project_root / 'src'
config_path = project_root / 'config'

# Get module paths
customtkinter_path = Path(customtkinter.__file__).parent
playwright_path = Path(playwright.__file__).parent

# Get Playwright browser path - need to bundle multiple browser types
try:
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    chromium_executable = Path(p.chromium.executable_path)
    p.stop()
    
    # Get the parent directory containing all playwright browsers (ms-playwright folder)
    # This includes chromium-XXXX, chromium_headless_shell-XXXX, etc.
    playwright_browsers_dir = chromium_executable.parent.parent.parent
    print(f"Found Playwright browsers at: {playwright_browsers_dir}")
    
    # List all browser directories to bundle
    browser_dirs = [d for d in playwright_browsers_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    print(f"Bundling browsers: {[d.name for d in browser_dirs]}")
except Exception as e:
    print(f"Warning: Could not find Playwright browsers: {e}")
    print("Please run: playwright install chromium")
    sys.exit(1)

# Collect all numpy and pandas data
numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')
pandas_datas, pandas_binaries, pandas_hiddenimports = collect_all('pandas')

# Filter out test modules from hidden imports (they're huge and not needed)
numpy_hiddenimports = [h for h in numpy_hiddenimports if '.tests' not in h and '.test_' not in h]
pandas_hiddenimports = [h for h in pandas_hiddenimports if '.tests' not in h and '.test_' not in h]

# Filter out test data files
numpy_datas = [(src, dst) for src, dst in numpy_datas if 'tests' not in src.lower()]
pandas_datas = [(src, dst) for src, dst in pandas_datas if 'tests' not in src.lower()]

block_cipher = None

# Build datas list with all browser directories
browser_datas = []
for browser_dir in browser_dirs:
    browser_datas.append((str(browser_dir), f'playwright_browsers/{browser_dir.name}'))

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=numpy_binaries + pandas_binaries,
    datas=[
        # Include config files
        (str(config_path / 'settings.json'), 'config'),
        (str(config_path / 'proxies.txt'), 'config'),
        # Include CustomTkinter assets
        (str(customtkinter_path), 'customtkinter'),
        # Include playwright driver
        (str(playwright_path), 'playwright'),
        # Include ALL Playwright browsers
    ] + browser_datas + [
    ] + numpy_datas + pandas_datas,
    hiddenimports=[
        'customtkinter',
        'playwright',
        'playwright.sync_api',
        'playwright.async_api',
        'playwright_stealth',
        'plyer.platforms.win.notification',
        'openpyxl',
        'aiofiles',
        'httpx',
        'greenlet',
        'subprocess',
        'src.gui.main_window',
        'src.gui.styles',
        'src.scraper.google_maps',
        'src.scraper.stealth',
        'src.scraper.proxy_manager',
        'src.utils.logger',
        'src.utils.data_processor',
        'src.utils.exporter',
        'src.utils.notifier',
        'src.core.config',
        'src.core.worker',
    ] + numpy_hiddenimports + pandas_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook-numpy-runtime.py'],
    excludes=[
        'matplotlib',
        'scipy',
        'PIL',
        'tkinter.test',
        'numpy.distutils',
        'numpy.f2py',
        'numpy.testing',
        'numpy.core.tests',
        'numpy.tests',
        'pandas.tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GoogleMapsScraper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',  # Custom icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GoogleMapsScraper',
)
