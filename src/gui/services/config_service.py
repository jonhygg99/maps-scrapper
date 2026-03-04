"""
Configuration management service
"""
import json
import webbrowser
from pathlib import Path
from src.gui.constants.ui_constants import (
    DEFAULT_DONATION_URL, DEFAULT_DONATION_PLATFORM, DEFAULT_DONATION_USERNAME
)
from src.gui.constants.scraping_constants import (
    DONATION_CONFIG_FILE, SETTINGS_CONFIG_FILE, PROXIES_CONFIG_FILE
)
from src.gui.utils.file_operations import get_config_directory


class ConfigService:
    """Manages configuration operations"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def open_donation_link(self):
        """Open donation link in browser"""
        try:
            config_path = get_config_directory() / DONATION_CONFIG_FILE
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    donation_config = json.load(f)
                
                # Check if donations are enabled
                if not donation_config.get('donation', {}).get('enabled', True):
                    return
                
                # Get platform and username
                platform = donation_config['donation'].get('platform', DEFAULT_DONATION_PLATFORM)
                username = donation_config['donation'].get('username', DEFAULT_DONATION_USERNAME)
                custom_url = donation_config['donation'].get('custom_url')
                
                # Build URL
                if custom_url:
                    donation_url = custom_url
                else:
                    url_template = donation_config['donation_platforms'].get(platform, '')
                    donation_url = url_template.format(username=username, custom_url=custom_url)
            else:
                # Fallback to default
                donation_url = DEFAULT_DONATION_URL
            
            webbrowser.open(donation_url)
            self.logger.info("💖 Thank you for considering a donation!")
            
        except Exception as e:
            self.logger.error(f"Failed to open donation link: {e}")
    
    def get_settings_file_path(self):
        """Get settings configuration file path"""
        return get_config_directory() / SETTINGS_CONFIG_FILE
    
    def get_proxies_file_path(self):
        """Get proxies configuration file path"""
        return get_config_directory() / PROXIES_CONFIG_FILE
    
    def get_donation_config_path(self):
        """Get donation configuration file path"""
        return get_config_directory() / DONATION_CONFIG_FILE
