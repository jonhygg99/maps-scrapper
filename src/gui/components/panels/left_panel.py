"""
Left panel component containing input controls and settings
"""
import customtkinter as ctk
from src.gui.styles import COLORS, FONTS, get_button_style


class LeftPanel(ctk.CTkFrame):
    """Left panel with scraper input controls and settings"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        self._create_ui()
    
    def _create_ui(self):
        """Create the left panel user interface"""
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Queries textbox expands
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="🗺️ Scraper",
            font=FONTS['heading']
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Search Queries Section
        queries_label = ctk.CTkLabel(
            self,
            text="📝 Search Queries:",
            font=FONTS['subheading']
        )
        queries_label.grid(row=1, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.query_text = ctk.CTkTextbox(
            self,
            font=FONTS['normal']
        )
        self.query_text.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        self.query_text.insert("1.0", "restaurants in New York\ncoffee shops in Los Angeles")
        
        # Settings Section
        settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        settings_frame.grid(row=3, column=0, padx=15, pady=10, sticky="ew")
        
        # Max Results
        max_results_label = ctk.CTkLabel(settings_frame, text="Max Results:", font=FONTS['normal'])
        max_results_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.max_results_entry = ctk.CTkEntry(settings_frame, width=80)
        self.max_results_entry.insert(0, "20")
        self.max_results_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Number of Threads
        threads_label = ctk.CTkLabel(settings_frame, text="Threads:", font=FONTS['normal'])
        threads_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.threads_entry = ctk.CTkEntry(settings_frame, width=80)
        self.threads_entry.insert(0, "3")
        self.threads_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Checkboxes Section
        checkboxes_frame = ctk.CTkFrame(self, fg_color="transparent")
        checkboxes_frame.grid(row=4, column=0, padx=15, pady=5, sticky="ew")
        
        self.use_proxy_var = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Use Proxies",
            font=FONTS['small']
        )
        self.use_proxy_var.grid(row=0, column=0, sticky="w", pady=2)
        
        self.headless_var = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Headless Mode",
            font=FONTS['small']
        )
        self.headless_var.grid(row=1, column=0, sticky="w", pady=2)
        self.headless_var.select()
        
        self.auto_save_var = ctk.CTkCheckBox(
            checkboxes_frame,
            text="Auto-save CSV",
            font=FONTS['small']
        )
        self.auto_save_var.grid(row=2, column=0, sticky="w", pady=2)
        self.auto_save_var.select()
        
        # Control Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=5, column=0, padx=15, pady=(10, 15), sticky="ew")

        self.start_btn = ctk.CTkButton(
            button_frame,
            text="▶ Start",
            font=FONTS['normal'],
            height=40,
            **get_button_style('success')
        )
        self.start_btn.pack(fill="x", pady=2)

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹ Stop",
            font=FONTS['normal'],
            height=40,
            state="disabled",
            **get_button_style('danger')
        )
        self.stop_btn.pack(fill="x", pady=2)

        self.open_output_btn = ctk.CTkButton(
            button_frame,
            text="📂 Open Output Folder",
            font=FONTS['normal'],
            height=36,
            **get_button_style('primary')
        )
        self.open_output_btn.pack(fill="x", pady=2)

        # Donate Section
        donate_frame = ctk.CTkFrame(self, fg_color="transparent")
        donate_frame.grid(row=6, column=0, padx=15, pady=(5, 10), sticky="ew")
        
        # Separator line
        separator = ctk.CTkFrame(donate_frame, height=1, fg_color=COLORS['border'])
        separator.pack(fill="x", pady=(0, 8))
        
        # Donate message
        donate_label = ctk.CTkLabel(
            donate_frame,
            text="💖 Enjoying this tool?",
            font=FONTS['small'],
            text_color=COLORS['text_secondary']
        )
        donate_label.pack(pady=(0, 5))
        
        # Donate button with gradient effect
        self.donate_btn = ctk.CTkButton(
            donate_frame,
            text="💙 Make A donation",
            font=("Segoe UI", 13, "bold"),
            height=36,
            fg_color=("#0070BA", "#003087"),  # PayPal blue gradient
            hover_color=("#005EA6", "#002C5F"),
            corner_radius=20,  # More rounded like PayPal buttons
            border_width=0
        )
        self.donate_btn.pack(fill="x", pady=2)
        
        # Thank you message (small)
        thank_label = ctk.CTkLabel(
            donate_frame,
            text="Your support helps keep this project alive! 🚀",
            font=("Segoe UI", 9),
            text_color=COLORS['text_secondary'],
            wraplength=250
        )
        thank_label.pack(pady=(3, 0))
    
    def get_queries(self):
        """Get search queries from textbox"""
        queries_text = self.query_text.get("1.0", "end").strip()
        return [q.strip() for q in queries_text.split("\n") if q.strip()]
    
    def get_max_results(self):
        """Get max results setting"""
        try:
            return int(self.max_results_entry.get())
        except ValueError:
            return 20
    
    def get_threads(self):
        """Get number of threads setting"""
        try:
            return int(self.threads_entry.get())
        except ValueError:
            return 3
    
    def get_use_proxy(self):
        """Get proxy setting"""
        return bool(self.use_proxy_var.get())
    
    def get_headless(self):
        """Get headless mode setting"""
        return bool(self.headless_var.get())
    
    def get_auto_save(self):
        """Get auto-save setting"""
        return bool(self.auto_save_var.get())
    
    def set_scraping_state(self, is_scraping):
        """Update button states based on scraping status"""
        if is_scraping:
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
