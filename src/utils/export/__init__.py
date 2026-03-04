"""
Data Exporter for CSV and Excel Formats

This module has been refactored to use the new modular export system.
The DataExporter class is maintained for backward compatibility.

For new code, consider using:
    from src.utils.export import ExporterFactory, export_data
    
    factory = ExporterFactory()
    result = factory.export_data(data, 'csv', 'my_data.csv')
"""

# Import the new export system
from .export import (
    DataExporter as NewDataExporter,
    ExporterFactory,
    ExportResult,
    export_data,
    get_available_formats
)

# Re-export for backward compatibility
DataExporter = NewDataExporter

# Additional convenience functions for the new API
__all__ = ['DataExporter', 'ExporterFactory', 'ExportResult', 'export_data', 'get_available_formats']
