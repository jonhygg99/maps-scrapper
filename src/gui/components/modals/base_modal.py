"""
Base modal class for reusable modal windows
"""
import customtkinter as ctk
from src.gui.styles import FONTS, get_button_style


class BaseModal(ctk.CTkToplevel):
    """Base modal window with common functionality"""
    
    def __init__(self, parent, title, size="600x500", **kwargs):
        super().__init__(parent, **kwargs)
        self.title(title)
        self.geometry(size)
        self.grab_set()
        
        self.parent = parent
        self.status_label = None
        self.textbox = None
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the base modal UI structure"""
        self.textbox = ctk.CTkTextbox(self, font=FONTS['normal'])
        self.textbox.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        
        self.status_label = ctk.CTkLabel(self, text="", text_color="red", font=FONTS['small'])
        self.status_label.pack(pady=(0, 8))
        
        save_btn = ctk.CTkButton(
            self, 
            text="💾 Save", 
            command=self.save_content, 
            font=FONTS['normal'], 
            height=36, 
            **get_button_style('success')
        )
        save_btn.pack(pady=(0, 16))
    
    def save_content(self):
        """Override this method in subclasses"""
        pass
    
    def set_content(self, content):
        """Set the textbox content"""
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)
    
    def get_content(self):
        """Get the textbox content"""
        return self.textbox.get("1.0", "end").strip()
    
    def set_status(self, message, color="red"):
        """Set the status label message"""
        self.status_label.configure(text=message, text_color=color)
