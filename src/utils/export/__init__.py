"""
Data Exporter for CSV and Excel Formats

This module provides a unified interface for data export operations.
"""

# Import the new export system components
from .exporter_factory import ExporterFactory
from .base import ExportResult
from .file_manager import FileManager

# Create a simple DataExporter class for backward compatibility
class DataExporter:
    """Backward compatible DataExporter class"""
    
    def __init__(self):
        self.factory = ExporterFactory()
        self.file_manager = FileManager()
    
    def export_to_csv(self, data, filename):
        """Export data to CSV format"""
        return self.factory.export_data(data, 'csv', filename)
    
    def export_to_excel(self, data, filename):
        """Export data to Excel format"""
        return self.factory.export_data(data, 'excel', filename)
    
    def export_to_json(self, data, filename):
        """Export data to JSON format"""
        return self.factory.export_data(data, 'json', filename)
    
    @classmethod
    def to_csv(cls, data, filename=None):
        """Export data to CSV format (class method for backward compatibility)"""
        instance = cls()
        return instance.export_to_csv(data, filename)
    
    @classmethod
    def to_excel(cls, data, filename=None):
        """Export data to Excel format (class method for backward compatibility)"""
        instance = cls()
        return instance.export_to_excel(data, filename)
    
    @classmethod
    def to_json(cls, data, filename=None):
        """Export data to JSON format (class method for backward compatibility)"""
        instance = cls()
        return instance.export_to_json(data, filename)

# Convenience functions
def export_data(data, format_type, filename, **kwargs):
    """Export data using the factory"""
    factory = ExporterFactory()
    return factory.export_data(data, format_type, filename, **kwargs)

def get_available_formats():
    """Get available export formats"""
    return ['csv', 'excel', 'json']

# Export all components
__all__ = ['DataExporter', 'ExporterFactory', 'ExportResult', 'export_data', 'get_available_formats', 'FileManager']
