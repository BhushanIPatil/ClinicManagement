"""
Performance and Security Middleware

Middleware for rate limiting, request logging, and security headers.
"""

from time import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for performance monitoring.
    
    Logs request duration and adds performance headers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time()
        
        response = await call_next(request)
        
        process_time = time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests (>1 second)
        if process_time > 1.0:
            print(f"Slow request: {request.url.path} took {process_time:.2f}s")
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for security headers.
    
    Adds security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Only add HSTS in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    
    In production, use Redis-based rate limiting.
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_minute = int(time() / 60)
        key = f"{client_ip}:{current_minute}"
        
        # Simple in-memory rate limiting (use Redis in production)
        count = self.request_counts.get(key, 0)
        if count >= self.requests_per_minute:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"},
            )
        
        self.request_counts[key] = count + 1
        
        # Clean old entries (simple cleanup)
        if len(self.request_counts) > 10000:
            self.request_counts.clear()
        
        return await call_next(request)
