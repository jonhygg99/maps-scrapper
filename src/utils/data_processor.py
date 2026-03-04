"""
Data Processor for Cleaning and Validating Scraped Data
"""
import re
from typing import List, Dict, Optional
from src.utils.logger import Logger


class DataProcessor:
    """Process and clean scraped data"""
    
    def __init__(self):
        self.logger = Logger.get_logger("DataProcessor")
    
    def clean_results(self, results: List[Dict]) -> List[Dict]:
        """
        Clean and validate scraped results
        
        Args:
            results: List of raw scraped data
            
        Returns:
            List of cleaned data
        """
        cleaned = []
        
        for i, result in enumerate(results):
            try:
                cleaned_result = self._clean_business_data(result)
                if cleaned_result:
                    cleaned.append(cleaned_result)
            except Exception as e:
                self.logger.warning(f"Error cleaning result {i}: {e}")
                continue
        
        self.logger.info(f"Cleaned {len(cleaned)} out of {len(results)} results")
        return cleaned
    
    def _clean_business_data(self, data: Dict) -> Optional[Dict]:
        """Clean individual business data"""
        if not data or not data.get('name'):
            return None
        
        cleaned = {}
        
        # Name
        cleaned['name'] = self._clean_text(data.get('name'))
        
        # Rating
        rating = data.get('rating')
        if rating:
            cleaned['rating'] = self._extract_rating(rating)
        else:
            cleaned['rating'] = None
        
        # Reviews
        reviews = data.get('reviews')
        if reviews:
            cleaned['reviews'] = self._extract_number(reviews)
        else:
            cleaned['reviews'] = None
        
        # Category
        cleaned['category'] = self._clean_text(data.get('category'))
        
        # Address
        cleaned['address'] = self._clean_text(data.get('address'))
        
        # Price level
        cleaned['price_level'] = data.get('price_level')
        
        # Phone
        cleaned['phone'] = self._clean_phone(data.get('phone'))
        
        # Website
        cleaned['website'] = self._clean_url(data.get('website'))
        
        return cleaned
    
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Clean text field"""
        if not text:
            return None
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,&()\'"]', '', text)
        
        return text.strip() if text.strip() else None
    
    def _extract_rating(self, rating_str: str) -> Optional[float]:
        """Extract numeric rating from string"""
        try:
            # Extract first number (e.g., "4.5" from "4.5 stars")
            match = re.search(r'(\d+\.?\d*)', rating_str)
            if match:
                rating = float(match.group(1))
                # Validate rating range
                if 0 <= rating <= 5:
                    return rating
        except:
            pass
        return None
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract integer number from string"""
        try:
            # Remove commas and extract number
            number_str = re.sub(r'[^\d]', '', text)
            if number_str:
                return int(number_str)
        except:
            pass
        return None
    
    def _clean_phone(self, phone: Optional[str]) -> Optional[str]:
        """Clean phone number"""
        if not phone:
            return None
        
        # Extract phone number pattern
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
        phone = ' '.join(phone.split())
        
        return phone if phone else None
    
    def _clean_url(self, url: Optional[str]) -> Optional[str]:
        """Clean and validate URL"""
        if not url:
            return None
        
        url = url.strip()
        
        # Basic URL validation
        if not (url.startswith('http://') or url.startswith('https://')):
            return None
        
        return url
    
    def remove_duplicates(self, results: List[Dict], key: str = 'name') -> List[Dict]:
        """
        Remove duplicate entries based on a key
        
        Args:
            results: List of data dictionaries
            key: Key to use for duplicate detection
            
        Returns:
            List with duplicates removed
        """
        seen = set()
        unique = []
        
        for result in results:
            identifier = result.get(key)
            if identifier and identifier not in seen:
                seen.add(identifier)
                unique.append(result)
        
        if len(unique) < len(results):
            self.logger.info(f"Removed {len(results) - len(unique)} duplicates")
        
        return unique
    
    def filter_by_rating(self, results: List[Dict], min_rating: float = 0.0) -> List[Dict]:
        """
        Filter results by minimum rating
        
        Args:
            results: List of data dictionaries
            min_rating: Minimum rating threshold
            
        Returns:
            Filtered list
        """
        filtered = [
            r for r in results
            if r.get('rating') is not None and r.get('rating') >= min_rating
        ]
        
        if len(filtered) < len(results):
            self.logger.info(f"Filtered to {len(filtered)} results with rating >= {min_rating}")
        
        return filtered
    
    def sort_by_rating(self, results: List[Dict], descending: bool = True) -> List[Dict]:
        """
        Sort results by rating
        
        Args:
            results: List of data dictionaries
            descending: Sort in descending order
            
        Returns:
            Sorted list
        """
        def get_rating(item):
            rating = item.get('rating')
            return rating if rating is not None else -1
        
        return sorted(results, key=get_rating, reverse=descending)
