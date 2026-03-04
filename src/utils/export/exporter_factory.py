"""
Factory for creating and managing exporters.
"""
from typing import Dict, Type, Optional, List, Any
from pathlib import Path

from .base import BaseExporter, ExportResult
from .csv_exporter import CSVExporter
from .excel_exporter import ExcelExporter
from .json_exporter import JSONExporter
from .config import ExportConfig
from src.utils.logging import Logger


class ExporterFactory:
    """Factory class for creating exporters and managing export operations."""
    
    # Registry of available exporters
    _exporters: Dict[str, Type[BaseExporter]] = {
        'csv': CSVExporter,
        'excel': ExcelExporter,
        'json': JSONExporter
    }
    
    def __init__(self):
        self.logger = Logger.get_logger("ExporterFactory")
    
    @classmethod
    def create_exporter(cls, format_type: str, **kwargs) -> BaseExporter:
        """
        Create an exporter instance for the specified format.
        """
        format_type = format_type.lower()
        
        if format_type not in cls._exporters:
            available_formats = ', '.join(cls._exporters.keys())
            raise ValueError(f"Unsupported export format: {format_type}. "
                           f"Available formats: {available_formats}")
        
        exporter_class = cls._exporters[format_type]
        return exporter_class(**kwargs)
    
    @classmethod
    def register_exporter(cls, format_type: str, exporter_class: Type[BaseExporter]) -> None:
        """
        Register a new exporter type.
        """
        cls._exporters[format_type.lower()] = exporter_class
    
    @classmethod
    def get_available_formats(cls) -> List[str]:
        """
        Get list of available export formats.
        """
        return list(cls._exporters.keys())
    
    @classmethod
    def is_format_supported(cls, format_type: str) -> bool:
        """
        Check if a format is supported.
        """
        return format_type.lower() in cls._exporters
    
    def export_data(self, data: List[Dict], format_type: str, 
                   filename: Optional[str] = None, 
                   output_dir: Optional[Path] = None,
                   **exporter_kwargs) -> ExportResult:
        """
        Export data using the specified format.
        """
        try:
            exporter = self.create_exporter(format_type, **exporter_kwargs)
            result = exporter.export(data, filename, output_dir)
            
            if result.success:
                self.logger.info(f"Successfully exported data to {format_type.upper()} "
                               f"format: {result.file_path}")
            else:
                self.logger.error(f"Failed to export data to {format_type.upper()}: "
                                f"{result.errors}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in export operation: {e}"
            self.logger.error(error_msg)
            return ExportResult(success=False, errors=[error_msg])
    
    def export_to_multiple_formats(self, data: List[Dict], 
                                  formats: List[str],
                                  base_filename: Optional[str] = None,
                                  output_dir: Optional[Path] = None) -> Dict[str, ExportResult]:
        """
        Export data to multiple formats.
        """
        results = {}
        
        for format_type in formats:
            try:
                # Generate format-specific filename
                if base_filename:
                    filename = f"{base_filename}_{format_type}"
                else:
                    filename = None
                
                result = self.export_data(data, format_type, filename, output_dir)
                results[format_type] = result
                
            except Exception as e:
                self.logger.error(f"Failed to export to {format_type}: {e}")
                results[format_type] = ExportResult(
                    success=False, 
                    errors=[str(e)]
                )
        
        return results
    
    def get_format_info(self, format_type: str) -> Dict[str, Any]:
        """
        Get information about a specific format.
        """
        format_type = format_type.lower()
        
        if not self.is_format_supported(format_type):
            return {'error': f'Format {format_type} not supported'}
        
        return {
            'format': format_type,
            'extension': ExportConfig.get_file_extension(format_type),
            'mime_type': ExportConfig.get_mime_type(format_type),
            'config': ExportConfig.get_config_for_format(format_type),
            'columns': ExportConfig.get_columns_for_format(format_type)
        }
    
    def validate_export_request(self, data: List[Dict], format_type: str) -> Dict[str, Any]:
        """
        Validate an export request.
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check data validity
        if not data:
            validation_result['valid'] = False
            validation_result['errors'].append("No data to export")
            return validation_result
        
        if not isinstance(data, list):
            validation_result['valid'] = False
            validation_result['errors'].append("Data must be a list")
            return validation_result
        
        if not all(isinstance(item, dict) for item in data):
            validation_result['valid'] = False
            validation_result['errors'].append("All data items must be dictionaries")
            return validation_result
        
        # Check format support
        if not self.is_format_supported(format_type):
            validation_result['valid'] = False
            validation_result['errors'].append(f"Format {format_type} not supported")
            return validation_result
        
        # Format-specific validation
        if format_type.lower() in ['csv', 'excel']:
            columns = ExportConfig.get_columns_for_format(format_type)
            if columns:
                # Check if any data has the expected columns
                sample_item = data[0]
                missing_columns = [col for col in columns if col not in sample_item]
                if missing_columns:
                    validation_result['warnings'].append(
                        f"Some expected columns are missing: {missing_columns}"
                    )
        
        return validation_result
