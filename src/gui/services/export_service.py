"""
Data export service
"""
from src.utils.export import DataExporter
from src.gui.utils.notification_manager import NotificationManager


class ExportService:
    """Manages data export operations"""
    
    def __init__(self, logger):
        self.logger = logger
    
    def export_data(self, data, format_type):
        """Export data in specified format"""
        if not data:
            self.logger.warning("⚠️ No data to export")
            return False
        
        try:
            if format_type == 'csv':
                filepath = DataExporter.to_csv(data)
                self.logger.info(f"✅ Exported to CSV: {filepath}")
                return filepath
            elif format_type == 'excel':
                filepath = DataExporter.to_excel(data)
                self.logger.info(f"✅ Exported to Excel: {filepath}")
                return filepath
            else:
                self.logger.error(f"❌ Unsupported export format: {format_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Export failed: {str(e)}")
            NotificationManager.notify_export_error(e)
            return False
    
    def export_csv(self, data):
        """Export data to CSV format"""
        return self.export_data(data, 'csv')
    
    def export_excel(self, data):
        """Export data to Excel format"""
        return self.export_data(data, 'excel')
