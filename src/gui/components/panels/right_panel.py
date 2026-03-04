"""
Right panel component containing results display and export controls
"""
import customtkinter as ctk
from src.gui.styles import FONTS, get_button_style


class RightPanel(ctk.CTkFrame):
    """Right panel with results display and export functionality"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        self._create_ui()
    
    def _create_ui(self):
        """Create the right panel user interface"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Results text expands
        
        # Results Header
        results_label = ctk.CTkLabel(
            self,
            text="📊 Scraped Results",
            font=FONTS['heading']
        )
        results_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Results Display
        self.results_text = ctk.CTkTextbox(
            self,
            font=FONTS['small'],
            wrap="word"
        )
        self.results_text.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        
        # Configure text tags for colored logging
        self._configure_log_colors()
        
        # Export Section
        export_frame = ctk.CTkFrame(self, fg_color="transparent")
        export_frame.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")
        
        self.export_csv_btn = ctk.CTkButton(
            export_frame,
            text="📄 CSV",
            font=FONTS['normal'],
            height=35,
            **get_button_style('primary')
        )
        self.export_csv_btn.pack(side="left", padx=3, fill="x", expand=True)
        
        self.export_excel_btn = ctk.CTkButton(
            export_frame,
            text="📊 Excel",
            font=FONTS['normal'],
            height=35,
            **get_button_style('primary')
        )
        self.export_excel_btn.pack(side="left", padx=3, fill="x", expand=True)
        
        self.clear_btn = ctk.CTkButton(
            export_frame,
            text="🗑️ Clear",
            font=FONTS['normal'],
            height=35,
            **get_button_style('warning')
        )
        self.clear_btn.pack(side="left", padx=3, fill="x", expand=True)
    
    def _configure_log_colors(self):
        """Configure color tags for different log levels"""
        # Get the underlying text widget
        text_widget = self.results_text._textbox
        
        # Define colors for each log level
        text_widget.tag_config("DEBUG", foreground="#808080")      # Gray
        text_widget.tag_config("INFO", foreground="#4A9EFF")       # Blue
        text_widget.tag_config("SUCCESS", foreground="#2ECC71")    # Green
        text_widget.tag_config("WARNING", foreground="#F39C12")    # Orange
        text_widget.tag_config("ERROR", foreground="#E74C3C")      # Red
        text_widget.tag_config("CRITICAL", foreground="#C0392B")   # Dark Red
    
    def add_colored_result(self, message, level):
        """Add colored message to results box based on log level"""
        # Get the underlying text widget
        text_widget = self.results_text._textbox
        
        # Determine tag based on level and message content
        tag = level
        
        # Special handling for success messages (contains ✅)
        if "✅" in message or "complete" in message.lower() or "success" in message.lower():
            tag = "SUCCESS"
        
        # Insert with color tag
        text_widget.insert("end", f"{message}\n", tag)
        text_widget.see("end")
    
    def clear_results(self):
        """Clear all results from the display"""
        self.results_text.delete("1.0", "end")
    
    def add_result(self, message):
        """Add message to results box"""
        self.results_text.insert("end", f"{message}\n")
        self.results_text.see("end")
