"""
Security headers middleware for FastAPI
Adds security headers to all responses
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses
    Implements OWASP security best practices
    """

    def __init__(self, app, cors_origins: str = "*"):
        """
        Args:
            app: FastAPI application
            cors_origins: Allowed CORS origins
        """
        super().__init__(app)
        self.cors_origins = cors_origins

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # CORS headers
        response.headers["Access-Control-Allow-Origin"] = self.cors_origins
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Correlation-ID"
        response.headers["Access-Control-Expose-Headers"] = "X-Correlation-ID, X-RateLimit-Limit, X-RateLimit-Remaining"
        response.headers["Access-Control-Max-Age"] = "3600"

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]

        return response
