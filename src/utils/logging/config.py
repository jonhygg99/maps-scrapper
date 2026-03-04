"""
Logging Configuration Management
Handles formatters and handler setup for the logging system
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


class LoggingConfig:
    """Manages logging configuration and setup"""
    
    @staticmethod
    def create_file_formatter():
        """Create formatter for file logging"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    @staticmethod
    def create_console_formatter():
        """Create formatter for console logging"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    @staticmethod
    def create_file_handler(log_file: Path):
        """Create and configure file handler"""
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(LoggingConfig.create_file_formatter())
        return file_handler
    
    @staticmethod
    def create_console_handler():
        """Create and configure console handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(LoggingConfig.create_console_formatter())
        return console_handler
    
    @staticmethod
    def setup_log_directory(log_dir: Path = None) -> Path:
        """Setup and return log directory path"""
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        
        log_dir = Path(log_dir)
        log_dir.mkdir(exist_ok=True)
        return log_dir
    
    @staticmethod
    def generate_log_filename(log_dir: Path) -> Path:
        """Generate timestamped log filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return log_dir / f"scraper_{timestamp}.log"
    
    @staticmethod
    def parse_log_level(level: str) -> int:
        """Parse string log level to logging constant"""
        return getattr(logging, level.upper())
