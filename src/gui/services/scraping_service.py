"""
Core scraping workflow service
"""
import asyncio
from datetime import datetime
from src.core.worker import WorkerPool
from src.scraper.google_maps import GoogleMapsScraper
from src.scraper.proxy_manager import ProxyManager
from src.core.config import Config
from src.utils.data_processing import DataProcessor
from src.utils.export import DataExporter
from src.gui.state.scraping_state import ScrapingState
from src.gui.utils.file_operations import create_safe_filename
from src.gui.utils.notification_manager import NotificationManager
from src.gui.constants.scraping_constants import (
    TIMESTAMP_FORMAT, COMBINED_FILENAME_PREFIX, WORKER_POOL_TIMEOUT
)


class ScrapingService:
    """Manages the core scraping workflow"""
    
    def __init__(self, logger):
        self.logger = logger
        self.worker_pool = None
        self.scraping_state = ScrapingState()
    
    async def start_scraping(self, queries, max_results, num_threads, use_proxy, headless):
        """Start the scraping process"""
        self.scraping_state.initialize_scraping(len(queries))
        
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
        
        # Add and start tasks
        self.worker_pool.add_tasks(queries)
        self.worker_pool.start()
        
        return self.worker_pool
    
    async def _scrape_query(self, query, max_results, use_proxy, headless, proxy_manager=None):
        """Scrape a single query"""
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
    
    def check_results(self):
        """Check for new results from worker pool"""
        if not self.worker_pool:
            return None
        
        return self.worker_pool.get_result(timeout=WORKER_POOL_TIMEOUT)
    
    def process_result(self, result, auto_save_enabled):
        """Process a single result from worker pool"""
        status = result['status']
        task = result['task']
        worker_id = result.get('worker_id', 'unknown')
        
        self.logger.debug(f"Processing result: status={status}, task={task}, worker_id={worker_id}")
        
        if status == 'success':
            results = result['result']
            self.logger.debug(f"Success case: {len(results)} results for task '{task}'")
            self.scraping_state.remove_active_worker(worker_id)
            self.scraping_state.increment_completed()
            
            # Log success
            self.logger.info(f"✅ {task}: {len(results)} results extracted")
            
            # Auto-save if enabled
            if auto_save_enabled and results:
                self.logger.debug(f"Auto-saving {len(results)} results for task '{task}'")
                self._auto_save_task_results(task, results)
            
            self.logger.debug(f"Returning {len(results)} results to main window")
            return results
            
        else:
            error = result.get('error', 'Unknown error')
            self.logger.debug(f"Error case: {error} for task '{task}'")
            self.scraping_state.remove_active_worker(worker_id)
            self.scraping_state.increment_completed()
            
            # Log error and notify
            self.logger.error(f"❌ {task}: {error}")
            NotificationManager.notify_task_error(task, error)
            self.logger.debug("Returning None to main window due to error")
            return None
    
    def _auto_save_task_results(self, task_name, results):
        """Auto-save results for a specific task"""
        try:
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            filename = create_safe_filename(task_name, timestamp) + ".csv"
            
            filepath = DataExporter.to_csv(results, filename=filename)
            self.logger.info(f"💾 Saved {task_name} results to: {filename}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save {task_name} results: {e}")
    
    def finalize_scraping(self, auto_save_enabled, all_results):
        """Finalize scraping process and save combined results"""
        self.logger.debug(f"Finalize scraping called with auto_save={auto_save_enabled}, all_results_count={len(all_results)}")
        
        # Process results
        processed_results = None
        if all_results:
            self.logger.debug(f"Processing {len(all_results)} results for finalization")
            processor = DataProcessor()
            cleaned_results = processor.clean_results(all_results)
            cleaned_results = processor.remove_duplicates(cleaned_results)
            
            self.logger.info(f"🎉 Scraping complete! Total results: {len(cleaned_results)}")
            NotificationManager.notify_scraping_complete(len(cleaned_results), self.scraping_state.get_total_tasks())
            
            # Create combined CSV file if enabled
            if auto_save_enabled:
                self.logger.debug("Auto-save enabled, creating combined results file")
                self._save_combined_results(cleaned_results)
            
            processed_results = cleaned_results
            self.logger.debug(f"Finalized with {len(processed_results)} processed results")
        else:
            self.logger.warning("⚠️ Scraping complete but no results found")
            NotificationManager.notify_no_results()
            processed_results = []
            self.logger.debug("Finalized with 0 processed results")
        
        return processed_results
    
    def _save_combined_results(self, results):
        """Save combined results file"""
        try:
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            combined_filename = f"{COMBINED_FILENAME_PREFIX}_{timestamp}.csv"
            filepath = DataExporter.to_csv(results, filename=combined_filename)
            self.logger.info(f"💾 Saved combined results to: {combined_filename}")
            
            # Open the combined CSV file with default application
            if open_file_with_default_app(filepath):
                self.logger.info("📂 Opened combined CSV file")
            else:
                self.logger.warning("⚠️ Could not open file automatically")
                
        except Exception as e:
            self.logger.error(f"❌ Auto-save failed: {e}")
            NotificationManager.notify_export_error(e)
    
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.worker_pool:
            self.logger.info("🛑 Force stopping all workers...")
            self.worker_pool.stop(wait=False, force=True)
            self.worker_pool = None
        
        self.scraping_state.clear()
    
    def get_scraping_state(self):
        """Get current scraping state"""
        return self.scraping_state
    
    def is_active(self):
        """Check if scraping is currently active"""
        return self.worker_pool is not None and self.worker_pool.is_active()
    
    def has_pending_tasks(self):
        """Check if there are pending tasks"""
        return self.worker_pool is not None and self.worker_pool.tasks_pending() > 0
