# GUI Structure Documentation

This document describes the refactored GUI structure for the Google Maps Scraper application.

## Overview

The GUI has been refactored from a monolithic 968-line MainWindow class into a modular, maintainable component-based architecture. This improves code readability, maintainability, and extensibility.

## Directory Structure

```
src/gui/
├── components/
│   ├── panels/              # Main UI panels
│   │   ├── left_panel.py    # Input controls and settings
│   │   ├── middle_panel.py  # Status and thread monitoring
│   │   └── right_panel.py  # Results display and export
│   ├── modals/              # Modal windows
│   │   ├── base_modal.py    # Base modal class
│   │   ├── settings_editor.py  # Settings configuration editor
│   │   └── proxy_editor.py     # Proxy configuration editor
│   └── widgets/             # Reusable UI widgets
│       ├── status_display.py    # Status message display
│       └── progress_tracker.py # Progress tracking widget
├── main_window.py           # Simplified main window (orchestrator)
├── styles.py                # Styles and theme configuration
└── README.md                # This documentation
```

## Components

### Panels

#### LeftPanel (`components/panels/left_panel.py`)
Contains all input controls and scraper settings:
- Search queries textbox
- Max results and threads configuration
- Proxy and headless mode checkboxes
- Start/stop/Open output folder buttons
- Donation section

**Key Methods:**
- `get_queries()` - Get search queries
- `get_max_results()` - Get max results setting
- `get_threads()` - Get thread count setting
- `get_use_proxy()` - Get proxy setting
- `get_headless()` - Get headless mode setting
- `get_auto_save()` - Get auto-save setting
- `set_scraping_state()` - Update button states

#### MiddlePanel (`components/panels/middle_panel.py`)
Handles thread monitoring and status logging:
- Progress bar
- Worker thread status display
- General status log

**Key Methods:**
- `update_threads_status()` - Update thread status display
- `update_threads_status_from_pool()` - Update from worker pool
- `add_status()` - Add status message
- `set_progress()` - Set progress bar value
- `reset_progress()` - Reset progress

#### RightPanel (`components/panels/right_panel.py`)
Displays results and export controls:
- Results textbox with colored logging
- Export buttons (CSV, Excel)
- Clear results button

**Key Methods:**
- `add_colored_result()` - Add colored message
- `clear_results()` - Clear display
- `add_result()` - Add plain message

### Modals

#### BaseModal (`components/modals/base_modal.py`)
Base class for modal windows with common functionality:
- Standard modal layout
- Textbox for content editing
- Status label for feedback
- Save button

#### SettingsEditor (`components/modals/settings_editor.py`)
Modal for editing `settings.json` configuration:
- JSON validation
- File saving with error handling

#### ProxyEditor (`components/modals/proxy_editor.py`)
Modal for editing `proxies.txt` configuration:
- Plain text editing
- File saving with error handling

### Widgets

#### StatusDisplay (`components/widgets/status_display.py`)
Reusable widget for displaying status messages:
- Colored message display
- Automatic message formatting
- Multiple log levels support

#### ProgressTracker (`components/widgets/progress_tracker.py`)
Widget for tracking scraping progress:
- Progress bar
- Statistics display
- Reset functionality

## Main Window

The `MainWindow` class now serves as an orchestrator:
- Creates and manages panel components
- Handles high-level application state
- Coordinates communication between components
- Manages scraping workflow and worker pool

**Key Responsibilities:**
- Component initialization and layout
- Event handling coordination
- Scraping process management
- Result processing and notifications

## Benefits of Refactoring

### Maintainability
- Smaller, focused classes are easier to understand and modify
- Clear separation of concerns
- Reduced code complexity

### Testability
- Individual components can be unit tested
- Isolated functionality makes testing easier
- Mock dependencies for testing

### Reusability
- Components can be reused in other parts of the application
- Modular design allows for easy extension
- Common patterns extracted into reusable widgets

### Readability
- Clear component boundaries
- Self-documenting structure
- Easier code navigation

## Usage Examples

### Creating a New Panel
```python
from src.gui.components.panels.base_panel import BasePanel

class CustomPanel(BasePanel):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_ui()
    
    def _create_ui(self):
        # Panel UI creation
        pass
```

### Using a Modal
```python
from src.gui.components.modals.settings_editor import SettingsEditor

# Open settings editor
settings_modal = SettingsEditor(self, logger)
```

### Adding to Main Window
```python
# In MainWindow._create_ui()
self.custom_panel = CustomPanel(self)
self.custom_panel.grid(row=0, column=0, sticky="nsew")
```

## Migration Notes

The original `main_window_original.py` file has been preserved as a backup. All functionality has been maintained while improving the code structure.

## Future Enhancements

This modular structure makes it easy to:
- Add new panels or widgets
- Implement different themes
- Create plugin-based extensions
- Add comprehensive testing
- Implement accessibility features
