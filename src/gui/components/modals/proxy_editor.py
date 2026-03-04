"""
Proxy editor modal for editing proxy configuration
"""
import os
from .base_modal import BaseModal


class ProxyEditor(BaseModal):
    """Modal window for editing proxies.txt configuration"""
    
    def __init__(self, parent, logger=None):
        self.logger = logger
        super().__init__(parent, "Edit proxies.txt")
        self._load_proxies()
    
    def _load_proxies(self):
        """Load proxies.txt content"""
        # Typical proxy file location: config/proxies.txt
        proxy_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "config",
            "proxies.txt"
        )
        
        try:
            with open(proxy_path, "r", encoding="utf-8") as f:
                proxy_data = f.read()
        except Exception as e:
            proxy_data = ""
            if self.logger:
                self.logger.error(f"Could not load proxies.txt: {e}")
        
        self.proxy_path = proxy_path
        self.set_content(proxy_data)
    
    def save_content(self):
        """Save proxy content to file"""
        new_data = self.get_content()
        try:
            with open(self.proxy_path, "w", encoding="utf-8") as f:
                f.write(new_data)
            self.set_status("✅ Saved successfully.", "green")
            if self.logger:
                self.logger.info("proxies.txt saved.")
        except Exception as e:
            self.set_status(f"❌ Failed to save: {e}", "red")
            if self.logger:
                self.logger.error(f"Failed to save proxies.txt: {e}")
