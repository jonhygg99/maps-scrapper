"""
Centralized notification management
"""
from src.utils.notifier import Notifier
from src.gui.constants.scraping_constants import (
    ERROR_MESSAGE_TRUNCATE_LENGTH, SUCCESS_NOTIFICATION_TRUNCATE_LENGTH
)


class NotificationManager:
    """Manages all application notifications"""
    
    @staticmethod
    def notify_task_error(task_name, error_message):
        """Send notification for task error"""
        truncated_error = str(error_message)[:ERROR_MESSAGE_TRUNCATE_LENGTH]
        message = f"Task '{task_name}' failed: {truncated_error}"
        Notifier.notify_error(message)
    
    @staticmethod
    def notify_scraping_complete(total_results, total_tasks):
        """Send notification for scraping completion"""
        Notifier.notify_complete(
            total_results=total_results,
            total_tasks=total_tasks
        )
    
    @staticmethod
    def notify_scraping_stopped(completed_tasks, total_tasks):
        """Send notification for scraping stopped"""
        message = f"Scraping stopped - {completed_tasks}/{total_tasks} tasks completed"
        Notifier.notify_warning(message)
    
    @staticmethod
    def notify_no_results():
        """Send notification when no results found"""
        Notifier.notify_warning("Scraping complete but no results found")
    
    @staticmethod
    def notify_export_error(error_message):
        """Send notification for export failure"""
        truncated_error = str(error_message)[:SUCCESS_NOTIFICATION_TRUNCATE_LENGTH]
        message = f"Failed to save results: {truncated_error}"
        Notifier.notify_error(message)
