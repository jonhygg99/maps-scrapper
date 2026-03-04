"""
Base classes for data processing components.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from src.utils.logging import Logger


class BaseProcessor(ABC):
    """Abstract base class for all data processors."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = Logger.get_logger(f"{self.__class__.__name__}")
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process the input data and return the result."""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class BaseValidator(BaseProcessor):
    """Abstract base class for data validators."""
    
    @abstractmethod
    def is_valid(self, value: Any) -> bool:
        """Check if the value is valid."""
        pass
    
    def process(self, data: Any) -> bool:
        """Validate the data and return True if valid."""
        return self.is_valid(data)


class BaseCleaner(BaseProcessor):
    """Abstract base class for data cleaners."""
    
    @abstractmethod
    def clean(self, value: Any) -> Any:
        """Clean the input value."""
        pass
    
    def process(self, data: Any) -> Any:
        """Clean the data and return the result."""
        return self.clean(data)


class BaseTransformer(BaseProcessor):
    """Abstract base class for data transformers."""
    
    @abstractmethod
    def transform(self, value: Any) -> Any:
        """Transform the input value."""
        pass
    
    def process(self, data: Any) -> Any:
        """Transform the data and return the result."""
        return self.transform(data)


class ProcessingResult:
    """Container for processing results with metadata."""
    
    def __init__(self, data: Any, success: bool = True, errors: Optional[List[str]] = None):
        self.data = data
        self.success = success
        self.errors = errors or []
        self.metadata = {}
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the result."""
        self.metadata[key] = value
