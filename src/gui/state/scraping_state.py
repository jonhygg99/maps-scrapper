"""
Scraping-specific state management
"""
from typing import Dict


class ScrapingState:
    """Manages scraping workflow state"""
    
    def __init__(self):
        self.active_workers = {}  # Track active workers {worker_id: task_name}
        self.completed_tasks = 0
        self.total_tasks = 0
    
    def initialize_scraping(self, total_tasks):
        """Initialize state for new scraping session"""
        self.active_workers.clear()
        self.completed_tasks = 0
        self.total_tasks = total_tasks
    
    def add_active_worker(self, worker_id, task_name):
        """Add a worker to active tracking"""
        self.active_workers[worker_id] = task_name
    
    def remove_active_worker(self, worker_id):
        """Remove a worker from active tracking"""
        if worker_id in self.active_workers:
            del self.active_workers[worker_id]
    
    def increment_completed(self):
        """Increment completed tasks count"""
        self.completed_tasks += 1
    
    def get_active_workers(self):
        """Get active workers dictionary"""
        return self.active_workers
    
    def get_active_worker_count(self):
        """Get count of active workers"""
        return len(self.active_workers)
    
    def get_completed_tasks(self):
        """Get number of completed tasks"""
        return self.completed_tasks
    
    def get_total_tasks(self):
        """Get total number of tasks"""
        return self.total_tasks
    
    def get_progress_ratio(self):
        """Get progress as a ratio (0.0 to 1.0)"""
        if self.total_tasks > 0:
            return self.completed_tasks / self.total_tasks
        return 0.0
    
    def is_complete(self):
        """Check if all tasks are completed"""
        return self.completed_tasks >= self.total_tasks
    
    def clear(self):
        """Clear all scraping state"""
        self.active_workers.clear()
        self.completed_tasks = 0
        self.total_tasks = 0
