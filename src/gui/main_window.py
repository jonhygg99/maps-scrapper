"""
Main GUI Window for Google Maps Scraper - Optimized Version
Multi-threaded interface with modern CustomTkinter design
"""
import customtkinter as ctk
import queue
from src.utils.logging import Logger

# Import constants
from src.gui.constants.ui_constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    GRID_WEIGHT_LEFT, GRID_WEIGHT_MIDDLE, GRID_WEIGHT_RIGHT,
    GRID_MINSIZE_LEFT, GRID_MINSIZE_MIDDLE, GRID_MINSIZE_RIGHT,
    RESULT_CHECK_INTERVAL, MAX_LOG_MESSAGES_PER_CALL,
    BUTTON_START, BUTTON_STOP, BUTTON_EXPORT_CSV, BUTTON_EXPORT_EXCEL, BUTTON_CLEAR,
    MENU_CONFIGURATION, MENU_EDIT_SETTINGS, MENU_EDIT_PROXIES,
    ERROR_NO_QUERIES, ERROR_INVALID_FORMAT,
    LOG_ICONS, STATUS_READY
)

# Import state management
from src.gui.state.application_state import ApplicationState
from src.gui.state.scraping_state import ScrapingState

# Import services
from src.gui.services.scraping_service import ScrapingService
from src.gui.services.export_service import ExportService
from src.gui.services.config_service import ConfigService

# Import components
from src.gui.components.panels.left_panel import LeftPanel
from src.gui.components.panels.middle_panel import MiddlePanel
from src.gui.components.panels.right_panel import RightPanel
from src.gui.components.modals.settings_editor import SettingsEditor
from src.gui.components.modals.proxy_editor import ProxyEditor

# Import utilities
from src.gui.utils.file_operations import open_directory_with_explorer
from src.gui.utils.notification_manager import NotificationManager


