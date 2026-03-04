"""
UI constants for consistent interface design
"""

# Window dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_TITLE = "Google Maps Scraper Pro"

# Grid layout weights and sizes
GRID_WEIGHT_LEFT = 1
GRID_WEIGHT_MIDDLE = 1
GRID_WEIGHT_RIGHT = 2
GRID_MINSIZE_LEFT = 320
GRID_MINSIZE_MIDDLE = 280
GRID_MINSIZE_RIGHT = 500

# Progress and timing
RESULT_CHECK_INTERVAL = 100  # milliseconds
MAX_LOG_MESSAGES_PER_CALL = 100
PROGRESS_UPDATE_INTERVAL = 100

# Donation settings
DEFAULT_DONATION_URL = 'https://buymeacoffee.com/yourusername'
DEFAULT_DONATION_PLATFORM = 'buymeacoffee'
DEFAULT_DONATION_USERNAME = 'yourusername'

# Default values
DEFAULT_MAX_RESULTS = 20
DEFAULT_THREADS = 3
DEFAULT_TIMEOUT = 30000

# File paths
OUTPUT_DIR_NAME = "output"
CONFIG_DIR_NAME = "config"
DONATION_CONFIG_FILE = "donation.json"
SETTINGS_CONFIG_FILE = "settings.json"
PROXIES_CONFIG_FILE = "proxies.txt"

# UI text and labels
MENU_CONFIGURATION = "Configuration"
MENU_EDIT_SETTINGS = "Edit Settings (settings.json)"
MENU_EDIT_PROXIES = "Edit Proxies (proxies.txt)"

PANEL_LEFT_TITLE = "🗺️ Scraper"
PANEL_MIDDLE_THREADS_TITLE = "⚙️ Worker Threads"
PANEL_MIDDLE_STATUS_TITLE = "📋 Status Log"
PANEL_RIGHT_TITLE = "📊 Scraped Results"

# Button text
BUTTON_START = "▶ Start"
BUTTON_STOP = "⏹ Stop"
BUTTON_OPEN_OUTPUT = "📂 Open Output Folder"
BUTTON_EXPORT_CSV = "📄 CSV"
BUTTON_EXPORT_EXCEL = "📊 Excel"
BUTTON_CLEAR = "🗑️ Clear"
BUTTON_SAVE = "💾 Save"
BUTTON_DONATE = "💙 Make A donation"

# Status messages
STATUS_READY = "Ready to start scraping..."
STATUS_NO_THREADS = "No active threads"
STATUS_INITIALIZING = "Initializing..."
STATUS_ALL_COMPLETE = "✅ All threads completed"
STATUS_ALL_STOPPED = "⏹️ All threads force-stopped"

# Log level icons
LOG_ICONS = {
    'DEBUG': '🔍',
    'INFO': 'ℹ️',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'CRITICAL': '🔥'
}

# Error messages
ERROR_NO_QUERIES = "⚠️ Please enter at least one search query"
ERROR_INVALID_FORMAT = "⚠️ Invalid number format in settings"
ERROR_NO_DATA_EXPORT = "⚠️ No data to export"
ERROR_NO_PROXIES = "⚠️ No proxies configured, continuing without proxies"

# Success messages
SUCCESS_RESULTS_SAVED = "💾 Saved {task} results to: {filename}"
SUCCESS_COMBINED_SAVED = "💾 Saved combined results to: {filename}"
SUCCESS_EXPORTED_CSV = "✅ Exported to CSV: {filepath}"
SUCCESS_EXPORTED_EXCEL = "✅ Exported to Excel: {filepath}"
SUCCESS_FILE_OPENED = "📂 Opened {file_type} file"
