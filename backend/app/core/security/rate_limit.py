"""
Rate Limiting Utilities

Rate limiting for API endpoints to prevent abuse.
"""

from functools import wraps
from typing import Callable
from time import time
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

# Simple in-memory rate limiter (use Redis in production)
_rate_limit_store: dict[str, list[float]] = {}


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Rate limiting decorator.
    
    Args:
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Usage:
        @rate_limit(max_requests=10, window_seconds=60)
        async def my_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"
            current_time = time()
            
            # Get request history for this IP
            if client_ip not in _rate_limit_store:
                _rate_limit_store[client_ip] = []
            
            request_times = _rate_limit_store[client_ip]
            
            # Remove old requests outside window
            request_times[:] = [
                t for t in request_times
                if current_time - t < window_seconds
            ]
            
            # Check rate limit
            if len(request_times) >= max_requests:
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {max_requests} requests per {window_seconds} seconds",
                    headers={"Retry-After": str(window_seconds)},
                )
            
            # Record this request
            request_times.append(current_time)
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator
