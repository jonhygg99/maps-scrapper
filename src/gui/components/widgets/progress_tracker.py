"""
Progress tracking widget for monitoring scraping progress
"""
import customtkinter as ctk
from src.gui.styles import FONTS


class ProgressTracker(ctk.CTkFrame):
    """Widget for tracking progress with progress bar and statistics"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._create_ui()
    
    def _create_ui(self):
        """Create the progress tracker UI"""
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=15, pady=5)
        self.progress_bar.set(0)
        
        # Statistics label
        self.stats_label = ctk.CTkLabel(self, text="", font=FONTS['small'])
        self.stats_label.pack(pady=5)
    
    def update_progress(self, completed, total):
        """Update progress bar and statistics"""
        if total > 0:
            progress = completed / total
            self.progress_bar.set(min(progress, 1.0))
            self.stats_label.configure(text=f"{completed}/{total} tasks completed")
        else:
            self.progress_bar.set(0)
            self.stats_label.configure(text="No tasks")
    
    def reset(self):
        """Reset progress tracker"""
        self.progress_bar.set(0)
        self.stats_label.configure(text="")
    
    def set_progress_value(self, value):
        """Set progress bar value directly (0.0 to 1.0)"""
        self.progress_bar.set(min(max(value, 0.0), 1.0))
