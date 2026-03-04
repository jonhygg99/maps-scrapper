"""
Base classes for data export functionality.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass
from src.utils.logger import Logger


@dataclass
class ExportResult:
    """Container for export operation results."""
    success: bool
    file_path: Optional[str] = None
    records_exported: int = 0
    errors: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the result."""
        self.metadata[key] = value


class BaseExporter(ABC):
    """Abstract base class for all data exporters."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = Logger.get_logger(f"{self.__class__.__name__}")
    
    @abstractmethod
    def export(self, data: List[Dict], filename: Optional[str] = None, 
               output_dir: Optional[Path] = None) -> ExportResult:
        """
        Export data to the specific format.
        """
        pass
    
    def _validate_data(self, data: List[Dict]) -> bool:
        """Validate input data."""
        if not data:
            self.logger.warning("No data to export")
            return False
        
        if not isinstance(data, list):
            self.logger.error("Data must be a list of dictionaries")
            return False
        
        if not all(isinstance(item, dict) for item in data):
            self.logger.error("All data items must be dictionaries")
            return False
        
        return True
    
    def _create_export_result(self, success: bool, file_path: Optional[str] = None, 
                             records: int = 0, errors: List[str] = None) -> ExportResult:
        """Create a standardized export result."""
        return ExportResult(
            success=success,
            file_path=file_path,
            records_exported=records,
            errors=errors or [],
            metadata={'exporter': self.name}
        )
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
