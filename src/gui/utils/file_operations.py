"""
File and folder operations utilities
"""
import os
import platform
import subprocess
from pathlib import Path
from src.gui.constants.scraping_constants import (
    PLATFORM_WINDOWS, PLATFORM_MACOS, PLATFORM_LINUX,
    FILE_OPEN_TIMEOUT_WINDOWS, FILE_OPEN_TIMEOUT_MACOS, FILE_OPEN_TIMEOUT_LINUX,
    TIMESTAMP_FORMAT, COMBINED_FILENAME_PREFIX,
    SAFE_FILENAME_PATTERN, SAFE_FILENAME_REPLACEMENT,
    DASH_SPACE_PATTERN, MAX_SAFE_FILENAME_LENGTH
)
from src.gui.constants.ui_constants import OUTPUT_DIR_NAME, CONFIG_DIR_NAME


def get_output_directory():
    """Get the output directory path"""
    base_dir = Path(__file__).parent.parent.parent.parent
    return base_dir / OUTPUT_DIR_NAME


def get_config_directory():
    """Get the config directory path"""
    base_dir = Path(__file__).parent.parent.parent.parent
    return base_dir / CONFIG_DIR_NAME


def ensure_directory_exists(directory_path):
    """Ensure directory exists, create if it doesn't"""
    if not directory_path.exists():
        directory_path.mkdir(parents=True, exist_ok=True)


def open_file_with_default_app(file_path):
    """Open file with system's default application"""
    try:
        current_platform = platform.system()
        if current_platform == PLATFORM_WINDOWS:
            os.startfile(file_path)
        elif current_platform == PLATFORM_MACOS:
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])
        return True
    except Exception:
        return False


def open_directory_with_explorer(directory_path):
    """Open directory in system file explorer"""
    ensure_directory_exists(directory_path)
    return open_file_with_default_app(directory_path)


def create_safe_filename(task_name, timestamp):
    """Create a safe filename from task name"""
    import re
    from src.gui.constants.scraping_constants import (
        SAFE_FILENAME_PATTERN, SAFE_FILENAME_REPLACEMENT,
        DASH_SPACE_PATTERN, MAX_SAFE_FILENAME_LENGTH
    )
    
    safe_task_name = re.sub(SAFE_FILENAME_PATTERN, '', task_name).strip()
    safe_task_name = re.sub(DASH_SPACE_PATTERN, SAFE_FILENAME_REPLACEMENT, safe_task_name)
    
    # Truncate if too long
    if len(safe_task_name) > MAX_SAFE_FILENAME_LENGTH:
        safe_task_name = safe_task_name[:MAX_SAFE_FILENAME_LENGTH]
    
    return f"{safe_task_name}_{timestamp}"
