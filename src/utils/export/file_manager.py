"""
File management utilities for export operations.
"""
from pathlib import Path
from typing import Optional
from datetime import datetime
from src.core.config import Config
from src.utils.logging import Logger


class FileManager:
    """Handles file path operations and directory management for exports."""
    
    def __init__(self):
        self.logger = Logger.get_logger("FileManager")
    
    def setup_output_directory(self, output_dir: Optional[Path] = None) -> Path:
        """
        Setup and return the output directory.
        """
        if output_dir is None:
            output_dir = Config.OUTPUT_DIR
        else:
            output_dir = Path(output_dir)
        
        try:
            output_dir.mkdir(exist_ok=True, parents=True)
            self.logger.debug(f"Output directory ready: {output_dir}")
            return output_dir
        except Exception as e:
            self.logger.error(f"Failed to create output directory {output_dir}: {e}")
            raise
    
    def generate_filename(self, format_type: str, filename: Optional[str] = None) -> str:
        """
        Generate filename with proper extension.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"google_maps_results_{timestamp}"
        
        # Add appropriate extension
        extensions = {
            'csv': '.csv',
            'excel': '.xlsx',
            'json': '.json'
        }
        
        extension = extensions.get(format_type.lower())
        if extension and not filename.endswith(extension):
            filename += extension
        
        return filename
    
    def get_file_path(self, filename: str, output_dir: Path) -> Path:
        """
        Get full file path.
        """
        return output_dir / filename
    
    def validate_file_path(self, file_path: Path) -> bool:
        """
        Validate that the file path is writable.
        """
        try:
            # Check if parent directory exists and is writable
            parent_dir = file_path.parent
            if not parent_dir.exists():
                parent_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write permission by creating a temporary file
            test_file = parent_dir / f".test_write_{datetime.now().timestamp()}"
            test_file.touch()
            test_file.unlink()
            
            return True
        except Exception as e:
            self.logger.error(f"File path validation failed for {file_path}: {e}")
            return False
    
    def ensure_unique_filename(self, file_path: Path) -> Path:
        """
        Ensure filename is unique by adding suffix if file exists.
        """
        if not file_path.exists():
            return file_path
        
        base_name = file_path.stem
        extension = file_path.suffix
        parent_dir = file_path.parent
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter}{extension}"
            new_path = parent_dir / new_name
            if not new_path.exists():
                self.logger.debug(f"Generated unique filename: {new_path}")
                return new_path
            counter += 1
