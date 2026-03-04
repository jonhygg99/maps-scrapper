"""
Data validation components.
"""
import re
from typing import Optional, Any
from urllib.parse import urlparse
from .base import BaseValidator


class RatingValidator(BaseValidator):
    """Validates rating values."""
    
    def __init__(self, min_rating: float = 0.0, max_rating: float = 5.0):
        super().__init__("RatingValidator")
        self.min_rating = min_rating
        self.max_rating = max_rating
    
    def is_valid(self, value: Any) -> bool:
        """Check if rating is within valid range."""
        if value is None:
            return True  # None is allowed
        
        try:
            rating = float(value)
            return self.min_rating <= rating <= self.max_rating
        except (ValueError, TypeError):
            return False


class URLValidator(BaseValidator):
    """Validates URL format."""
    
    def __init__(self, require_scheme: bool = True):
        super().__init__("URLValidator")
        self.require_scheme = require_scheme
    
    def is_valid(self, value: Any) -> bool:
        """Check if URL has valid format."""
        if not value:
            return False
        
        try:
            url = str(value).strip()
            if self.require_scheme and not (url.startswith('http://') or url.startswith('https://')):
                return False
            
            parsed = urlparse(url)
            return bool(parsed.netloc)
        except Exception:
            return False


class PhoneValidator(BaseValidator):
    """Validates phone number format."""
    
    def __init__(self, min_digits: int = 7):
        super().__init__("PhoneValidator")
        self.min_digits = min_digits
    
    def is_valid(self, value: Any) -> bool:
        """Check if phone number contains enough digits."""
        if not value:
            return False
        
        # Extract digits from the string
        digits = re.sub(r'[^\d]', '', str(value))
        return len(digits) >= self.min_digits


class TextValidator(BaseValidator):
    """Validates text content."""
    
    def __init__(self, min_length: int = 1, max_length: Optional[int] = None):
        super().__init__("TextValidator")
        self.min_length = min_length
        self.max_length = max_length
    
    def is_valid(self, value: Any) -> bool:
        """Check if text meets length requirements."""
        if not value:
            return self.min_length == 0
        
        text = str(value).strip()
        length = len(text)
        
        if length < self.min_length:
            return False
        
        if self.max_length is not None and length > self.max_length:
            return False
        
        return True


class NumberValidator(BaseValidator):
    """Validates numeric values."""
    
    def __init__(self, min_value: Optional[float] = None, max_value: Optional[float] = None):
        super().__init__("NumberValidator")
        self.min_value = min_value
        self.max_value = max_value
    
    def is_valid(self, value: Any) -> bool:
        """Check if number is within valid range."""
        if value is None:
            return True  # None is allowed
        
        try:
            number = float(value)
            
            if self.min_value is not None and number < self.min_value:
                return False
            
            if self.max_value is not None and number > self.max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
