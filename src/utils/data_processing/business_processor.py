"""
Specialized processor for business data.
"""
from typing import Dict, Optional, Any
from .base import BaseProcessor, ProcessingResult
from .validators import RatingValidator, TextValidator
from .cleaners import TextCleaner, PhoneCleaner, URLCleaner
from .transformers import RatingTransformer, NumberTransformer, CategoryNormalizer, AddressNormalizer


class BusinessDataProcessor(BaseProcessor):
    """Processes business data with specialized cleaners and validators."""
    
    def __init__(self):
        super().__init__("BusinessDataProcessor")
        
        # Initialize processors for different fields
        self.text_cleaner = TextCleaner()
        self.phone_cleaner = PhoneCleaner()
        self.url_cleaner = URLCleaner()
        self.rating_transformer = RatingTransformer()
        self.number_transformer = NumberTransformer()
        self.category_normalizer = CategoryNormalizer()
        self.address_normalizer = AddressNormalizer()
        
        # Validators
        self.rating_validator = RatingValidator()
        self.text_validator = TextValidator(min_length=1)
    
    def process(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single business data record."""
        if not data or not data.get('name'):
            return None
        
        try:
            cleaned = {}
            
            # Process name (required field)
            name = self.text_cleaner.clean(data.get('name'))
            if not name:
                return None
            cleaned['name'] = name
            
            # Process rating
            rating = self._process_rating(data.get('rating'))
            cleaned['rating'] = rating
            
            # Process reviews count
            reviews = self._process_reviews(data.get('reviews'))
            cleaned['reviews'] = reviews
            
            # Process category
            category = self._process_category(data.get('category'))
            cleaned['category'] = category
            
            # Process address
            address = self._process_address(data.get('address'))
            cleaned['address'] = address
            
            # Process phone
            phone = self._process_phone(data.get('phone'))
            cleaned['phone'] = phone
            
            # Process website
            website = self._process_website(data.get('website'))
            cleaned['website'] = website
            
            # Copy other fields as-is
            for field in ['price_level', 'hours', 'introduction', 'in_store_pickup', 
                         'store_delivery', 'store_shopping']:
                if field in data:
                    cleaned[field] = data[field]
            
            return cleaned
            
        except Exception as e:
            self.logger.warning(f"Error processing business data: {e}")
            return None
    
    def _process_rating(self, rating_value: Any) -> Optional[float]:
        """Process rating field."""
        if not rating_value:
            return None
        
        # Transform and validate rating
        rating = self.rating_transformer.transform(rating_value)
        if rating is not None and self.rating_validator.is_valid(rating):
            return rating
        return None
    
    def _process_reviews(self, reviews_value: Any) -> Optional[int]:
        """Process reviews count field."""
        if not reviews_value:
            return None
        
        return self.number_transformer.transform(reviews_value)
    
    def _process_category(self, category_value: Any) -> Optional[str]:
        """Process category field."""
        if not category_value:
            return None
        
        # Clean and normalize category
        cleaned = self.text_cleaner.clean(category_value)
        if cleaned:
            return self.category_normalizer.transform(cleaned)
        return None
    
    def _process_address(self, address_value: Any) -> Optional[str]:
        """Process address field."""
        if not address_value:
            return None
        
        # Clean and normalize address
        cleaned = self.text_cleaner.clean(address_value)
        if cleaned:
            return self.address_normalizer.transform(cleaned)
        return None
    
    def _process_phone(self, phone_value: Any) -> Optional[str]:
        """Process phone field."""
        if not phone_value:
            return None
        
        return self.phone_cleaner.clean(phone_value)
    
    def _process_website(self, website_value: Any) -> Optional[str]:
        """Process website field."""
        if not website_value:
            return None
        
        return self.url_cleaner.clean(website_value)
    
    def validate_business_data(self, data: Dict[str, Any]) -> ProcessingResult:
        """Validate business data and return detailed result."""
        result = ProcessingResult(data)
        
        # Check required fields
        if not data.get('name'):
            result.add_error("Business name is required")
        
        # Validate rating if present
        if 'rating' in data and data['rating'] is not None:
            if not self.rating_validator.is_valid(data['rating']):
                result.add_error(f"Invalid rating: {data['rating']}")
        
        # Validate text fields
        text_fields = ['name', 'category', 'address']
        for field in text_fields:
            if field in data and data[field] is not None:
                if not self.text_validator.is_valid(data[field]):
                    result.add_error(f"Invalid {field}: {data[field]}")
        
        return result
