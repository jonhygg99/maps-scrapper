"""
Application-wide state management
"""
from typing import Dict, Any, List


class ApplicationState:
    """Manages global application state"""
    
    def __init__(self):
        self.all_results = []
        self.is_scraping = False
        self.result_check_job = None
        self.log_queue = None
    
    def clear_results(self):
        """Clear all results"""
        self.all_results.clear()
    
    def add_results(self, results):
        """Add results to the collection"""
        self.all_results.extend(results)
    
    def get_results_count(self):
        """Get total number of results"""
        return len(self.all_results)
    
    def get_results(self):
        """Get all results"""
        return self.all_results
    
    def set_scraping_state(self, is_scraping):
        """Set scraping state"""
        self.is_scraping = is_scraping
    
    def get_scraping_state(self):
        """Get current scraping state"""
        return self.is_scraping
    
    def set_result_check_job(self, job):
        """Set the result check job reference"""
        self.result_check_job = job
    
    def get_result_check_job(self):
        """Get the result check job reference"""
        return self.result_check_job
    
    def set_log_queue(self, queue):
        """Set the log queue reference"""
        self.log_queue = queue
    
    def get_log_queue(self):
        """Get the log queue reference"""
        return self.log_queue
