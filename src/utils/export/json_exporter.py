"""
JSON export functionality.
"""
import json
from typing import List, Dict, Optional, Any
from pathlib import Path

from .base import BaseExporter, ExportResult
from .file_manager import FileManager
from .config import ExportConfig


class JSONExporter(BaseExporter):
    """Exporter for JSON format files."""
    
    def __init__(self, include_metadata: bool = False):
        super().__init__("JSONExporter")
        self.file_manager = FileManager()
        self.include_metadata = include_metadata
        self.config = ExportConfig.get_config_for_format('json')
    
    def export(self, data: List[Dict], filename: Optional[str] = None, 
               output_dir: Optional[Path] = None) -> ExportResult:
        """
        Export data to JSON file.
        """
        try:
            # Validate input data
            if not self._validate_data(data):
                return self._create_export_result(False, errors=["Invalid input data"])
            
            # Setup output directory and filename
            output_dir = self.file_manager.setup_output_directory(output_dir)
            filename = self.file_manager.generate_filename('json', filename)
            file_path = self.file_manager.get_file_path(filename, output_dir)
            
            # Validate file path
            if not self.file_manager.validate_file_path(file_path):
                return self._create_export_result(False, errors=[f"Invalid file path: {file_path}"])
            
            # Prepare data for export
            export_data = self._prepare_export_data(data)
            
            # Write JSON file
            records_written = self._write_json_file(file_path, export_data)
            
            self.logger.info(f"Exported {records_written} records to {file_path}")
            
            result = self._create_export_result(
                success=True,
                file_path=str(file_path),
                records=records_written
            )
            result.set_metadata('format', 'json')
            result.set_metadata('include_metadata', self.include_metadata)
            
            return result
            
        except Exception as e:
            error_msg = f"Error exporting to JSON: {e}"
            self.logger.error(error_msg)
            return self._create_export_result(False, errors=[error_msg])
    
    def _prepare_export_data(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Prepare data for JSON export, optionally adding metadata.
        """
        if self.include_metadata:
            from datetime import datetime
            
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'total_records': len(data),
                    'exporter': self.name,
                    'version': '1.0'
                },
                'data': data
            }
        else:
            export_data = data
        
        return export_data
    
    def _write_json_file(self, file_path: Path, data: Any) -> int:
        """
        Write data to JSON file.
        """
        encoding = 'utf-8'  # Standard UTF-8 for JSON
        
        with open(file_path, 'w', encoding=encoding) as f:
            json.dump(
                data,
                f,
                indent=self.config.get('indent', 2),
                ensure_ascii=self.config.get('ensure_ascii', False),
                sort_keys=self.config.get('sort_keys', False)
            )
        
        # Count records based on data structure
        if isinstance(data, dict) and 'data' in data:
            return len(data['data'])
        elif isinstance(data, list):
            return len(data)
        else:
            return 1
    
    def set_include_metadata(self, include_metadata: bool) -> None:
        """
        Set whether to include metadata in JSON export.
        """
        self.include_metadata = include_metadata
        self.logger.debug(f"Set include_metadata: {include_metadata}")
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """
        Update JSON export configuration.
        """
        self.config.update(config)
        self.logger.debug(f"Updated JSON config: {config}")
    
    def filter_empty_fields(self, data: List[Dict]) -> List[Dict]:
        """
        Remove empty fields from data before export.
        
        Args:
            data: Original data
            
        Returns:
            Filtered data without empty fields
        """
        filtered_data = []
        for item in data:
            filtered_item = {
                key: value for key, value in item.items() 
                if value is not None and value != ''
            }
            filtered_data.append(filtered_item)
        
        return filtered_data
    
    def add_custom_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Add custom metadata to be included in export.
        
        Args:
            metadata: Custom metadata to include
        """
        if not hasattr(self, 'custom_metadata'):
            self.custom_metadata = {}
        self.custom_metadata.update(metadata)
        self.logger.debug(f"Added custom metadata: {metadata}")
    
    def _prepare_export_data(self, data: List[Dict]) -> Dict[str, Any]:
        """
        Prepare data for JSON export, optionally adding metadata.
        """
        if self.include_metadata:
            from datetime import datetime
            
            metadata = {
                'exported_at': datetime.now().isoformat(),
                'total_records': len(data),
                'exporter': self.name,
                'version': '1.0'
            }
            
            # Add custom metadata if available
            if hasattr(self, 'custom_metadata'):
                metadata.update(self.custom_metadata)
            
            export_data = {
                'metadata': metadata,
                'data': data
            }
        else:
            export_data = data
        
        return export_data
