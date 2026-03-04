"""
Google Maps Scraper - Main Entry Point
Advanced web scraper with GUI, multi-threading, and anti-detection
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow
from src.gui.styles import apply_theme
from src.core.config import Config
from src.utils.logger import Logger


def main():
    """Main application entry point"""
    
    # Initialize configuration
    Config.initialize()
    
    # Initialize logging
    Logger.initialize(level=Config.get_env("LOG_LEVEL", "INFO"))
    logger = Logger.get_logger("Main")
    
    logger.info("=" * 50)
    logger.info("Google Maps Scraper Started")
    logger.info("=" * 50)
    
    # Set Playwright browser path if running from bundled executable
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        import os
        bundle_dir = sys._MEIPASS
        browsers_path = os.path.join(bundle_dir, 'playwright_browsers')
        # Set environment variable to point to the bundled browsers directory
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_path
        logger.info(f"Using bundled Chromium browser at: {browsers_path}")
    
    try:
        # Apply GUI theme
        apply_theme()
        
        # Create and run application
        app = MainWindow()
        
        # Set closing protocol
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start application
        app.mainloop()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Application closed")


if __name__ == "__main__":
    main()
