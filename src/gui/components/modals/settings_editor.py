"""
Settings editor modal for editing configuration files
"""
import json
import os
from .base_modal import BaseModal


class SettingsEditor(BaseModal):
    """Modal window for editing settings.json configuration"""
    
    def __init__(self, parent, logger=None):
        self.logger = logger
        super().__init__(parent, "Edit settings.json")
        self._load_settings()
    
    def _load_settings(self):
        """Load settings.json content"""
        # Correct path: config/settings.json
        settings_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "config",
            "settings.json"
        )
        
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings_data = f.read()
        except Exception as e:
            settings_data = "{}"
            if self.logger:
                self.logger.error(f"Could not load settings.json: {e}")
        
        self.settings_path = settings_path
        self.set_content(settings_data)
    
    def save_content(self):
        """Save settings content to file"""
        new_data = self.get_content()
        try:
            # Validate JSON
            parsed = json.loads(new_data)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=4)
            self.set_status("✅ Saved successfully.", "green")
            if self.logger:
                self.logger.info("settings.json saved.")
        except Exception as e:
            self.set_status(f"❌ Invalid JSON: {e}", "red")
            if self.logger:
                self.logger.error(f"Failed to save settings.json: {e}")
