"""
Platform-specific utility functions
"""
import platform
from src.gui.constants.scraping_constants import (
    PLATFORM_WINDOWS, PLATFORM_MACOS, PLATFORM_LINUX
)


def is_windows():
    """Check if running on Windows"""
    return platform.system() == PLATFORM_WINDOWS


def is_macos():
    """Check if running on macOS"""
    return platform.system() == PLATFORM_MACOS


def is_linux():
    """Check if running on Linux"""
    return platform.system() == PLATFORM_LINUX


def get_platform_name():
    """Get current platform name"""
    return platform.system()


def get_file_open_command():
    """Get the appropriate file open command for current platform"""
    if is_windows():
        return 'start'
    elif is_macos():
        return 'open'
    else:  # Linux
        return 'xdg-open'
