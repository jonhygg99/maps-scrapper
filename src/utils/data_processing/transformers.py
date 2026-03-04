"""
Data transformation components.
"""
import re
from typing import Optional, Any
from .base import BaseTransformer


class RatingTransformer(BaseTransformer):
    """Transforms rating strings to normalized float values."""
    
    def __init__(self, min_rating: float = 0.0, max_rating: float = 5.0):
        super().__init__("RatingTransformer")
        self.min_rating = min_rating
        self.max_rating = max_rating
    
    def transform(self, value: Any) -> Optional[float]:
        """Extract and normalize rating from string."""
        if value is None:
            return None
        
        try:
            # If already a number, just validate range
            if isinstance(value, (int, float)):
                rating = float(value)
                return rating if self.min_rating <= rating <= self.max_rating else None
            
            # Extract first number from string (e.g., "4.5" from "4.5 stars")
            text = str(value)
            match = re.search(r'(-?\d+\.?\d*)', text)
            
            if match:
                rating = float(match.group(1))
                return rating if self.min_rating <= rating <= self.max_rating else None
            
        except (ValueError, TypeError):
            pass
        
        return None


class NumberTransformer(BaseTransformer):
    """Transforms text to integer values."""
    
    def __init__(self, remove_non_digits: bool = True):
        super().__init__("NumberTransformer")
        self.remove_non_digits = remove_non_digits
    
    def transform(self, value: Any) -> Optional[int]:
        """Extract integer from text."""
        if value is None:
            return None
        
        try:
            # If already a number, convert to int
            if isinstance(value, (int, float)):
                return int(value)
            
            text = str(value)
            
            if self.remove_non_digits:
                # Remove all non-digit characters
                number_str = re.sub(r'[^\d]', '', text)
            else:
                # Extract first number found
                match = re.search(r'-?\d+', text)
                number_str = match.group(1) if match else ''
            
            if number_str:
                return int(number_str)
                
        except (ValueError, TypeError):
            pass
        
        return None


class TextNormalizer(BaseTransformer):
    """Normalizes text by applying various transformations."""
    
    def __init__(self, 
                 lowercase: bool = False,
                 uppercase: bool = False,
                 title_case: bool = False,
                 remove_extra_spaces: bool = True):
        super().__init__("TextNormalizer")
        self.lowercase = lowercase
        self.uppercase = uppercase
        self.title_case = title_case
        self.remove_extra_spaces = remove_extra_spaces
        
        # Validate that only one case transformation is specified
        case_transforms = [self.lowercase, self.uppercase, self.title_case]
        if sum(case_transforms) > 1:
            raise ValueError("Only one case transformation can be specified")
    
    def transform(self, value: Any) -> Optional[str]:
        """Apply text normalization transformations."""
        if value is None:
            return None
        
        text = str(value)
        
        # Apply case transformation
        if self.lowercase:
            text = text.lower()
        elif self.uppercase:
            text = text.upper()
        elif self.title_case:
            text = text.title()
        
        # Remove extra spaces
        if self.remove_extra_spaces:
            text = ' '.join(text.split())
        
        return text if text else None


class CategoryNormalizer(BaseTransformer):
    """Normalizes category names by standardizing format."""
    
    def __init__(self, separator: str = ', ', remove_duplicates: bool = True):
        super().__init__("CategoryNormalizer")
        self.separator = separator
        self.remove_duplicates = remove_duplicates
    
    def transform(self, value: Any) -> Optional[str]:
        """Normalize category string."""
        if not value:
            return None
        
        text = str(value).strip()
        
        # Split by common separators
        categories = re.split(r'[,;|]', text)
        
        # Clean and normalize each category
        normalized = []
        seen = set()
        
        for category in categories:
            cat = category.strip().title()
            
            if self.remove_duplicates:
                if cat.lower() not in seen:
                    seen.add(cat.lower())
                    normalized.append(cat)
            else:
                normalized.append(cat)
        
        return self.separator.join(normalized) if normalized else None


class AddressNormalizer(BaseTransformer):
    """Normalizes address strings."""
    
    def __init__(self, country_code: Optional[str] = None):
        super().__init__("AddressNormalizer")
        self.country_code = country_code
    
    def transform(self, value: Any) -> Optional[str]:
        """Normalize address format."""
        if not value:
            return None
        
        address = str(value).strip()
        
        # Basic normalization
        address = ' '.join(address.split())  # Normalize whitespace
        
        # Add country code if specified and not present
        if self.country_code and self.country_code.upper() not in address.upper():
            address = f"{address}, {self.country_code.upper()}"
        
        return address if address else None
