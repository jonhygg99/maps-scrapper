"""
Excel export functionality.
"""
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path

from .base import BaseExporter, ExportResult
from .file_manager import FileManager
from .config import ExportConfig


class ExcelExporter(BaseExporter):
    """Exporter for Excel format files."""
    
    def __init__(self, columns: Optional[List[str]] = None):
        super().__init__("ExcelExporter")
        self.file_manager = FileManager()
        self.columns = columns or ExportConfig.DEFAULT_CSV_COLUMNS
        self.config = ExportConfig.get_config_for_format('excel')
    
    def export(self, data: List[Dict], filename: Optional[str] = None, 
               output_dir: Optional[Path] = None) -> ExportResult:
        """
        Export data to Excel file.
        """
        try:
            # Validate input data
            if not self._validate_data(data):
                return self._create_export_result(False, errors=["Invalid input data"])
            
            # Setup output directory and filename
            output_dir = self.file_manager.setup_output_directory(output_dir)
            filename = self.file_manager.generate_filename('excel', filename)
            file_path = self.file_manager.get_file_path(filename, output_dir)
            
            # Validate file path
            if not self.file_manager.validate_file_path(file_path):
                return self._create_export_result(False, errors=[f"Invalid file path: {file_path}"])
            
            # Filter data to include only specified columns
            filtered_data = self._filter_data_columns(data)
            
            # Write Excel file
            records_written = self._write_excel_file(file_path, filtered_data)
            
            self.logger.info(f"Exported {records_written} records to {file_path}")
            
            result = self._create_export_result(
                success=True,
                file_path=str(file_path),
                records=records_written
            )
            result.set_metadata('format', 'excel')
            result.set_metadata('columns', self.columns)
            result.set_metadata('sheet_name', self.config.get('sheet_name', 'Results'))
            
            return result
            
        except Exception as e:
            error_msg = f"Error exporting to Excel: {e}"
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
    
    def _write_excel_file(self, file_path: Path, data: List[Dict]) -> int:
        """
        Write data to Excel file with formatting.
        """
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Export to Excel with formatting
        sheet_name = self.config.get('sheet_name', 'Results')
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            # Auto-adjust column widths if enabled
            if self.config.get('auto_adjust_widths', True):
                self._adjust_column_widths(writer.sheets[sheet_name], df)
        
        return len(data)
    
    def _adjust_column_widths(self, worksheet, df) -> None:
        """
        Auto-adjust column widths in Excel worksheet.
        """
        max_width = self.config.get('max_column_width', 50)
        min_width = self.config.get('min_column_width', 10)
        
        for column in df:
            # Calculate maximum length of data in column
            column_length = max(
                df[column].astype(str).map(len).max(),
                len(str(column))
            )
            
            # Apply width constraints
            column_length = max(min_width, min(column_length + 2, max_width))
            
            # Set column width
            col_idx = df.columns.get_loc(column)
            col_letter = chr(65 + col_idx)  # A, B, C, etc.
            worksheet.column_dimensions[col_letter].width = column_length
    
    def set_columns(self, columns: List[str]) -> None:
        """
        Update the columns to export.
        
        Args:
            columns: New list of column names
        """
        self.columns = columns
        self.logger.debug(f"Updated Excel columns: {self.columns}")
    
    def add_column(self, column: str) -> None:
        """
        Add a column to the export list.
        """
        if column not in self.columns:
            self.columns.append(column)
            self.logger.debug(f"Added Excel column: {column}")
    
    def remove_column(self, column: str) -> None:
        """
        Remove a column from the export list.
        """
        if column in self.columns:
            self.columns.remove(column)
            self.logger.debug(f"Removed Excel column: {column}")
    
    def set_sheet_name(self, sheet_name: str) -> None:
        """
        Set the worksheet name for Excel export.
        """
        self.config['sheet_name'] = sheet_name
        self.logger.debug(f"Set Excel sheet name: {sheet_name}")
