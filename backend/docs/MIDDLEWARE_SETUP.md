# Middleware Setup Instructions

## Manual Setup Required

Due to file encoding issues, please manually add the following to `backend/app/main.py`:

### 1. Add Imports (after line 21)

```python
from app.core.middleware import (
    PerformanceMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)
```

### 2. Add Middleware Registration (after line 76, after CORS middleware)

```python
# Add performance and security middleware
app.add_middleware(PerformanceMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting (only in production or if enabled)
if settings.ENVIRONMENT == "production":
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

## What These Middleware Do

### PerformanceMiddleware
- Logs request duration
- Adds `X-Process-Time` header
- Logs slow requests (>1 second)

### SecurityHeadersMiddleware
- Adds security headers to all responses:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection: 1; mode=block`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Strict-Transport-Security` (production only)

### RateLimitMiddleware
- Limits requests per IP
- Default: 60 requests per minute
- Returns 429 when exceeded
- Only enabled in production
