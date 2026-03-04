"""
Data cleaning components.
"""
import re
from typing import Optional, Any
from urllib.parse import urlparse
from .base import BaseCleaner


class TextCleaner(BaseCleaner):
    """Cleans text fields by removing extra whitespace and unwanted characters."""
    
    def __init__(self, remove_special_chars: bool = True, allowed_chars: str = r'\w\s\-.,&()\'"'):
        super().__init__("TextCleaner")
        self.remove_special_chars = remove_special_chars
        self.allowed_chars = allowed_chars
    
    def clean(self, value: Any) -> Optional[str]:
        """Clean text by normalizing whitespace and removing unwanted characters."""
        if not value:
            return None
        
        text = str(value)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters if requested
        if self.remove_special_chars:
            text = re.sub(f'[^{self.allowed_chars}]', '', text)
        
        # Return None if empty after cleaning
        text = text.strip()
        return text if text else None


class PhoneCleaner(BaseCleaner):
    """Cleans phone numbers by extracting digits and common formatting."""
    
    def __init__(self, keep_formatting: bool = True):
        super().__init__("PhoneCleaner")
        self.keep_formatting = keep_formatting
    
    def clean(self, value: Any) -> Optional[str]:
        """Clean phone number by extracting digits and preserving basic formatting."""
        if not value:
            return None
        
        phone = str(value)
        
        if self.keep_formatting:
            # Keep digits and common phone formatting characters
            phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
            # Normalize whitespace
            phone = ' '.join(phone.split())
        else:
            # Extract only digits
            phone = re.sub(r'[^\d]', '', phone)
        
        return phone if phone else None


class URLCleaner(BaseCleaner):
    """Cleans and normalizes URLs."""
    
    def __init__(self, ensure_scheme: bool = True, default_scheme: str = 'https'):
        super().__init__("URLCleaner")
        self.ensure_scheme = ensure_scheme
        self.default_scheme = default_scheme
    
    def clean(self, value: Any) -> Optional[str]:
        """Clean URL by ensuring proper scheme and format."""
        if not value:
            return None
        
        url = str(value).strip()
        
        # Add scheme if missing and ensure_scheme is True
        if self.ensure_scheme and not url.startswith(('http://', 'https://')):
            url = f"{self.default_scheme}://{url}"
        
        # Parse and rebuild URL to normalize
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            
            # Rebuild URL with normalized components
            cleaned = f"{parsed.scheme}://{parsed.netloc}"
            if parsed.path:
                cleaned += parsed.path
            if parsed.query:
                cleaned += f"?{parsed.query}"
            if parsed.fragment:
                cleaned += f"#{parsed.fragment}"
            
            return cleaned
        except Exception:
            return None


class NumberCleaner(BaseCleaner):
    """Cleans numeric values by extracting numbers from text."""
    
    def __init__(self, remove_commas: bool = True, allow_floats: bool = True):
        super().__init__("NumberCleaner")
        self.remove_commas = remove_commas
        self.allow_floats = allow_floats
    
    def clean(self, value: Any) -> Optional[float]:
        """Extract numeric value from text."""
        if value is None:
            return None
        
        text = str(value)
        
        # Remove commas if requested
        if self.remove_commas:
            text = text.replace(',', '')
        
        # Extract number using regex
        pattern = r'-?\d+\.?\d*' if self.allow_floats else r'-?\d+'
        match = re.search(pattern, text)
        
        if match:
            try:
                return float(match.group()) if self.allow_floats else int(match.group())
            except ValueError:
                pass
        
        return None


class WhitespaceCleaner(BaseCleaner):
    """Specialized cleaner for normalizing whitespace."""
    
    def __init__(self, normalize_spaces: bool = True, strip_edges: bool = True):
        super().__init__("WhitespaceCleaner")
        self.normalize_spaces = normalize_spaces
        self.strip_edges = strip_edges
    
    def clean(self, value: Any) -> Optional[str]:
        """Normalize whitespace in text."""
        if not value:
            return None
        
        text = str(value)
        
        if self.strip_edges:
            text = text.strip()
        
        if self.normalize_spaces:
            text = ' '.join(text.split())
        
        return text if text else None
