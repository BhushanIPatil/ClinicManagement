"""
Caching utilities for performance optimization.

Simple in-memory cache. In production, use Redis.
"""

from typing import Any, Optional
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json


class SimpleCache:
    """Simple in-memory cache for development."""
    
    def __init__(self):
        self._cache: dict[str, tuple[Any, datetime]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        if datetime.utcnow() > expiry:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        """Set value in cache with TTL."""
        expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()


# Global cache instance
cache = SimpleCache()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items()),
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl_seconds: int = 60):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(ttl_seconds=300)
        async def expensive_operation():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator
