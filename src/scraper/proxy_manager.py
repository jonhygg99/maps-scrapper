"""
Proxy Manager for Rotating Proxies
Handles proxy validation and rotation
"""
import random
from typing import List, Optional
import httpx
from src.utils.logger import Logger
from src.core.config import Config


class ProxyManager:
    """Manages proxy rotation and validation"""
    
    def __init__(self, proxies: Optional[List[str]] = None):
        """
        Initialize proxy manager
        
        Args:
            proxies: List of proxy URLs (format: http://host:port or http://user:pass@host:port)
        """
        self.proxies = proxies or Config.get_proxies()
        self.active_proxies = []
        self.failed_proxies = []
        self.current_index = 0
        self.logger = Logger.get_logger("ProxyManager")
        
        if self.proxies:
            self.logger.info(f"Loaded {len(self.proxies)} proxies")
        else:
            self.logger.warning("No proxies loaded")
    
    async def validate_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """
        Validate a proxy by testing it
        
        Args:
            proxy: Proxy URL to validate
            timeout: Request timeout in seconds
            
        Returns:
            True if proxy is valid, False otherwise
        """
        try:
            async with httpx.AsyncClient(proxy=proxy, timeout=timeout) as client:
                response = await client.get('https://www.google.com')
                
                if response.status_code == 200:
                    self.logger.info(f"Proxy validated: {self._mask_proxy(proxy)}")
                    return True
                else:
                    self.logger.warning(f"Proxy returned status {response.status_code}: {self._mask_proxy(proxy)}")
                    return False
                    
        except Exception as e:
            self.logger.warning(f"Proxy validation failed: {self._mask_proxy(proxy)} - {str(e)}")
            return False
    
    async def validate_all_proxies(self):
        """Validate all proxies and separate active from failed"""
        if not self.proxies:
            self.logger.warning("No proxies to validate")
            return
        
        self.logger.info(f"Validating {len(self.proxies)} proxies...")
        
        for proxy in self.proxies:
            if await self.validate_proxy(proxy):
                self.active_proxies.append(proxy)
            else:
                self.failed_proxies.append(proxy)
        
        self.logger.info(
            f"Validation complete: {len(self.active_proxies)} active, "
            f"{len(self.failed_proxies)} failed"
        )
    
    def get_random_proxy(self) -> Optional[str]:
        """
        Get a random proxy from active proxies
        
        Returns:
            Random proxy URL or None if no active proxies
        """
        if not self.active_proxies:
            if self.proxies:
                # Use unvalidated proxies if no validated ones available
                return random.choice(self.proxies)
            return None
        
        proxy = random.choice(self.active_proxies)
        self.logger.debug(f"Using proxy: {self._mask_proxy(proxy)}")
        return proxy
    
    def get_next_proxy(self) -> Optional[str]:
        """
        Get next proxy in round-robin fashion
        
        Returns:
            Next proxy URL or None if no proxies available
        """
        proxies_to_use = self.active_proxies if self.active_proxies else self.proxies
        
        if not proxies_to_use:
            return None
        
        proxy = proxies_to_use[self.current_index]
        self.current_index = (self.current_index + 1) % len(proxies_to_use)
        
        self.logger.debug(f"Using proxy: {self._mask_proxy(proxy)}")
        return proxy
    
    def mark_proxy_failed(self, proxy: str):
        """
        Mark a proxy as failed and remove from active list
        
        Args:
            proxy: Proxy URL that failed
        """
        if proxy in self.active_proxies:
            self.active_proxies.remove(proxy)
            self.failed_proxies.append(proxy)
            self.logger.warning(f"Proxy marked as failed: {self._mask_proxy(proxy)}")
    
    def get_proxy_stats(self) -> dict:
        """
        Get statistics about proxies
        
        Returns:
            Dictionary with proxy statistics
        """
        return {
            'total': len(self.proxies),
            'active': len(self.active_proxies),
            'failed': len(self.failed_proxies),
            'unvalidated': len(self.proxies) - len(self.active_proxies) - len(self.failed_proxies)
        }
    
    def _mask_proxy(self, proxy: str) -> str:
        """
        Mask sensitive information in proxy URL for logging
        
        Args:
            proxy: Proxy URL
            
        Returns:
            Masked proxy URL
        """
        try:
            # Mask password if present
            if '@' in proxy:
                protocol, rest = proxy.split('://')
                credentials, host = rest.split('@')
                if ':' in credentials:
                    user, _ = credentials.split(':')
                    return f"{protocol}://{user}:****@{host}"
            return proxy
        except:
            return proxy
    
    def has_proxies(self) -> bool:
        """Check if any proxies are available"""
        return len(self.proxies) > 0 or len(self.active_proxies) > 0
    
    def reset(self):
        """Reset proxy manager state"""
        self.active_proxies = []
        self.failed_proxies = []
        self.current_index = 0
        self.logger.info("Proxy manager reset")
