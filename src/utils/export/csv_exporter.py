"""
CSV export functionality.
"""
import csv
from typing import List, Dict, Optional
from pathlib import Path

from .base import BaseExporter, ExportResult
from .file_manager import FileManager
from .config import ExportConfig


class CSVExporter(BaseExporter):
    """Exporter for CSV format files."""
    
    def __init__(self, columns: Optional[List[str]] = None):
        super().__init__("CSVExporter")
        self.file_manager = FileManager()
        self.columns = columns or ExportConfig.DEFAULT_CSV_COLUMNS
        self.config = ExportConfig.get_config_for_format('csv')
    
    def export(self, data: List[Dict], filename: Optional[str] = None, 
               output_dir: Optional[Path] = None) -> ExportResult:
        """
        Export data to CSV file.
        """
        try:
            # Validate input data
            if not self._validate_data(data):
                return self._create_export_result(False, errors=["Invalid input data"])
            
            # Setup output directory and filename
            output_dir = self.file_manager.setup_output_directory(output_dir)
            filename = self.file_manager.generate_filename('csv', filename)
            file_path = self.file_manager.get_file_path(filename, output_dir)
            
            # Validate file path
            if not self.file_manager.validate_file_path(file_path):
                return self._create_export_result(False, errors=[f"Invalid file path: {file_path}"])
            
            # Filter data to include only specified columns
            filtered_data = self._filter_data_columns(data)
            
            # Write CSV file
            records_written = self._write_csv_file(file_path, filtered_data)
            
            self.logger.info(f"Exported {records_written} records to {file_path}")
            
            result = self._create_export_result(
                success=True,
                file_path=str(file_path),
                records=records_written
            )
            result.set_metadata('format', 'csv')
            result.set_metadata('columns', self.columns)
            
            return result
            
        except Exception as e:
            error_msg = f"Error exporting to CSV: {e}"
            self.logger.error(error_msg)
            return self._create_export_result(False, errors=[error_msg])
    
    def _filter_data_columns(self, data: List[Dict]) -> List[Dict]:
        """
        Filter data to include only specified columns.
        """
        filtered_data = []
        for item in data:
            filtered_item = {}
            for field in self.columns:
                filtered_item[field] = item.get(field, '')
            filtered_data.append(filtered_item)
        
        return filtered_data
    
    def _write_csv_file(self, file_path: Path, data: List[Dict]) -> int:
        """
        Write data to CSV file.
        """
        encoding = self.config.get('encoding', 'utf-8-sig')
        
        with open(file_path, 'w', newline='', encoding=encoding) as csvfile:
            writer = csv.DictWriter(
                csvfile, 
                fieldnames=self.columns,
                delimiter=self.config.get('delimiter', ','),
                quotechar=self.config.get('quote_char', '"'),
                escapechar=self.config.get('escape_char'),
                lineterminator=self.config.get('lineterminator', '\n')
            )
            
            writer.writeheader()
            writer.writerows(data)
            
            return len(data)
    
    def set_columns(self, columns: List[str]) -> None:
        """
        Update the columns to export.
        """
        self.columns = columns
        self.logger.debug(f"Updated CSV columns: {self.columns}")
    
    def add_column(self, column: str) -> None:
        """
        Add a column to the export list.
        """
        if column not in self.columns:
            self.columns.append(column)
            self.logger.debug(f"Added CSV column: {column}")
    
    def remove_column(self, column: str) -> None:
        """
        Remove a column from the export list.
        """
        if column in self.columns:
            self.columns.remove(column)
            self.logger.debug(f"Removed CSV column: {column}")
