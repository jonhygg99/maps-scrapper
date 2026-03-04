# Logging System

A modular logging system that provides centralized logging with file and console output, plus UI integration capabilities.

## Architecture

The logging system is organized into several components:

- **`manager.py`**: Core Logger class with main functionality
- **`config.py`**: Configuration management and formatter setup
- **`ui_handler.py`**: Queue-based UI message handling
- **`__init__.py`**: Main entry point maintaining backward compatibility

## Usage

### Basic Usage

```python
from src.utils.logging import Logger

# Initialize the logging system
Logger.initialize()

# Get a logger instance
logger = Logger.get_logger(__name__)

# Log messages
logger.info("Application started")
logger.error("An error occurred")
```

### Advanced Usage

```python
from pathlib import Path

# Initialize with custom settings
Logger.initialize(
    log_dir=Path("custom_logs"),
    level="DEBUG"
)

# Add UI handler for GUI applications
Logger.add_ui_handler()

# Get log queue for UI processing
log_queue = Logger.get_log_queue()

# Control console output
Logger.disable_console_logging()
Logger.enable_console_logging()

# Change logging level
Logger.set_level("WARNING")
```

## Features

- **File Logging**: Automatic timestamped log files
- **Console Logging**: Real-time console output
- **UI Integration**: Queue-based message handling for GUI applications
- **Thread Safety**: Safe for use in multi-threaded applications
- **Configurable**: Customizable log levels and directories
- **Backward Compatible**: Existing imports continue to work

## Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General information messages
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures
- `CRITICAL`: Critical errors that may stop the application

## File Structure

Log files are automatically named with timestamps:
```
logs/
├── scraper_20260304_160500.log
├── scraper_20260304_161200.log
└── ...
```

## UI Integration

For GUI applications, use the UI handler to display log messages:

```python
# Add UI handler
Logger.add_ui_handler()

# Get messages from queue
log_queue = Logger.get_log_queue()
while True:
    try:
        message = log_queue.get_nowait()
        # Display message in UI
        print(f"{message['level']}: {message['message']}")
    except queue.Empty:
        break
```
