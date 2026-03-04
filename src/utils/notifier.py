"""
Cross-platform desktop notification utility
Supports Windows, macOS, and Linux
"""
import logging
from typing import Optional

try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    logging.warning("plyer not installed. Desktop notifications disabled.")


class Notifier:
    """Cross-platform desktop notification manager"""
    
    APP_NAME = "Google Maps Scraper"
    APP_ICON = None  # Can be set to path of .ico file
    
    @staticmethod
    def notify(
        title: str,
        message: str,
        timeout: int = 10,
        app_icon: Optional[str] = None
    ) -> bool:
        """
        Show a desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            timeout: How long to show notification (seconds)
            app_icon: Path to icon file (optional)
            
        Returns:
            True if notification was sent, False otherwise
        """
        if not NOTIFICATIONS_AVAILABLE:
            logging.debug(f"Notification skipped (plyer not available): {title} - {message}")
            return False
        
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=Notifier.APP_NAME,
                app_icon=app_icon or Notifier.APP_ICON,
                timeout=timeout
            )
            logging.debug(f"Notification sent: {title}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")
            return False
    
    @staticmethod
    def notify_success(message: str, timeout: int = 10) -> bool:
        """Show success notification"""
        return Notifier.notify(
            title="✅ Success",
            message=message,
            timeout=timeout
        )
    
    @staticmethod
    def notify_error(message: str, timeout: int = 10) -> bool:
        """Show error notification"""
        return Notifier.notify(
            title="❌ Error",
            message=message,
            timeout=timeout
        )
    
    @staticmethod
    def notify_warning(message: str, timeout: int = 10) -> bool:
        """Show warning notification"""
        return Notifier.notify(
            title="⚠️ Warning",
            message=message,
            timeout=timeout
        )
    
    @staticmethod
    def notify_info(message: str, timeout: int = 10) -> bool:
        """Show info notification"""
        return Notifier.notify(
            title="ℹ️ Info",
            message=message,
            timeout=timeout
        )
    
    @staticmethod
    def notify_complete(total_results: int, total_tasks: int, timeout: int = 10) -> bool:
        """Show scraping completion notification"""
        return Notifier.notify(
            title="🎉 Scraping Complete!",
            message=f"Completed {total_tasks} tasks\nExtracted {total_results} results",
            timeout=timeout
        )
