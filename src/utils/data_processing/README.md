# Data Processing Module

This module provides a modular, extensible system for data validation, cleaning, and transformation. It replaces the monolithic DataProcessor with a collection of specialized components that can be combined in flexible pipelines.

## Architecture

The `DataProcessor` class is now the main interface of this module, defined directly in `__init__.py`. This follows Python best practices for package design where the primary interface is available at the package level.

### Main Interface

- **DataProcessor** (in `__init__.py`): Main interface for backward compatibility

### Base Classes (in `base.py`)

- **BaseProcessor**: Abstract base for all processing components
- **BaseValidator**: For data validation logic
- **BaseCleaner**: For data cleaning operations
- **BaseTransformer**: For data transformation logic

### Core Components

#### Validators (`validators.py`)

- `RatingValidator`: Validates rating values within specified ranges
- `URLValidator`: Validates URL format and structure
- `PhoneValidator`: Validates phone number format
- `TextValidator`: Validates text length and content
- `NumberValidator`: Validates numeric ranges

#### Cleaners (`cleaners.py`)

- `TextCleaner`: Normalizes text, removes unwanted characters
- `PhoneCleaner`: Cleans and formats phone numbers
- `URLCleaner`: Normalizes URLs with proper schemes
- `NumberCleaner`: Extracts numeric values from text
- `WhitespaceCleaner`: Normalizes whitespace in text

#### Transformers (`transformers.py`)

- `RatingTransformer`: Extracts and normalizes ratings
- `NumberTransformer`: Extracts integers from text
- `TextNormalizer`: Applies text case transformations
- `CategoryNormalizer`: Standardizes category names
- `AddressNormalizer`: Normalizes address formats

#### Filters (`filters.py`)

- `RatingFilter`: Filters by minimum rating
- `DuplicateFilter`: Removes duplicate entries
- `FieldFilter`: Filters based on field predicates
- `NullFilter`: Filters null/empty values
- `TextFilter`: Text pattern matching
- `RangeFilter`: Numeric range filtering

#### Sorters (`sorters.py`)

- `RatingSorter`: Sorts by rating values
- `FieldSorter`: Generic field-based sorting
- `MultiFieldSorter`: Multi-criteria sorting
- `TextSorter`: Text-based sorting with options
- `LengthSorter`: Sorts by field length

#### Pipeline System (`pipeline.py`)

- **ProcessingPipeline**: Sequential processing with error handling
- **BatchProcessingPipeline**: Optimized for list processing
- **ConditionalPipeline**: Branching logic support
- **ParallelPipeline**: Concurrent processing capabilities

### Specialized Processors

#### BusinessDataProcessor (`business_processor.py`)

Specialized processor for business data that combines multiple cleaners and validators:

- Name validation and cleaning
- Rating extraction and validation
- Review count processing
- Category normalization
- Address standardization
- Phone number cleaning
- URL validation

## Usage Examples

### Basic Usage (Backward Compatible)

```python
from src.utils.data_processing import DataProcessor

processor = DataProcessor()
cleaned_data = processor.clean_results(raw_data)
unique_data = processor.remove_duplicates(cleaned_data)
filtered_data = processor.filter_by_rating(unique_data, min_rating=4.0)
sorted_data = processor.sort_by_rating(filtered_data)
```

### Advanced Pipeline Usage

```python
from src.utils.data_processing import (
    BatchProcessingPipeline, BusinessDataProcessor,
    DuplicateFilter, RatingFilter, RatingSorter
)

# Create custom pipeline
pipeline = BatchProcessingPipeline("CustomProcessing")
pipeline.add_step(BusinessDataProcessor())
pipeline.add_step(DuplicateFilter(key='name', case_sensitive=False))
pipeline.add_step(RatingFilter(min_rating=3.5))
pipeline.add_step(RatingSorter(descending=True))

# Process data
results = pipeline.process(raw_data)
```

### Individual Component Usage

```python
from src.utils.data_processing import TextCleaner, RatingValidator

# Clean text
cleaner = TextCleaner(remove_special_chars=True)
clean_text = cleaner.clean("  Some messy text!!  ")

# Validate rating
validator = RatingValidator(min_rating=0.0, max_rating=5.0)
is_valid = validator.is_valid(4.5)
```

## Benefits

1. **Modularity**: Each component has a single responsibility
2. **Extensibility**: Easy to add new validators, cleaners, or transformers
3. **Testability**: Individual components can be unit tested
4. **Flexibility**: Components can be combined in various ways
5. **Maintainability**: Clear separation of concerns
6. **Backward Compatibility**: Existing code continues to work
7. **Performance**: Optimized pipeline processing for large datasets

## Migration Guide

The refactored DataProcessor maintains full backward compatibility. Existing code will continue to work without changes:

```python
# This still works exactly as before (note the new import path)
from src.utils.data_processing import DataProcessor

processor = DataProcessor()
cleaned = processor.clean_results(data)
```

For new code, consider using the pipeline system for better flexibility:

```python
# New recommended approach
pipeline = processor.create_processing_pipeline()
pipeline.add_step(processor.get_business_processor())
# ... add more steps as needed
results = processor.process_with_pipeline(data, pipeline)
```

## Configuration

Components can be configured with various parameters:

```python
# Custom validator
validator = RatingValidator(min_rating=1.0, max_rating=5.0)

# Custom cleaner
cleaner = TextCleaner(
    remove_special_chars=True,
    allowed_chars=r'\w\s\-.,&()\'"'
)

# Custom filter
filter = DuplicateFilter(key='name', case_sensitive=False)
```

## Error Handling

The pipeline system provides multiple error handling modes:

- `'continue'`: Skip errors and continue processing
- `'stop'`: Stop on first error
- `'collect'`: Collect all errors but continue processing

```python
pipeline = ProcessingPipeline("MyPipeline")
pipeline.set_error_handling('collect')
```
