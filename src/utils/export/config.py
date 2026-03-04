"""
Configuration settings for export operations.
"""
from typing import List, Dict, Any


class ExportConfig:
    """Configuration constants and settings for export operations."""
    
    # Default column order for CSV exports
    DEFAULT_CSV_COLUMNS = [
        'name', 'category', 'phone', 'website', 'reviews', 'rating', 'address', 
        'hours', 'introduction', 'in_store_pickup', 'price_level', 'store_delivery', 'store_shopping'
    ]
    
    # File format mappings
    FILE_EXTENSIONS = {
        'csv': '.csv',
        'excel': '.xlsx',
        'json': '.json'
    }
    
    # MIME types
    MIME_TYPES = {
        'csv': 'text/csv',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'json': 'application/json'
    }
    
    # Excel formatting settings
    EXCEL_CONFIG = {
        'max_column_width': 50,
        'min_column_width': 10,
        'auto_adjust_widths': True,
        'sheet_name': 'Results'
    }
    
    # JSON export settings
    JSON_CONFIG = {
        'indent': 2,
        'ensure_ascii': False,
        'sort_keys': False
    }
    
    # CSV export settings
    CSV_CONFIG = {
        'encoding': 'utf-8-sig',
        'delimiter': ',',
        'quote_char': '"',
        'escape_char': None,
        'lineterminator': '\n'
    }
    
    # Filename patterns
    FILENAME_PATTERNS = {
        'default': 'google_maps_results_{timestamp}',
        'businesses': 'businesses_{timestamp}',
        'locations': 'locations_{timestamp}',
        'custom': '{custom_name}_{timestamp}'
    }
    
    # Default export settings
    DEFAULT_SETTINGS = {
        'include_empty_fields': True,
        'validate_data': True,
        'create_unique_filenames': False,
        'backup_existing_files': False
    }
    
    @classmethod
    def get_columns_for_format(cls, format_type: str) -> List[str]:
        """
        Get column definitions for a specific format.
        """
        if format_type.lower() in ['csv', 'excel']:
            return cls.DEFAULT_CSV_COLUMNS.copy()
        return []  # JSON doesn't have fixed column order
    
    @classmethod
    def get_config_for_format(cls, format_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific format.
        """
        configs = {
            'csv': cls.CSV_CONFIG,
            'excel': cls.EXCEL_CONFIG,
            'json': cls.JSON_CONFIG
        }
        return configs.get(format_type.lower(), {})
    
    @classmethod
    def get_file_extension(cls, format_type: str) -> str:
        """
        Get file extension for a format.
        """
        return cls.FILE_EXTENSIONS.get(format_type.lower(), '')
    
    @classmethod
    def get_mime_type(cls, format_type: str) -> str:
        """
        Get MIME type for a format.
        """
        return cls.MIME_TYPES.get(format_type.lower(), 'application/octet-stream')
