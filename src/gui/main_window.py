"""
Main GUI Window for Google Maps Scraper - Refactored Version
Multi-threaded interface with modern CustomTkinter design
"""
import customtkinter as ctk
import queue
import asyncio
import webbrowser
import json
import os
import platform
import subprocess
import re
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from src.gui.styles import COLORS, FONTS, apply_theme
from src.core.worker import WorkerPool
from src.core.config import Config
from src.scraper.google_maps import GoogleMapsScraper
from src.scraper.proxy_manager import ProxyManager
from src.utils.logging import Logger
from src.utils.data_processing import DataProcessor
from src.utils.export import DataExporter
from src.utils.notifier import Notifier

# Import new components
from src.gui.components.panels.left_panel import LeftPanel
from src.gui.components.panels.middle_panel import MiddlePanel
from src.gui.components.panels.right_panel import RightPanel
from src.gui.components.modals.settings_editor import SettingsEditor
from src.gui.components.modals.proxy_editor import ProxyEditor


class MainWindow(ctk.CTk):
    """Main application window - simplified orchestrator"""
    
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
        
        # Apply theme
        apply_theme()
        
        # Add menu bar for config/proxy editors
        self._create_menu()

        # Setup UI with components
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
        """Create the user interface using components"""
        
        # Configure grid - 3 columns layout
        self.grid_columnconfigure(0, weight=1, minsize=320)  # Left: Input controls
        self.grid_columnconfigure(1, weight=1, minsize=280)  # Middle: Status & Threads
        self.grid_columnconfigure(2, weight=2, minsize=500)  # Right: Results (larger)
        self.grid_rowconfigure(0, weight=1)
        
        # Create three panels using components
        self.left_panel = LeftPanel(self)
        self.left_panel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        
        self.middle_panel = MiddlePanel(self)
        self.middle_panel.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        self.right_panel = RightPanel(self)
        self.right_panel.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="nsew")
        
        # Connect button callbacks
        self.left_panel.start_btn.configure(command=self.start_scraping)
        self.left_panel.stop_btn.configure(command=self.stop_scraping)
        self.left_panel.open_output_btn.configure(command=self.open_output_folder)
        self.left_panel.donate_btn.configure(command=self.open_donate_link)
        
        self.right_panel.export_csv_btn.configure(command=lambda: self.export_data('csv'))
        self.right_panel.export_excel_btn.configure(command=lambda: self.export_data('excel'))
        self.right_panel.clear_btn.configure(command=self.clear_results)
    
    def start_scraping(self):
        """Start the scraping process"""
        # Get queries from left panel
        queries = self.left_panel.get_queries()
        if not queries:
            self.logger.warning("⚠️ Please enter at least one search query")
            return
        
        try:
            max_results = self.left_panel.get_max_results()
            num_threads = self.left_panel.get_threads()
        except ValueError:
            self.logger.error("⚠️ Invalid number format in settings")
            return
        
        # Update UI state
        self.is_scraping = True
        self.left_panel.set_scraping_state(True)
        self.middle_panel.reset_progress()
        
        # Clear previous results
        self.all_results.clear()
        self.right_panel.clear_results()
        
        # Initialize tracking
        self.active_workers.clear()
        self.completed_tasks = 0
        self.total_tasks = len(queries)
        
        self.logger.info(f"🚀 Starting scraping for {len(queries)} queries")
        self.logger.info(f"📊 Settings: {max_results} results per query, {num_threads} threads")
        
        # Get settings
        use_proxy = self.left_panel.get_use_proxy()
        headless = self.left_panel.get_headless()
        
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
        self.middle_panel.update_threads_status(f"Started {num_threads} worker threads\nInitializing...")
        
        self.logger.info(f"Started {num_threads} worker threads for {len(queries)} queries")
    
    async def _scrape_query(self, query: str, max_results: int, use_proxy: bool, 
                           headless: bool, proxy_manager=None):
        """Scrape a single query (runs in worker thread)"""
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
                    
                    # Log success
                    self.logger.info(f"✅ {task}: {len(results)} results extracted")
                    
                    # Auto-save this task's results if enabled
                    if self.left_panel.get_auto_save() and results:
                        try:
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
                        self.middle_panel.set_progress(progress)
                    
                else:
                    error = result.get('error', 'Unknown error')
                    
                    # Mark worker as idle
                    if worker_id in self.active_workers:
                        del self.active_workers[worker_id]
                    self.completed_tasks += 1
                    
                    # Log error
                    self.logger.error(f"❌ {task}: {error}")
                    
                    # Send error notification
                    Notifier.notify_error(f"Task '{task}' failed: {str(error)[:80]}")
            
            # Update thread status
            self.middle_panel.update_threads_status_from_pool(
                self.worker_pool, self.active_workers, self.completed_tasks, 
                self.total_tasks, self.all_results
            )
            
            # Check if all workers are done
            if not self.worker_pool.is_active() and self.worker_pool.tasks_pending() == 0:
                if self.is_scraping:
                    self._on_scraping_complete()
        
        # Schedule next check
        self.result_check_job = self.after(100, self._check_results)
    
    def _on_scraping_complete(self):
        """Called when scraping is complete"""
        self.is_scraping = False
        self.left_panel.set_scraping_state(False)
        self.middle_panel.set_progress(1.0)
        
        # Stop and cleanup worker pool
        if self.worker_pool:
            self.worker_pool.stop(wait=True)
            self.worker_pool = None
        
        # Clear active workers
        self.active_workers.clear()
        
        # Update thread status
        self.middle_panel.update_threads_status(
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
            if self.left_panel.get_auto_save():
                try:
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
                    Notifier.notify_error(f"Failed to save results: {str(e)[:100]}")
        else:
            self.logger.warning("⚠️ Scraping complete but no results found")
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
        self.left_panel.set_scraping_state(False)
        
        # Clear active workers
        self.active_workers.clear()
        
        # Update thread status
        self.middle_panel.update_threads_status(
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
        """Open the output/results folder in the system file explorer"""
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
    
    def _process_log_queue(self):
        """Process log messages from the queue (runs on main thread)"""
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
                    self.right_panel.add_colored_result(formatted_message, level)
                    
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
