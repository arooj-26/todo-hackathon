"""
Rate limiting middleware for FastAPI
Implements token bucket algorithm to prevent API abuse
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger(__name__)


class TokenBucket:
    """Token bucket for rate limiting"""

    def __init__(self, capacity: int, refill_rate: float):
        """
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False otherwise
        """
        # Refill tokens based on time passed
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.refill_rate)
        )
        self.last_refill = now

        # Try to consume
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True

        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm
    Limits requests per IP address
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst: int = 10
    ):
        """
        Args:
            app: FastAPI application
            requests_per_minute: Sustained request rate
            burst: Burst capacity
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst = burst
        self.buckets: Dict[str, TokenBucket] = {}

    def get_client_id(self, request: Request) -> str:
        """Extract client identifier from request"""
        # Use X-Forwarded-For if behind proxy, otherwise client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def get_bucket(self, client_id: str) -> TokenBucket:
        """Get or create token bucket for client"""
        if client_id not in self.buckets:
            refill_rate = self.requests_per_minute / 60.0  # tokens per second
            self.buckets[client_id] = TokenBucket(
                capacity=self.burst,
                refill_rate=refill_rate
            )
        return self.buckets[client_id]

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready", "/metrics"]:
            return await call_next(request)

        # Get client identifier
        client_id = self.get_client_id(request)

        # Get token bucket
        bucket = self.get_bucket(client_id)

        # Try to consume token
        if not bucket.consume():
            logger.warning(
                "rate_limit_exceeded",
                client_id=client_id,
                path=request.url.path,
                method=request.method
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))

        return response
