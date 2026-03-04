"""
Logging System for Application
Provides centralized logging with file and console output
"""
import logging
import sys
import queue
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable


class UILogHandler(logging.Handler):
    """Custom handler that queues log messages for UI processing"""
    
    def __init__(self, log_queue: queue.Queue):
        """
        Initialize UI log handler
        
        Args:
            log_queue: Queue to put log messages into
        """
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        """Emit a log record to the queue (thread-safe)"""
        try:
            msg = self.format(record)
            # Put the message in queue without blocking
            try:
                self.log_queue.put_nowait({
                    'level': record.levelname,
                    'message': msg
                })
            except queue.Full:
                # Queue is full, skip this message
                pass
        except Exception:
            self.handleError(record)


class Logger:
    """Centralized logging system"""
    
    _loggers = {}
    _initialized = False
    _ui_handler = None
    _log_queue = None
    
    @classmethod
    def initialize(cls, log_dir: Optional[Path] = None, level: str = "INFO"):
        """
        Initialize logging system
        
        Args:
            log_dir: Directory to store log files
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        if cls._initialized:
            return
        
        # Create log queue for UI messages
        cls._log_queue = queue.Queue(maxsize=1000)
        
        # Set log directory
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        
        log_dir = Path(log_dir)
        log_dir.mkdir(exist_ok=True)
        
        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"scraper_{timestamp}.log"
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
        
        root_logger.info(f"Logging initialized - Log file: {log_file}")
    
    @classmethod
    def get_log_queue(cls) -> queue.Queue:
        """
        Get the log queue for UI processing
        
        Returns:
            Queue containing log messages
        """
        if not cls._initialized:
            cls.initialize()
        return cls._log_queue
    
    @classmethod
    def add_ui_handler(cls):
        """
        Add UI handler to send log messages to queue
        """
        if not cls._initialized:
            cls.initialize()
        
        # Remove existing UI handler if present
        if cls._ui_handler:
            logging.getLogger().removeHandler(cls._ui_handler)
        
        # Create and add new UI handler
        cls._ui_handler = UILogHandler(cls._log_queue)
        cls._ui_handler.setLevel(logging.INFO)
        ui_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        cls._ui_handler.setFormatter(ui_formatter)
        logging.getLogger().addHandler(cls._ui_handler)
    
    @classmethod
    def remove_ui_handler(cls):
        """Remove UI handler"""
        if cls._ui_handler:
            logging.getLogger().removeHandler(cls._ui_handler)
            cls._ui_handler = None
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get or create a logger instance
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Logger instance
        """
        if not cls._initialized:
            cls.initialize()
        
        if name not in cls._loggers:
            cls._loggers[name] = logging.getLogger(name)
        
        return cls._loggers[name]
    
    @classmethod
    def set_level(cls, level: str):
        """
        Set logging level for all loggers
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        logging.getLogger().setLevel(getattr(logging, level.upper()))
    
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
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
