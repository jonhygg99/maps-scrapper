"""
Logging Manager
Centralized logging system with handler management
"""
import logging
import sys
import queue
from pathlib import Path
from typing import Optional

from .config import LoggingConfig
from .ui_handler import UILogHandler


class Logger:
    """Centralized logging system"""
    
    _loggers = {}
    _initialized = False
    _ui_handler = None
    _log_queue = None
    
    @classmethod
    def initialize(cls, log_dir: Optional[Path] = None, level: str = "INFO"):
        """Initialize logging system with file and console output"""
        if cls._initialized:
            return
        
        # Create log queue for UI messages
        cls._log_queue = queue.Queue(maxsize=1000)
        
        # Setup log directory and file
        log_dir = LoggingConfig.setup_log_directory(log_dir)
        log_file = LoggingConfig.generate_log_filename(log_dir)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(LoggingConfig.parse_log_level(level))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Add file handler
        file_handler = LoggingConfig.create_file_handler(log_file)
        root_logger.addHandler(file_handler)
        
        # Add console handler
        console_handler = LoggingConfig.create_console_handler()
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
        root_logger.info(f"Logging initialized - Log file: {log_file}")
    
    @classmethod
    def get_log_queue(cls) -> queue.Queue:
        """Get the log queue for UI processing"""
        if not cls._initialized:
            cls.initialize()
        return cls._log_queue
    
    @classmethod
    def add_ui_handler(cls):
        """Add UI handler to send log messages to queue"""
        if not cls._initialized:
            cls.initialize()
        
        # Remove existing UI handler if present
        if cls._ui_handler:
            logging.getLogger().removeHandler(cls._ui_handler)
        
        # Create and add new UI handler
        cls._ui_handler = UILogHandler(cls._log_queue)
        cls._ui_handler.setLevel(logging.INFO)
        cls._ui_handler.setFormatter(LoggingConfig.create_console_formatter())
        logging.getLogger().addHandler(cls._ui_handler)
    
    @classmethod
    def remove_ui_handler(cls):
        """Remove UI handler"""
        if cls._ui_handler:
            logging.getLogger().removeHandler(cls._ui_handler)
            cls._ui_handler = None
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger instance"""
        if not cls._initialized:
            cls.initialize()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, level: str):
        """Set logging level for all loggers"""
        logging.getLogger().setLevel(LoggingConfig.parse_log_level(level))
    
    @classmethod
    def disable_console_logging(cls):
        """Disable console output (keep file logging only)"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                root_logger.removeHandler(handler)
    
    @classmethod
    def enable_console_logging(cls):
        """Enable console output"""
        root_logger = logging.getLogger()
        
        # Check if console handler already exists
        has_console = any(
            isinstance(h, logging.StreamHandler) and h.stream == sys.stdout
            for h in root_logger.handlers
        )
        
        if not has_console:
            console_handler = LoggingConfig.create_console_handler()
            root_logger.addHandler(console_handler)
