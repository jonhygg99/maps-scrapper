"""
Data Processing Module
Provides modular components for data validation, cleaning, and transformation.
The DataProcessor class serves as the main interface for backward compatibility.
"""
from typing import List, Dict, Optional
from src.utils.logging import Logger

# Import all modular components
from .base import BaseProcessor, BaseValidator, BaseCleaner, BaseTransformer
from .validators import RatingValidator, URLValidator, PhoneValidator, TextValidator, NumberValidator
from .cleaners import TextCleaner, PhoneCleaner, URLCleaner, NumberCleaner, WhitespaceCleaner
from .transformers import RatingTransformer, NumberTransformer, TextNormalizer, CategoryNormalizer, AddressNormalizer
from .business_processor import BusinessDataProcessor
from .filters import RatingFilter, DuplicateFilter, FieldFilter, NullFilter, TextFilter, RangeFilter
from .sorters import RatingSorter, FieldSorter, MultiFieldSorter, TextSorter, LengthSorter
from .pipeline import ProcessingPipeline, BatchProcessingPipeline, ConditionalPipeline, ParallelPipeline


class DataProcessor:
    """Process and clean scraped data using modular components."""
    
    def __init__(self):
        self.logger = Logger.get_logger("DataProcessor")
        self.business_processor = BusinessDataProcessor()
        self._setup_default_pipeline()
    
    def _setup_default_pipeline(self):
        """Setup the default processing pipeline."""
        self.cleaning_pipeline = ProcessingPipeline("DataCleaning")
        self.cleaning_pipeline.add_step(self.business_processor)
        
        self.filtering_pipeline = ProcessingPipeline("DataFiltering")
        
        self.sorting_pipeline = ProcessingPipeline("DataSorting")
    
    def clean_results(self, results: List[Dict]) -> List[Dict]:
        """Clean and validate scraped results."""
        if not results:
            return []
        
        cleaned = []
        
        for i, result in enumerate(results):
            try:
                cleaned_result = self.business_processor.process(result)
                if cleaned_result:
                    cleaned.append(cleaned_result)
            except Exception as e:
                self.logger.warning(f"Error cleaning result {i}: {e}")
                continue
        
        self.logger.info(f"Cleaned {len(cleaned)} out of {len(results)} results")
        return cleaned
    
    def _clean_business_data(self, data: Dict) -> Optional[Dict]:
        """Clean individual business data (legacy method for backward compatibility)."""
        return self.business_processor.process(data)
    
    # Legacy methods for backward compatibility
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean text field (legacy method)."""
        cleaner = TextCleaner()
        return cleaner.clean(text)
    
    def _extract_rating(self, rating_str: str) -> Optional[float]:
        """Extract numeric rating from string (legacy method)."""
        transformer = RatingTransformer()
        return transformer.transform(rating_str)
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract integer number from string (legacy method)."""
        transformer = NumberTransformer()
        return transformer.transform(text)
    
    def _clean_phone(self, phone: Optional[str]) -> Optional[str]:
        """Clean phone number (legacy method)."""
        cleaner = PhoneCleaner()
        return cleaner.clean(phone)
    
    def _clean_url(self, url: Optional[str]) -> Optional[str]:
        """Clean and validate URL (legacy method)."""
        cleaner = URLCleaner()
        return cleaner.clean(url)
    
    def remove_duplicates(self, results: List[Dict], key: str = 'name') -> List[Dict]:
        """Remove duplicate entries based on a key."""
        duplicate_filter = DuplicateFilter(key=key, case_sensitive=False)
        return duplicate_filter.process(results)
    
    def filter_by_rating(self, results: List[Dict], min_rating: float = 0.0) -> List[Dict]:
        """Filter results by minimum rating."""
        rating_filter = RatingFilter(min_rating=min_rating)
        return rating_filter.process(results)
    
    def sort_by_rating(self, results: List[Dict], descending: bool = True) -> List[Dict]:
        """Sort results by rating."""
        rating_sorter = RatingSorter(descending=descending)
        return rating_sorter.process(results)
    
    # New methods using the modular pipeline system
    def create_processing_pipeline(self) -> ProcessingPipeline:
        """Create a configurable processing pipeline."""
        return ProcessingPipeline("CustomDataProcessing")
    
    def process_with_pipeline(self, results: List[Dict], pipeline: ProcessingPipeline) -> List[Dict]:
        """Process results using a custom pipeline."""
        # Add business processor as first step if not already present
        if not pipeline.steps:
            pipeline.add_step(self.business_processor)
        
        return pipeline.process(results)
    
    def get_business_processor(self) -> BusinessDataProcessor:
        """Get the underlying business processor for advanced usage."""
        return self.business_processor


__all__ = [
    # Main interface
    'DataProcessor',
    
    # Base classes
    'BaseProcessor',
    'BaseValidator', 
    'BaseCleaner',
    'BaseTransformer',
    
    # Validators
    'RatingValidator',
    'URLValidator', 
    'PhoneValidator',
    'TextValidator',
    'NumberValidator',
    
    # Cleaners
    'TextCleaner',
    'PhoneCleaner',
    'URLCleaner',
    'NumberCleaner',
    'WhitespaceCleaner',
    
    # Transformers
    'RatingTransformer',
    'NumberTransformer',
    'TextNormalizer',
    'CategoryNormalizer',
    'AddressNormalizer',
    
    # Processors
    'BusinessDataProcessor',
    
    # Filters
    'RatingFilter',
    'DuplicateFilter',
    'FieldFilter',
    'NullFilter',
    'TextFilter',
    'RangeFilter',
    
    # Sorters
    'RatingSorter',
    'FieldSorter',
    'MultiFieldSorter',
    'TextSorter',
    'LengthSorter',
    
    # Pipelines
    'ProcessingPipeline',
    'BatchProcessingPipeline',
    'ConditionalPipeline',
    'ParallelPipeline'
]
