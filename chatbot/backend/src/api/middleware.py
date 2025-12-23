"""
API middleware for logging, rate limiting, and request tracking.
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and responses.
    """

    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process request
        try:
            response = await call_next(request)

            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Duration: {process_time:.3f}s"
            )

            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            logger.error(f"Request failed: {request.method} {request.url.path} Error: {str(e)}")
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.

    Limits requests per user to prevent abuse.
    For production, use Redis-based rate limiting.
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Extract user ID from path if available
        path_parts = request.url.path.split('/')
        user_id = None

        if len(path_parts) >= 3 and path_parts[1] == 'api':
            try:
                user_id = path_parts[2]
            except (IndexError, ValueError):
                pass

        if user_id:
            # Clean old timestamps
            now = datetime.now()
            cutoff = now - timedelta(minutes=1)
            self.request_counts[user_id] = [
                ts for ts in self.request_counts[user_id]
                if ts > cutoff
            ]

            # Check rate limit
            if len(self.request_counts[user_id]) >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for user: {user_id}")
                return Response(
                    content='{"error": "Rate limit exceeded. Please try again later."}',
                    status_code=429,
                    media_type="application/json"
                )

            # Record request
            self.request_counts[user_id].append(now)

        return await call_next(request)
