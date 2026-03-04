"""
Data filtering components.
"""
from typing import List, Dict, Any, Callable, Optional
from .base import BaseProcessor


class RatingFilter(BaseProcessor):
    """Filters data by minimum rating threshold."""
    
    def __init__(self, min_rating: float = 0.0):
        super().__init__("RatingFilter")
        self.min_rating = min_rating
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter results by minimum rating."""
        filtered = [
            item for item in data
            if item.get('rating') is not None and item.get('rating') >= self.min_rating
        ]
        
        if len(filtered) < len(data):
            self.logger.info(f"Filtered to {len(filtered)} results with rating >= {self.min_rating}")
        
        return filtered


class DuplicateFilter(BaseProcessor):
    """Filters duplicate entries based on specified key."""
    
    def __init__(self, key: str = 'name', case_sensitive: bool = True):
        super().__init__("DuplicateFilter")
        self.key = key
        self.case_sensitive = case_sensitive
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entries based on key."""
        seen = set()
        unique = []
        
        for item in data:
            identifier = item.get(self.key)
            if identifier:
                if not self.case_sensitive:
                    identifier = str(identifier).lower()
                
                if identifier not in seen:
                    seen.add(identifier)
                    unique.append(item)
            else:
                # Include items without the key
                unique.append(item)
        
        if len(unique) < len(data):
            self.logger.info(f"Removed {len(data) - len(unique)} duplicates")
        
        return unique


class FieldFilter(BaseProcessor):
    """Filters data based on field values."""
    
    def __init__(self, field: str, predicate: Callable[[Any], bool]):
        super().__init__("FieldFilter")
        self.field = field
        self.predicate = predicate
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter data based on field predicate."""
        filtered = [
            item for item in data
            if self.field in item and self.predicate(item[self.field])
        ]
        
        return filtered


class NullFilter(BaseProcessor):
    """Filters out entries with null values in specified fields."""
    
    def __init__(self, fields: List[str], allow_null: bool = False):
        super().__init__("NullFilter")
        self.fields = fields
        self.allow_null = allow_null
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter entries based on null values in specified fields."""
        if self.allow_null:
            # Keep entries where any of the specified fields are null
            filtered = [
                item for item in data
                if any(item.get(field) is None for field in self.fields)
            ]
        else:
            # Keep entries where all specified fields are not null
            filtered = [
                item for item in data
                if all(item.get(field) is not None for field in self.fields)
            ]
        
        return filtered


class TextFilter(BaseProcessor):
    """Filters data based on text content matching."""
    
    def __init__(self, field: str, pattern: str, case_sensitive: bool = False, 
                 regex: bool = False):
        super().__init__("TextFilter")
        self.field = field
        self.pattern = pattern
        self.case_sensitive = case_sensitive
        self.regex = regex
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter data based on text pattern matching."""
        import re
        
        filtered = []
        
        for item in data:
            field_value = item.get(self.field)
            if field_value is None:
                continue
            
            text = str(field_value)
            
            if not self.case_sensitive:
                text = text.lower()
                pattern = self.pattern.lower()
            
            if self.regex:
                try:
                    if re.search(pattern, text):
                        filtered.append(item)
                except re.error:
                    # If regex is invalid, fall back to simple string matching
                    if pattern in text:
                        filtered.append(item)
            else:
                if pattern in text:
                    filtered.append(item)
        
        return filtered


class RangeFilter(BaseProcessor):
    """Filters numeric data within specified range."""
    
    def __init__(self, field: str, min_value: Optional[float] = None, 
                 max_value: Optional[float] = None):
        super().__init__("RangeFilter")
        self.field = field
        self.min_value = min_value
        self.max_value = max_value
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter data within numeric range."""
        filtered = []
        
        for item in data:
            field_value = item.get(self.field)
            if field_value is None:
                continue
            
            try:
                value = float(field_value)
                
                if self.min_value is not None and value < self.min_value:
                    continue
                
                if self.max_value is not None and value > self.max_value:
                    continue
                
                filtered.append(item)
                
            except (ValueError, TypeError):
                continue
        
        return filtered
