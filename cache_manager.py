"""
Cache Manager for Stock Bot
Caches API responses to reduce latency and API calls
"""
import time
from typing import Any, Optional
import json

class CacheManager:
    def __init__(self, default_ttl=300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp, ttl = self.cache[key]
            if time.time() - timestamp < ttl:
                return value
            else:
                # Expired, remove it
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Cache a value with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        self.cache[key] = (value, time.time(), ttl)
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
    
    def clear_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp, ttl) in self.cache.items()
            if current_time - timestamp >= ttl
        ]
        for key in expired_keys:
            del self.cache[key]

# Global cache instance
cache = CacheManager()
