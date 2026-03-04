"""
Data sorting components.
"""
from typing import List, Dict, Any, Callable, Optional
from .base import BaseProcessor


class RatingSorter(BaseProcessor):
    """Sorts data by rating field."""
    
    def __init__(self, descending: bool = True, null_value: float = -1):
        super().__init__("RatingSorter")
        self.descending = descending
        self.null_value = null_value
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort data by rating."""
        def get_rating(item):
            rating = item.get('rating')
            return rating if rating is not None else self.null_value
        
        return sorted(data, key=get_rating, reverse=self.descending)


class FieldSorter(BaseProcessor):
    """Sorts data by specified field."""
    
    def __init__(self, field: str, descending: bool = False, 
                 key_func: Optional[Callable[[Any], Any]] = None,
                 null_value: Any = None):
        super().__init__("FieldSorter")
        self.field = field
        self.descending = descending
        self.key_func = key_func
        self.null_value = null_value
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort data by specified field."""
        def get_sort_key(item):
            value = item.get(self.field)
            
            if value is None:
                return self.null_value
            
            if self.key_func:
                return self.key_func(value)
            
            return value
        
        return sorted(data, key=get_sort_key, reverse=self.descending)


class MultiFieldSorter(BaseProcessor):
    """Sorts data by multiple fields with priority."""
    
    def __init__(self, sort_fields: List[tuple]):
        """
        Initialize with list of (field, descending, key_func, null_value) tuples.
        
        Args:
            sort_fields: List of tuples with sorting configuration
                        Example: [('rating', True), ('name', False)]
        """
        super().__init__("MultiFieldSorter")
        self.sort_fields = sort_fields
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort data by multiple fields."""
        def get_sort_key(item):
            key = []
            for field_config in self.sort_fields:
                if len(field_config) == 1:
                    field = field_config[0]
                    descending = False
                    key_func = None
                    null_value = None
                elif len(field_config) == 2:
                    field, descending = field_config
                    key_func = None
                    null_value = None
                elif len(field_config) == 3:
                    field, descending, key_func = field_config
                    null_value = None
                else:
                    field, descending, key_func, null_value = field_config
                
                value = item.get(field)
                if value is None:
                    key.append(null_value)
                elif key_func:
                    key.append(key_func(value))
                else:
                    key.append(value)
            
            return tuple(key)
        
        # Determine reverse flag based on first field's descending setting
        reverse = self.sort_fields[0][1] if len(self.sort_fields) > 0 else False
        
        return sorted(data, key=get_sort_key, reverse=reverse)


class TextSorter(BaseProcessor):
    """Sorts text data with various options."""
    
    def __init__(self, field: str, descending: bool = False, 
                 case_sensitive: bool = True, ignore_articles: bool = False):
        super().__init__("TextSorter")
        self.field = field
        self.descending = descending
        self.case_sensitive = case_sensitive
        self.ignore_articles = ignore_articles
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort text data with specified options."""
        def get_text_key(item):
            text = item.get(self.field, '')
            
            if not isinstance(text, str):
                text = str(text)
            
            if not self.case_sensitive:
                text = text.lower()
            
            if self.ignore_articles:
                # Remove leading articles (a, an, the)
                articles = ['a ', 'an ', 'the ']
                for article in articles:
                    if text.startswith(article):
                        text = text[len(article):]
                        break
            
            return text
        
        return sorted(data, key=get_text_key, reverse=self.descending)


class LengthSorter(BaseProcessor):
    """Sorts data by length of specified field."""
    
    def __init__(self, field: str, descending: bool = False):
        super().__init__("LengthSorter")
        self.field = field
        self.descending = descending
    
    def process(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort data by length of field."""
        def get_length(item):
            value = item.get(self.field)
            if value is None:
                return 0
            return len(str(value))
        
        return sorted(data, key=get_length, reverse=self.descending)
