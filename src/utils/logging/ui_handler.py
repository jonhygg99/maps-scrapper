"""
UI Log Handler for Application
Handles queue-based log message processing for UI components
"""
import logging
import queue


class UILogHandler(logging.Handler):
    """Custom handler that queues log messages for UI processing"""
    
    def __init__(self, log_queue: queue.Queue):
        """Initialize UI log handler with message queue"""
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        """Emit a log record to the queue (thread-safe)"""
        try:
            msg = self.format(record)
            # Put the message in queue without blocking
            try:
                self.log_queue.put_nowait({
                    'level': record.levelname,
                    'message': msg
                })
            except queue.Full:
                # Queue is full, skip this message
                pass
        except Exception:
            self.handleError(record)
