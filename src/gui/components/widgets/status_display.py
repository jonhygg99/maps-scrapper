"""
Status display widget for showing thread and worker status
"""
import customtkinter as ctk
from src.gui.styles import FONTS


class StatusDisplay(ctk.CTkTextbox):
    """Widget for displaying status messages with formatting"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, font=FONTS['small'], **kwargs)
        self._configure_tags()
    
    def _configure_tags(self):
        """Configure color tags for different message types"""
        text_widget = self._textbox
        text_widget.tag_config("INFO", foreground="#4A9EFF")
        text_widget.tag_config("SUCCESS", foreground="#2ECC71")
        text_widget.tag_config("WARNING", foreground="#F39C12")
        text_widget.tag_config("ERROR", foreground="#E74C3C")
        text_widget.tag_config("DEBUG", foreground="#808080")
    
    def add_message(self, message, level="INFO"):
        """Add a colored message to the display"""
        text_widget = self._textbox
        
        # Determine tag based on level and content
        tag = level
        if "✅" in message or "complete" in message.lower():
            tag = "SUCCESS"
        elif "❌" in message or "error" in message.lower():
            tag = "ERROR"
        elif "⚠️" in message or "warning" in message.lower():
            tag = "WARNING"
        
        text_widget.insert("end", f"{message}\n", tag)
        text_widget.see("end")
    
    def clear(self):
        """Clear all messages"""
        self.delete("1.0", "end")
    
    def set_text(self, text):
        """Set the entire text content"""
        self.delete("1.0", "end")
        self.insert("1.0", text)