class MainWindow(ctk.CTk):
    """Main application window - optimized orchestrator"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize state management
        self.app_state = ApplicationState()
        self.scraping_state = ScrapingState()
        
        # Initialize services
        self.logger = Logger.get_logger("MainWindow")
        self.scraping_service = ScrapingService(self.logger)
        self.export_service = ExportService(self.logger)
        self.config_service = ConfigService(self.logger)
        
        # Setup window
        self._setup_window()
        self._setup_logging()
        self._create_menu()
        self._create_ui()
        self._start_background_tasks()
        
        self.logger.info("Application started")
    
    def _setup_window(self):
        """Configure window properties"""
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    def _setup_logging(self):
        """Initialize logging system"""
        Logger.add_ui_handler()
        self.app_state.set_log_queue(Logger.get_log_queue())
    
    def _create_menu(self):
        """Create menu bar with configuration options"""
        import tkinter as tk
        
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        
        config_menu = tk.Menu(menu_bar, tearoff=0)
        config_menu.add_command(label=MENU_EDIT_SETTINGS, command=self.open_settings_editor)
        config_menu.add_command(label=MENU_EDIT_PROXIES, command=self.open_proxy_editor)
        menu_bar.add_cascade(label=MENU_CONFIGURATION, menu=config_menu)
    
    def _create_ui(self):
        """Create user interface using components"""
        # Configure grid layout
        self.grid_columnconfigure(0, weight=GRID_WEIGHT_LEFT, minsize=GRID_MINSIZE_LEFT)
        self.grid_columnconfigure(1, weight=GRID_WEIGHT_MIDDLE, minsize=GRID_MINSIZE_MIDDLE)
        self.grid_columnconfigure(2, weight=GRID_WEIGHT_RIGHT, minsize=GRID_MINSIZE_RIGHT)
        self.grid_rowconfigure(0, weight=1)
        
        # Create panels
        self._create_panels()
        self._connect_callbacks()
    
    def _create_panels(self):
        """Create and layout all panels"""
        self.left_panel = LeftPanel(self)
        self.left_panel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        self.middle_panel = MiddlePanel(self)
        self.middle_panel.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        self.right_panel = RightPanel(self)
        self.right_panel.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
    
    def _connect_callbacks(self):
        """Connect all button callbacks to methods"""
        self.left_panel.start_btn.configure(command=self._start_scraping_wrapper)
        self.left_panel.stop_btn.configure(command=self.stop_scraping)
        self.left_panel.open_output_btn.configure(command=self.open_output_folder)
        self.left_panel.donate_btn.configure(command=self.open_donate_link)
        
        self.right_panel.export_csv_btn.configure(command=lambda: self.export_data('csv'))
        self.right_panel.export_excel_btn.configure(command=lambda: self.export_data('excel'))
        self.right_panel.clear_btn.configure(command=self.clear_results)
    
    def _start_scraping_wrapper(self):
        """Async wrapper for start_scraping button callback"""
        import asyncio
        try:
            # Create new event loop if needed
            loop = asyncio.get_event_loop()
            if loop is None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async method
            loop.run_until_complete(self.start_scraping())
        except Exception as e:
            self.logger.error(f"Failed to start scraping: {e}")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        self._check_results()
        self._process_log_queue()
    
    async def start_scraping(self):
        """Start the scraping process"""
        # Get user input
        queries = self.left_panel.get_queries()
        if not queries:
            self.logger.warning(ERROR_NO_QUERIES)
            return
        
        try:
            max_results = self.left_panel.get_max_results()
            num_threads = self.left_panel.get_threads()
        except ValueError:
            self.logger.error(ERROR_INVALID_FORMAT)
            return
        
        # Update state and UI
        self.app_state.set_scraping_state(True)
        self.scraping_state.initialize_scraping(len(queries))
        self.left_panel.set_scraping_state(True)
        self.middle_panel.reset_progress()
        self._clear_results_display()
        
        # Start scraping service
        use_proxy = self.left_panel.get_use_proxy()
        headless = self.left_panel.get_headless()
        
        # Await the async scraping service
        await self.scraping_service.start_scraping(
            queries, max_results, num_threads, use_proxy, headless
        )
        
        # Update UI
        self._update_ui_for_scraping_start(num_threads, queries)
        
        self.logger.info(f"🚀 Started {num_threads} workers for {len(queries)} queries")
    
    def stop_scraping(self):
        """Stop the scraping process"""
        self.scraping_service.stop_scraping()
        self.app_state.set_scraping_state(False)
        self.left_panel.set_scraping_state(False)
        
        # Update UI
        self._update_ui_for_scraping_stop()
        
        self.logger.info("⏹️ Scraping force-stopped by user")
        NotificationManager.notify_scraping_stopped(
            self.scraping_state.get_completed_tasks(),
            self.scraping_state.get_total_tasks()
        )
    
    def export_data(self, format_type):
        """Export scraped data"""
        results = self.app_state.get_results()
        self.export_service.export_data(results, format_type)
    
    def clear_results(self):
        """Clear all results"""
        self.app_state.clear_results()
        self.right_panel.clear_results()
        self.middle_panel.reset_progress()
        self.logger.info("🗑️ Results cleared")
    
    def open_settings_editor(self):
        """Open settings editor modal"""
        SettingsEditor(self, self.logger)
    
    def open_proxy_editor(self):
        """Open proxy editor modal"""
        ProxyEditor(self, self.logger)
    
    def open_output_folder(self):
        """Open output folder in system explorer"""
        from src.gui.utils.file_operations import get_output_directory
        output_dir = get_output_directory()
        open_directory_with_explorer(output_dir)
        self.logger.info(f"Opened output folder: {output_dir}")
    
    def open_donate_link(self):
        """Open donation link in browser"""
        self.config_service.open_donation_link()
    
    def _check_results(self):
        """Check for new results from worker pool"""
        result = self.scraping_service.check_results()
        
        if result:
            processed_result = self.scraping_service.process_result(
                result, self.left_panel.get_auto_save()
            )
            
            if processed_result:
                self.app_state.add_results(processed_result)
                self._update_progress()
                self._update_thread_status()
        
        # Check completion
        if self._is_scraping_complete():
            self._on_scraping_complete()
        
        # Schedule next check
        job = self.after(RESULT_CHECK_INTERVAL, self._check_results)
        self.app_state.set_result_check_job(job)
    
    def _process_log_queue(self):
        """Process log messages from queue"""
        log_queue = self.app_state.get_log_queue()
        if not log_queue:
            return
        
        try:
            for _ in range(MAX_LOG_MESSAGES_PER_CALL):
                try:
                    log_msg = log_queue.get_nowait()
                    level = log_msg['level']
                    message = log_msg['message']
                    
                    icon = LOG_ICONS.get(level, 'ℹ️')
                    formatted_message = f"{icon} {message}"
                    
                    self.right_panel.add_colored_result(formatted_message, level)
                    
                except:
                    break  # Queue is empty
        except Exception:
            pass  # Silently ignore errors during shutdown
        
        # Schedule next check
        try:
            self.after(RESULT_CHECK_INTERVAL, self._process_log_queue)
        except:
            pass  # Window is closing
    
    def _on_scraping_complete(self):
        """Handle scraping completion"""
        self.app_state.set_scraping_state(False)
        self.left_panel.set_scraping_state(False)
        self.middle_panel.set_progress(1.0)
        
        # Finalize scraping and get processed results
        all_results = self.app_state.get_results()
        processed_results = self.scraping_service.finalize_scraping(
            self.left_panel.get_auto_save(), all_results
        )
        
        # Update state with processed results (don't clear existing results)
        if processed_results:
            self.app_state.add_results(processed_results)
        
        # Update UI
        self._update_ui_for_scraping_complete()
        
        self.logger.info(f"Scraping finished. Total unique results: {len(processed_results)}")
    
    def _update_ui_for_scraping_start(self, num_threads, queries):
        """Update UI when scraping starts"""
        self.middle_panel.update_threads_status(f"Started {num_threads} worker threads\nInitializing...")
    
    def _update_ui_for_scraping_stop(self):
        """Update UI when scraping stops"""
        self.middle_panel.update_threads_status(
            f"⏹️ All threads force-stopped\n"
            f"📊 Completed: {self.scraping_state.get_completed_tasks()}/{self.scraping_state.get_total_tasks()} tasks\n"
            f"✅ Results collected: {self.app_state.get_results_count()}"
        )
    
    def _update_ui_for_scraping_complete(self):
        """Update UI when scraping completes"""
        self.middle_panel.update_threads_status(
            f"✅ All threads completed\n"
            f"📊 Processed: {self.scraping_state.get_completed_tasks()}/{self.scraping_state.get_total_tasks()} tasks\n"
            f"✅ Total results: {self.app_state.get_results_count()}"
        )
    
    def _update_progress(self):
        """Update progress display"""
        if self.scraping_state.get_total_tasks() > 0:
            progress = self.scraping_state.get_progress_ratio()
            self.middle_panel.set_progress(progress)
    
    def _update_thread_status(self):
        """Update thread status display"""
        from src.gui.state.worker_tracker import WorkerTracker
        
        tracker = WorkerTracker()
        tracker.update_worker_status(self.scraping_service.worker_pool)
        
        status_message = tracker.get_status_summary(
            self.scraping_state.get_active_workers(),
            self.scraping_state.get_completed_tasks(),
            self.scraping_state.get_total_tasks(),
            self.app_state.get_results()
        )
        
        self.middle_panel.update_threads_status(status_message)
    
    def _clear_results_display(self):
        """Clear results display"""
        self.right_panel.clear_results()
    
    def _is_scraping_complete(self):
        """Check if scraping is complete"""
        return (not self.scraping_service.is_active() and 
                not self.scraping_service.has_pending_tasks() and
                self.app_state.get_scraping_state())
    
    def on_closing(self):
        """Handle window closing"""
        if self.app_state.get_scraping_state():
            self.stop_scraping()
        
        result_check_job = self.app_state.get_result_check_job()
        if result_check_job:
            self.after_cancel(result_check_job)
        
        Logger.remove_ui_handler()
        self.logger.info("Application closing")
        self.destroy()
