"""
Data Exporter for CSV and Excel Formats
"""
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from src.utils.logger import Logger
from src.core.config import Config


class DataExporter:
    """Export scraped data to various formats"""
    
    def __init__(self):
        self.logger = Logger.get_logger("DataExporter")
    
    @staticmethod
    def to_csv(data: List[Dict], filename: Optional[str] = None, output_dir: Optional[Path] = None) -> str:
        """
        Export data to CSV file
        
        Args:
            data: List of dictionaries to export
            filename: Output filename (auto-generated if None)
            output_dir: Output directory (uses config if None)
            
        Returns:
            Path to created file
        """
        logger = Logger.get_logger("DataExporter")
        
        if not data:
            logger.warning("No data to export")
            return None
        
        # Setup output path
        if output_dir is None:
            output_dir = Config.OUTPUT_DIR
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"google_maps_results_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        filepath = output_dir / filename
        
        try:
            # Get all unique keys from all dictionaries
            fieldnames = set()
            for item in data:
                fieldnames.update(item.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Exported {len(data)} records to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    @staticmethod
    def to_excel(data: List[Dict], filename: Optional[str] = None, output_dir: Optional[Path] = None) -> str:
        """
        Export data to Excel file
        
        Args:
            data: List of dictionaries to export
            filename: Output filename (auto-generated if None)
            output_dir: Output directory (uses config if None)
            
        Returns:
            Path to created file
        """
        logger = Logger.get_logger("DataExporter")
        
        if not data:
            logger.warning("No data to export")
            return None
        
        # Setup output path
        if output_dir is None:
            output_dir = Config.OUTPUT_DIR
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"google_maps_results_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        filepath = output_dir / filename
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Export to Excel with formatting
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Results']
                for column in df:
                    column_length = max(df[column].astype(str).map(len).max(), len(column))
                    col_idx = df.columns.get_loc(column)
                    worksheet.column_dimensions[chr(65 + col_idx)].width = min(column_length + 2, 50)
            
            logger.info(f"Exported {len(data)} records to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise
    
    @staticmethod
    def to_json(data: List[Dict], filename: Optional[str] = None, output_dir: Optional[Path] = None) -> str:
        """
        Export data to JSON file
        
        Args:
            data: List of dictionaries to export
            filename: Output filename (auto-generated if None)
            output_dir: Output directory (uses config if None)
            
        Returns:
            Path to created file
        """
        import json
        
        logger = Logger.get_logger("DataExporter")
        
        if not data:
            logger.warning("No data to export")
            return None
        
        # Setup output path
        if output_dir is None:
            output_dir = Config.OUTPUT_DIR
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"google_maps_results_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(data)} records to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
