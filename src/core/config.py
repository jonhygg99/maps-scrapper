"""
Configuration Manager for Google Maps Scraper
Handles loading and saving application settings
"""
import json
from pathlib import Path
from typing import List, Dict, Any
import os
from dotenv import load_dotenv


class Config:
    """Centralized configuration management"""
    
    # Path setup
    BASE_DIR = Path(__file__).parent.parent.parent
    CONFIG_DIR = BASE_DIR / "config"
    CONFIG_FILE = CONFIG_DIR / "settings.json"
    PROXY_FILE = CONFIG_DIR / "proxies.txt"
    OUTPUT_DIR = BASE_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Default settings
    _settings = {
        "max_threads": 3,
        "request_delay_min": 2,
        "request_delay_max": 5,
        "use_proxy": False,
        "headless": True,
        "timeout": 30000,
        "max_results_per_query": 20,
        "scroll_pause_time": 2,
        "user_agent_rotation": True,
        "viewport_width": 1920,
        "viewport_height": 1080,
        "export_format": "csv"
    }
    
    @classmethod
    def initialize(cls):
        """Initialize configuration and create necessary directories"""
        # Load environment variables
        load_dotenv(cls.BASE_DIR / ".env")
        
        # Create directories if they don't exist
        cls.CONFIG_DIR.mkdir(exist_ok=True)
        cls.OUTPUT_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        
        # Load settings from file
        cls.load()
    
    @classmethod
    def load(cls):
        """Load settings from JSON file"""
        if cls.CONFIG_FILE.exists():
            try:
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    cls._settings.update(loaded_settings)
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            # Create default config file
            cls.save()
    
    @classmethod
    def save(cls):
        """Save current settings to JSON file"""
        try:
            cls.CONFIG_DIR.mkdir(exist_ok=True)
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(cls._settings, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    @classmethod
    def get(cls, key: str, default=None) -> Any:
        """Get a configuration value"""
        return cls._settings.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any):
        """Set a configuration value"""
        cls._settings[key] = value
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all settings"""
        return cls._settings.copy()
    
    @classmethod
    def update(cls, settings: Dict[str, Any]):
        """Update multiple settings at once"""
        cls._settings.update(settings)
    
    @classmethod
    def get_proxies(cls) -> List[str]:
        """Load proxies from file"""
        if not cls.PROXY_FILE.exists():
            return []
        
        try:
            with open(cls.PROXY_FILE, 'r', encoding='utf-8') as f:
                proxies = [
                    line.strip() 
                    for line in f.readlines() 
                    if line.strip() and not line.strip().startswith('#')
                ]
                return proxies
        except Exception as e:
            print(f"Error loading proxies: {e}")
            return []
    
    @classmethod
    def get_env(cls, key: str, default: str = "") -> str:
        """Get environment variable"""
        return os.getenv(key, default)
    
    @classmethod
    def is_debug(cls) -> bool:
        """Check if debug mode is enabled"""
        return cls.get_env("DEBUG", "False").lower() == "true"
