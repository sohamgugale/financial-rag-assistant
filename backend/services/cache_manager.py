"""
Cache Manager
Simple in-memory caching for query responses
"""

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from loguru import logger


class CacheManager:
    """
    Simple in-memory cache for RAG responses
    In production, use Redis for distributed caching
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached value
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if datetime.now() < entry['expires_at']:
                logger.debug(f"Cache hit for key: {key[:50]}...")
                return entry['value']
            else:
                # Remove expired entry
                del self.cache[key]
                logger.debug(f"Cache expired for key: {key[:50]}...")
        
        return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        
        logger.debug(f"Cached value for key: {key[:50]}... (TTL: {ttl}s)")
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Deleted cache entry: {key[:50]}...")
            return True
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of cached entries"""
        # Remove expired entries
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if now >= entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'active_entries': self.get_cache_size()
        }
