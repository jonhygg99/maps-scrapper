"""
Worker tracking and management utilities
"""
from typing import Dict, List


class WorkerTracker:
    """Tracks worker pool status and individual worker information"""
    
    def __init__(self):
        self.worker_status = {}  # {worker_id: status_info}
    
    def update_worker_status(self, worker_pool):
        """Update status from worker pool"""
        if not worker_pool:
            return
        
        try:
            alive_workers = [w for w in worker_pool.workers if w.is_alive()]
            total_workers = len(worker_pool.workers)
            pending_tasks = worker_pool.tasks_pending()
            
            self.worker_status = {
                'alive_count': len(alive_workers),
                'total_count': total_workers,
                'pending_tasks': pending_tasks,
                'alive_workers': alive_workers
            }
        except Exception:
            self.worker_status = {'error': True}
    
    def get_status_summary(self, active_workers, completed_tasks, total_tasks, all_results):
        """Generate formatted status summary"""
        if 'error' in self.worker_status:
            return "❌ Status error"
        
        status_lines = []
        
        # Header with summary
        status_lines.append(f"🔧 Workers: {self.worker_status['alive_count']}/{self.worker_status['total_count']} active")
        status_lines.append(f"📋 Tasks: {completed_tasks}/{total_tasks} completed")
        status_lines.append(f"⏳ Pending: {self.worker_status['pending_tasks']}")
        status_lines.append(f"✅ Results: {len(all_results)}")
        
        # Individual worker status
        alive_workers = self.worker_status.get('alive_workers', [])
        if alive_workers:
            status_lines.append("\n--- Worker Details ---")
            for worker in alive_workers:
                worker_id = worker.worker_id
                if worker_id in active_workers:
                    task_name = active_workers[worker_id]
                    # Truncate long task names
                    if len(task_name) > 30:
                        task_name = task_name[:27] + "..."
                    status_lines.append(f"Worker {worker_id}: 🔄 {task_name}")
                else:
                    status_lines.append(f"Worker {worker_id}: ⏸️ Idle")
        
        return "\n".join(status_lines)
    
    def has_active_workers(self):
        """Check if there are active workers"""
        return self.worker_status.get('alive_count', 0) > 0
    
    def get_alive_worker_count(self):
        """Get count of alive workers"""
        return self.worker_status.get('alive_count', 0)
