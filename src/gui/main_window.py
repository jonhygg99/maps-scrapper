"""
Main GUI Window for Google Maps Scraper
Multi-threaded interface with modern CustomTkinter design
"""
import customtkinter as ctk
import queue
import asyncio
import webbrowser
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from src.gui.styles import COLORS, FONTS, get_button_style, apply_theme
from src.core.worker import WorkerPool
from src.core.config import Config
from src.scraper.google_maps import GoogleMapsScraper
from src.scraper.proxy_manager import ProxyManager
from src.utils.logger import Logger
from src.utils.data_processor import DataProcessor
from src.utils.exporter import DataExporter
from src.utils.notifier import Notifier
import json


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Google Maps Scraper Pro")
        self.geometry("1200x700")
        
        # Initialize logger
        self.logger = Logger.get_logger("MainWindow")
        
        # Set up UI log handler (queue-based for thread safety)
        Logger.add_ui_handler()
        self.log_queue = Logger.get_log_queue()
        
        # Data storage
        self.all_results = []
        self.worker_pool = None
        self.is_scraping = False
        self.active_workers = {}  # Track active workers {worker_id: task_name}
        self.completed_tasks = 0
        self.total_tasks = 0
        
        # Result checking
        self.result_check_job = None
        
        # Add menu bar for config/proxy editors
        self._create_menu()

        # Setup UI
        self._create_ui()
        
        # Start result checker and log processor
        self._check_results()
        self._process_log_queue()
        
        self.logger.info("Application started")
    
    def _create_menu(self):
        """Create a menu bar with config/proxy editors"""
        import tkinter as tk

        # CustomTkinter does not have a native menu, so use Tkinter's Menu
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        config_menu = tk.Menu(self.menu_bar, tearoff=0)
        config_menu.add_command(label="Edit Settings (settings.json)", command=self.open_settings_editor)
        config_menu.add_command(label="Edit Proxies (proxies.txt)", command=self.open_proxy_editor)
        self.menu_bar.add_cascade(label="Configuration", menu=config_menu)

    def _create_ui(self):
        """Create the user interface"""
        
        # Configure grid - 3 columns layout
        self.grid_columnconfigure(0, weight=1, minsize=320)  # Left: Input controls
        self.grid_columnconfigure(1, weight=1, minsize=280)  # Middle: Status & Threads
        self.grid_columnconfigure(2, weight=2, minsize=500)  # Right: Results (larger)
        self.grid_rowconfigure(0, weight=1)
        
        # Create three panels
        self._create_left_panel()
        self._create_middle_panel()
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create left panel with input controls"""
        
        left_frame = ctk.CTkFrame(self, corner_radius=10)
        left_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        # Configure grid weights
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(2, weight=1)  # Queries textbox expands
        
        # Title
        title_label = ctk.CTkLabel(
            left_frame,
            text="🗺️ Scraper",
            font=FONTS['heading']
        )
        title_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Search Queries Section
        queries_label = ctk.CTkLabel(
            left_frame,
            text="📝 Search Queries:",
            font=FONTS['subheading']
        )
        queries_label.grid(row=1, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.query_text = ctk.CTkTextbox(
            left_frame,
            font=FONTS['normal']
        )
        self.query_text.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        self.query_text.insert("1.0", "restaurants in New York\ncoffee shops in Los Angeles")
        
        # Settings Section
        settings_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
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
        self.threads_entry.insert(0, str(Config.get('max_threads', 3)))
        self.threads_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Checkboxes Section
        checkboxes_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
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
        button_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, padx=15, pady=(10, 15), sticky="ew")

        self.start_btn = ctk.CTkButton(
            button_frame,
            text="▶ Start",
            command=self.start_scraping,
            font=FONTS['normal'],
            height=40,
            **get_button_style('success')
        )
        self.start_btn.pack(fill="x", pady=2)

        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹ Stop",
            command=self.stop_scraping,
            font=FONTS['normal'],
            height=40,
            state="disabled",
            **get_button_style('danger')
        )
        self.stop_btn.pack(fill="x", pady=2)

        # NEW: Open Output Folder button
        self.open_output_btn = ctk.CTkButton(
            button_frame,
            text="📂 Open Output Folder",
            command=self.open_output_folder,
            font=FONTS['normal'],
            height=36,
            **get_button_style('primary')
        )
        self.open_output_btn.pack(fill="x", pady=2)

        # Donate Section
        donate_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
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
            command=self.open_donate_link,
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
    
    def _create_middle_panel(self):
        """Create middle panel with status and thread monitoring"""
        
        middle_frame = ctk.CTkFrame(self, corner_radius=10)
        middle_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        # Configure grid
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_rowconfigure(2, weight=1)  # Threads status
        middle_frame.grid_rowconfigure(4, weight=1)  # General status
        
        # Threads Status Section
        threads_label = ctk.CTkLabel(
            middle_frame,
            text="⚙️ Worker Threads",
            font=FONTS['heading']
        )
        threads_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(middle_frame)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        self.threads_text = ctk.CTkTextbox(
            middle_frame,
            font=FONTS['small']
        )
        self.threads_text.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        self._update_threads_status("No active threads")
        
        # Status Section
        status_label = ctk.CTkLabel(
            middle_frame,
            text="📋 Status Log",
            font=FONTS['heading']
        )
        status_label.grid(row=3, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.status_text = ctk.CTkTextbox(
            middle_frame,
            font=FONTS['small']
        )
        self.status_text.grid(row=4, column=0, padx=15, pady=(5, 15), sticky="nsew")
        self._add_status("Ready to start scraping...")
    
    def _create_right_panel(self):
        """Create right panel with results display"""
        
        right_frame = ctk.CTkFrame(self, corner_radius=10)
        right_frame.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
        
        # Configure grid
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)  # Results text expands
        
        # Results Header
        results_label = ctk.CTkLabel(
            right_frame,
            text="📊 Scraped Results",
            font=FONTS['heading']
        )
        results_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Results Display
        self.results_text = ctk.CTkTextbox(
            right_frame,
            font=FONTS['small'],
            wrap="word"
        )
        self.results_text.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        
        # Configure text tags for colored logging
        self._configure_log_colors()
        
        # Export Section
        export_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        export_frame.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")
        
        self.export_csv_btn = ctk.CTkButton(
            export_frame,
            text="📄 CSV",
            command=lambda: self.export_data('csv'),
            font=FONTS['normal'],
            height=35,
            **get_button_style('primary')
        )
        self.export_csv_btn.pack(side="left", padx=3, fill="x", expand=True)
        
        self.export_excel_btn = ctk.CTkButton(
            export_frame,
            text="📊 Excel",
            command=lambda: self.export_data('excel'),
            font=FONTS['normal'],
            height=35,
            **get_button_style('primary')
        )
        self.export_excel_btn.pack(side="left", padx=3, fill="x", expand=True)
        
        self.clear_btn = ctk.CTkButton(
            export_frame,
            text="🗑️ Clear",
            command=self.clear_results,
            font=FONTS['normal'],
            height=35,
            **get_button_style('warning')
        )
        self.clear_btn.pack(side="left", padx=3, fill="x", expand=True)
    
    def start_scraping(self):
        """Start the scraping process"""
        # Get queries
        queries_text = self.query_text.get("1.0", "end").strip()
        if not queries_text:
            self.logger.warning("⚠️ Please enter at least one search query")
            return
        
        queries = [q.strip() for q in queries_text.split("\n") if q.strip()]
        
        try:
            max_results = int(self.max_results_entry.get())
            num_threads = int(self.threads_entry.get())
        except ValueError:
            self.logger.error("⚠️ Invalid number format in settings")
            return
        
        # Update UI state
        self.is_scraping = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_bar.set(0)
        
        # Clear previous results
        self.all_results.clear()
        self.results_text.delete("1.0", "end")
        
        # Initialize tracking
        self.active_workers.clear()
        self.completed_tasks = 0
        self.total_tasks = len(queries)
        
        self.logger.info(f"🚀 Starting scraping for {len(queries)} queries")
        self.logger.info(f"📊 Settings: {max_results} results per query, {num_threads} threads")
        
        # Get settings (convert checkbox values to boolean)
        use_proxy = bool(self.use_proxy_var.get())
        headless = bool(self.headless_var.get())
        
        # Initialize proxy manager if needed
        proxy_manager = None
        if use_proxy:
            proxy_manager = ProxyManager()
            if not proxy_manager.has_proxies():
                self.logger.warning("⚠️ No proxies configured, continuing without proxies")
                use_proxy = False
        
        # Create worker pool
        self.worker_pool = WorkerPool(
            num_workers=num_threads,
            scraper_func=self._scrape_query,
            max_results=max_results,
            use_proxy=use_proxy,
            headless=headless,
            proxy_manager=proxy_manager
        )
        
        # Add tasks
        self.worker_pool.add_tasks(queries)
        
        # Start workers
        self.worker_pool.start()
        
        # Update thread status
        self._update_threads_status(f"Started {num_threads} worker threads\nInitializing...")
        
        self.logger.info(f"Started {num_threads} worker threads for {len(queries)} queries")
    
    async def _scrape_query(self, query: str, max_results: int, use_proxy: bool, 
                           headless: bool, proxy_manager=None):
        """
        Scrape a single query (runs in worker thread)
        
        Args:
            query: Search query
            max_results: Maximum results to scrape
            use_proxy: Whether to use proxy
            headless: Run browser in headless mode
            proxy_manager: Proxy manager instance
        """
        proxy = None
        if use_proxy and proxy_manager:
            proxy = proxy_manager.get_random_proxy()
        
        scraper = GoogleMapsScraper(
            headless=headless,
            proxy=proxy,
            timeout=Config.get('timeout', 30000)
        )
        
        try:
            await scraper.initialize()
            page = await scraper.create_page()
            
            await scraper.search_location(page, query)
            results = await scraper.extract_businesses(page, max_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error scraping '{query}': {e}")
            raise
            
        finally:
            await scraper.close()
    
    def _check_results(self):
        """Check for new results from worker pool (runs on main thread)"""
        if self.worker_pool:
            result = self.worker_pool.get_result(timeout=0.1)
            
            if result:
                status = result['status']
                task = result['task']
                worker_id = result.get('worker_id', 'unknown')
                
                if status == 'success':
                    results = result['result']
                    self.all_results.extend(results)
                    
                    # Mark worker as idle and task as completed
                    if worker_id in self.active_workers:
                        del self.active_workers[worker_id]
                    self.completed_tasks += 1
                    
                    # Log success (will appear in results_text via log handler)
                    self.logger.info(f"✅ {task}: {len(results)} results extracted")
                    
                    # Auto-save this task's results to separate CSV file if enabled
                    if self.auto_save_var.get() and results:
                        try:
                            import re
                            # Create safe filename from task name
                            safe_task_name = re.sub(r'[^\w\s-]', '', task).strip()
                            safe_task_name = re.sub(r'[-\s]+', '_', safe_task_name)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"{safe_task_name}_{timestamp}.csv"
                            
                            filepath = DataExporter.to_csv(results, filename=filename)
                            self.logger.info(f"💾 Saved {task} results to: {filename}")
                        except Exception as e:
                            self.logger.error(f"❌ Failed to save {task} results: {e}")
                    
                    # Update progress
                    if self.total_tasks > 0:
                        progress = self.completed_tasks / self.total_tasks
                        self.progress_bar.set(min(progress, 1.0))
                    
                else:
                    error = result.get('error', 'Unknown error')
                    
                    # Mark worker as idle
                    if worker_id in self.active_workers:
                        del self.active_workers[worker_id]
                    self.completed_tasks += 1
                    
                    # Log error (will appear in results_text via log handler)
                    self.logger.error(f"❌ {task}: {error}")
                    
                    # Send error notification for failed tasks
                    Notifier.notify_error(f"Task '{task}' failed: {str(error)[:80]}")
            
            # Update thread status
            self._update_threads_status_from_pool()
            
            # Check if all workers are done
            if not self.worker_pool.is_active() and self.worker_pool.tasks_pending() == 0:
                if self.is_scraping:
                    self._on_scraping_complete()
        
        # Schedule next check
        self.result_check_job = self.after(100, self._check_results)
    
    def _on_scraping_complete(self):
        """Called when scraping is complete"""
        self.is_scraping = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.progress_bar.set(1.0)
        
        # Stop and cleanup worker pool
        if self.worker_pool:
            self.worker_pool.stop(wait=True)
            self.worker_pool = None
        
        # Clear active workers
        self.active_workers.clear()
        
        # Update thread status
        self._update_threads_status(
            f"✅ All threads completed\n"
            f"📊 Processed: {self.completed_tasks}/{self.total_tasks} tasks\n"
            f"✅ Total results: {len(self.all_results)}"
        )
        
        # Process results
        if self.all_results:
            processor = DataProcessor()
            cleaned_results = processor.clean_results(self.all_results)
            cleaned_results = processor.remove_duplicates(cleaned_results)
            self.all_results = cleaned_results
            
            self.logger.info(f"🎉 Scraping complete! Total results: {len(self.all_results)}")
            
            # Send success notification
            Notifier.notify_complete(
                total_results=len(self.all_results),
                total_tasks=self.total_tasks
            )
            
            # Create combined CSV file if enabled
            if self.auto_save_var.get():
                try:
                    import os
                    import subprocess
                    import platform
                    
                    # Save combined results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    combined_filename = f"combined_all_results_{timestamp}.csv"
                    filepath = DataExporter.to_csv(self.all_results, filename=combined_filename)
                    self.logger.info(f"💾 Saved combined results to: {combined_filename}")
                    
                    # Open the combined CSV file with default application
                    try:
                        if platform.system() == 'Windows':
                            os.startfile(filepath)
                        elif platform.system() == 'Darwin':  # macOS
                            subprocess.run(['open', filepath])
                        else:  # Linux
                            subprocess.run(['xdg-open', filepath])
                        
                        self.logger.info(f"📂 Opened combined CSV file")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Could not open file automatically: {e}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Auto-save failed: {e}")
                    # Send error notification
                    Notifier.notify_error(f"Failed to save results: {str(e)[:100]}")
        else:
            self.logger.warning("⚠️ Scraping complete but no results found")
            # Send warning notification
            Notifier.notify_warning("Scraping complete but no results found")
        
        self.logger.info(f"Scraping finished. Total unique results: {len(self.all_results)}")
    
    def stop_scraping(self):
        """Stop the scraping process immediately"""
        if self.worker_pool:
            self.logger.info("🛑 Force stopping all workers...")
            
            # Force stop without waiting (kills threads immediately)
            self.worker_pool.stop(wait=False, force=True)
            self.worker_pool = None
        
        self.is_scraping = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # Clear active workers
        self.active_workers.clear()
        
        # Update thread status
        self._update_threads_status(
            f"⏹️ All threads force-stopped\n"
            f"📊 Completed: {self.completed_tasks}/{self.total_tasks} tasks\n"
            f"✅ Results collected: {len(self.all_results)}"
        )
        
        self.logger.info("⏹️ Scraping force-stopped by user")
        
        # Send notification
        Notifier.notify_warning(f"Scraping stopped - {self.completed_tasks}/{self.total_tasks} tasks completed")
    
    def open_donate_link(self):
        """Open donation link in browser"""
        try:
            # Load donation config
            import json
            config_path = Path(__file__).parent.parent.parent / 'config' / 'donation.json'
            
            if config_path.exists():
                with open(config_path, 'r') as f:
                    donation_config = json.load(f)
                
                # Check if donations are enabled
                if not donation_config.get('donation', {}).get('enabled', True):
                    return
                
                # Get platform and username
                platform = donation_config['donation'].get('platform', 'buymeacoffee')
                username = donation_config['donation'].get('username', 'yourusername')
                custom_url = donation_config['donation'].get('custom_url')
                
                # Build URL
                if custom_url:
                    donation_url = custom_url
                else:
                    url_template = donation_config['donation_platforms'].get(platform, '')
                    donation_url = url_template.format(username=username, custom_url=custom_url)
            else:
                # Fallback to default
                donation_url = 'https://buymeacoffee.com/yourusername'
            
            webbrowser.open(donation_url)
            self.logger.info("💖 Thank you for considering a donation!")
            
        except Exception as e:
            self.logger.error(f"Failed to open donation link: {e}")
    
    def export_data(self, format_type: str):
        """Export scraped data"""
        if not self.all_results:
            self.logger.warning("⚠️ No data to export")
            return
        
        try:
            if format_type == 'csv':
                filepath = DataExporter.to_csv(self.all_results)
                self.logger.info(f"✅ Exported to CSV: {filepath}")
            elif format_type == 'excel':
                filepath = DataExporter.to_excel(self.all_results)
                self.logger.info(f"✅ Exported to Excel: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Export failed: {str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        self.all_results.clear()
        self.results_text.delete("1.0", "end")
        self.progress_bar.set(0)
        self.logger.info("🗑️ Results cleared")
    
    def _add_status(self, message: str):
        """Add message to status box"""
        self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")
    
    def _update_threads_status(self, message: str):
        """Update threads status box"""
        self.threads_text.delete("1.0", "end")
        self.threads_text.insert("1.0", message)
    
    def _update_threads_status_from_pool(self):
        """Update thread status from worker pool"""
        if not self.worker_pool:
            self._update_threads_status("⭕ No active threads")
            return
        
        try:
            # Get worker pool statistics
            alive_workers = [w for w in self.worker_pool.workers if w.is_alive()]
            total_workers = len(self.worker_pool.workers)
            pending_tasks = self.worker_pool.tasks_pending()
            
            # Build status message
            status_lines = []
            
            # Header with summary
            status_lines.append(f"🔧 Workers: {len(alive_workers)}/{total_workers} active")
            status_lines.append(f"📋 Tasks: {self.completed_tasks}/{self.total_tasks} completed")
            status_lines.append(f"⏳ Pending: {pending_tasks}")
            status_lines.append(f"✅ Results: {len(self.all_results)}")
            
            # Individual worker status
            if alive_workers:
                status_lines.append("\n--- Worker Details ---")
                for worker in alive_workers:
                    worker_id = worker.worker_id
                    if worker_id in self.active_workers:
                        task_name = self.active_workers[worker_id]
                        # Truncate long task names
                        if len(task_name) > 30:
                            task_name = task_name[:27] + "..."
                        status_lines.append(f"Worker {worker_id}: 🔄 {task_name}")
                    else:
                        status_lines.append(f"Worker {worker_id}: ⏸️ Idle")
            
            self._update_threads_status("\n".join(status_lines))
            
        except Exception as e:
            self._update_threads_status(f"❌ Status error: {e}")
    
    def _add_result(self, message: str):
        """Add message to results box"""
        self.results_text.insert("end", f"{message}\n")
        self.results_text.see("end")
    
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
    
    def _add_colored_result(self, message: str, level: str):
        """
        Add colored message to results box based on log level
        
        Args:
            message: Message to display
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
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
    
    def _process_log_queue(self):
        """
        Process log messages from the queue (runs on main thread)
        This is called periodically to safely update UI from worker threads
        """
        try:
            # Process up to 100 messages per call to avoid UI blocking
            for _ in range(100):
                try:
                    log_msg = self.log_queue.get_nowait()
                    level = log_msg['level']
                    message = log_msg['message']
                    
                    # Map log levels to emoji icons
                    level_icons = {
                        'DEBUG': '🔍',
                        'INFO': 'ℹ️',
                        'WARNING': '⚠️',
                        'ERROR': '❌',
                        'CRITICAL': '🔥'
                    }
                    
                    icon = level_icons.get(level, 'ℹ️')
                    formatted_message = f"{icon} {message}"
                    
                    # Add to results text with color
                    self._add_colored_result(formatted_message, level)
                    
                except:
                    # Queue is empty, break the loop
                    break
        except Exception as e:
            # Silently ignore errors during shutdown
            pass
        
        # Schedule next check (every 100ms)
        try:
            self.after(100, self._process_log_queue)
        except:
            # Window is closing
            pass
    
    def _handle_log_message(self, level: str, message: str):
        """
        DEPRECATED: This method is no longer used.
        Log messages now go through queue-based processing.
        Kept for compatibility.
        """
        pass
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_scraping:
            self.stop_scraping()
        
        if self.result_check_job:
            self.after_cancel(self.result_check_job)
        
        # Remove UI log handler
        Logger.remove_ui_handler()
        
        self.logger.info("Application closing")
        self.destroy()
    
    def open_settings_editor(self):
        """Open a modal to edit and save settings.json"""
        import os

        # Correct path: config/settings.json
        settings_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "settings.json"
        )

        # Modal window
        modal = ctk.CTkToplevel(self)
        modal.title("Edit settings.json")
        modal.geometry("600x500")
        modal.grab_set()

        # Load settings.json
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings_data = f.read()
        except Exception as e:
            settings_data = "{}"
            self.logger.error(f"Could not load settings.json: {e}")

        # Textbox for editing
        textbox = ctk.CTkTextbox(modal, font=FONTS['normal'])
        textbox.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        textbox.insert("1.0", settings_data)

        status_label = ctk.CTkLabel(modal, text="", text_color="red", font=FONTS['small'])
        status_label.pack(pady=(0, 8))

        def save_settings():
            new_data = textbox.get("1.0", "end").strip()
            try:
                # Validate JSON
                parsed = json.loads(new_data)
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=4)
                status_label.configure(text="✅ Saved successfully.", text_color="green")
                self.logger.info("settings.json saved.")
            except Exception as e:
                status_label.configure(text=f"❌ Invalid JSON: {e}", text_color="red")
                self.logger.error(f"Failed to save settings.json: {e}")

        save_btn = ctk.CTkButton(
            modal, text="💾 Save", command=save_settings, font=FONTS['normal'], height=36, **get_button_style('success')
        )
        save_btn.pack(pady=(0, 16))

    def open_proxy_editor(self):
        """Open a modal to edit and save proxies.txt"""
        import os

        # Typical proxy file location: config/proxies.txt
        proxy_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "config",
            "proxies.txt"
        )

        modal = ctk.CTkToplevel(self)
        modal.title("Edit proxies.txt")
        modal.geometry("600x500")
        modal.grab_set()

        try:
            with open(proxy_path, "r", encoding="utf-8") as f:
                proxy_data = f.read()
        except Exception as e:
            proxy_data = ""
            self.logger.error(f"Could not load proxies.txt: {e}")

        textbox = ctk.CTkTextbox(modal, font=FONTS['normal'])
        textbox.pack(fill="both", expand=True, padx=16, pady=(16, 8))
        textbox.insert("1.0", proxy_data)

        status_label = ctk.CTkLabel(modal, text="", text_color="red", font=FONTS['small'])
        status_label.pack(pady=(0, 8))

        def save_proxies():
            new_data = textbox.get("1.0", "end").strip()
            try:
                with open(proxy_path, "w", encoding="utf-8") as f:
                    f.write(new_data)
                status_label.configure(text="✅ Saved successfully.", text_color="green")
                self.logger.info("proxies.txt saved.")
            except Exception as e:
                status_label.configure(text=f"❌ Failed to save: {e}", text_color="red")
                self.logger.error(f"Failed to save proxies.txt: {e}")

        save_btn = ctk.CTkButton(
            modal, text="💾 Save", command=save_proxies, font=FONTS['normal'], height=36, **get_button_style('success')
        )
        save_btn.pack(pady=(0, 16))

    def open_output_folder(self):
        """Open the output/results folder in the system file explorer"""
        import os
        import platform
        import subprocess

        # You may want to adjust this path if your output folder is elsewhere
        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "output"
        )
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        try:
            if platform.system() == 'Windows':
                os.startfile(output_dir)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', output_dir])
            else:
                subprocess.run(['xdg-open', output_dir])
            self.logger.info(f"Opened output folder: {output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to open output folder: {e}")
