"""
Scraping workflow constants and configuration
"""

# Scraping limits and defaults
MAX_SAFE_FILENAME_LENGTH = 50
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
COMBINED_FILENAME_PREFIX = "combined_all_results"

# File naming patterns
SAFE_FILENAME_PATTERN = r'[^\w\s-]'
SAFE_FILENAME_REPLACEMENT = '_'
DASH_SPACE_PATTERN = r'[-\s]+'

# Notification settings
ERROR_MESSAGE_TRUNCATE_LENGTH = 80
SUCCESS_NOTIFICATION_TRUNCATE_LENGTH = 100

# Worker pool settings
WORKER_POOL_TIMEOUT = 0.1  # seconds for result checking

# File operations
FILE_OPEN_TIMEOUT_WINDOWS = "startfile"
FILE_OPEN_TIMEOUT_MACOS = "open"
FILE_OPEN_TIMEOUT_LINUX = "xdg-open"

# Platform names
PLATFORM_WINDOWS = 'Windows'
PLATFORM_MACOS = 'Darwin'
PLATFORM_LINUX = 'Linux'

# File paths
DONATION_CONFIG_FILE = "donation.json"
SETTINGS_CONFIG_FILE = "settings.json"
PROXIES_CONFIG_FILE = "proxies.txt"

# Donation settings
DEFAULT_DONATION_URL = 'https://buymeacoffee.com/yourusername'
DEFAULT_DONATION_PLATFORM = 'buymeacoffee'
DEFAULT_DONATION_USERNAME = 'yourusername'

# Export formats
EXPORT_FORMAT_CSV = 'csv'
EXPORT_FORMAT_EXCEL = 'excel'

# Status tracking
PROGRESS_COMPLETE = 1.0
PROGRESS_RESET = 0.0
