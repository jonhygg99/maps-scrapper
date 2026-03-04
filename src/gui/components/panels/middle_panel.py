"""
Middle panel component containing status and thread monitoring
"""
import customtkinter as ctk
from src.gui.styles import FONTS


class MiddlePanel(ctk.CTkFrame):
    """Middle panel with thread monitoring and status log"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        self._create_ui()
    
    def _create_ui(self):
        """Create the middle panel user interface"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Threads status
        self.grid_rowconfigure(4, weight=1)  # General status
        
        # Threads Status Section
        threads_label = ctk.CTkLabel(
            self,
            text="⚙️ Worker Threads",
            font=FONTS['heading']
        )
        threads_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        self.threads_text = ctk.CTkTextbox(
            self,
            font=FONTS['small']
        )
        self.threads_text.grid(row=2, column=0, padx=15, pady=5, sticky="nsew")
        self.update_threads_status("No active threads")
        
        # Status Section
        status_label = ctk.CTkLabel(
            self,
            text="📋 Status Log",
            font=FONTS['heading']
        )
        status_label.grid(row=3, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.status_text = ctk.CTkTextbox(
            self,
            font=FONTS['small']
        )
        self.status_text.grid(row=4, column=0, padx=15, pady=(5, 15), sticky="nsew")
        self.add_status("Ready to start scraping...")
    
    def update_threads_status(self, message):
        """Update threads status box with message"""
        self.threads_text.delete("1.0", "end")
        self.threads_text.insert("1.0", message)
    
    def update_threads_status_from_pool(self, worker_pool, active_workers, completed_tasks, total_tasks, all_results):
        """Update thread status from worker pool information"""
        if not worker_pool:
            self.update_threads_status("⭕ No active threads")
            return
        
        try:
            # Get worker pool statistics
            alive_workers = [w for w in worker_pool.workers if w.is_alive()]
            total_workers = len(worker_pool.workers)
            pending_tasks = worker_pool.tasks_pending()
            
            # Build status message
            status_lines = []
            
            # Header with summary
            status_lines.append(f"🔧 Workers: {len(alive_workers)}/{total_workers} active")
            status_lines.append(f"📋 Tasks: {completed_tasks}/{total_tasks} completed")
            status_lines.append(f"⏳ Pending: {pending_tasks}")
            status_lines.append(f"✅ Results: {len(all_results)}")
            
            # Individual worker status
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
            
            self.update_threads_status("\n".join(status_lines))
            
        except Exception as e:
            self.update_threads_status(f"❌ Status error: {e}")
    
    def add_status(self, message):
        """Add message to status box"""
        self.status_text.insert("end", f"{message}\n")
        self.status_text.see("end")
    
    def set_progress(self, value):
        """Set progress bar value"""
        self.progress_bar.set(min(value, 1.0))
    
    def reset_progress(self):
        """Reset progress bar to zero"""
        self.progress_bar.set(0)
