"""Prometheus metrics middleware for FastAPI."""

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method', 'endpoint']
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status_code']
)

# Application-specific metrics
tasks_created_total = Counter(
    'tasks_created_total',
    'Total tasks created'
)

tasks_completed_total = Counter(
    'tasks_completed_total',
    'Total tasks completed'
)

tasks_deleted_total = Counter(
    'tasks_deleted_total',
    'Total tasks deleted'
)

events_published_total = Counter(
    'events_published_total',
    'Total events published to Kafka',
    ['topic', 'event_type']
)

events_publish_failures_total = Counter(
    'events_publish_failures_total',
    'Total event publish failures',
    ['topic', 'error_type']
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

active_users_gauge = Gauge(
    'active_users',
    'Number of active users (with activity in last hour)'
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics for HTTP requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics.

        Args:
            request: FastAPI request
            call_next: Next middleware or route handler

        Returns:
            Response from handler
        """
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = request.url.path

        # Track request size
        request_size = int(request.headers.get("content-length", 0))
        http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(request_size)

        # Track in-progress requests
        http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()

        # Track request duration
        start_time = time.time()

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record metrics
            status_code = response.status_code
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Track response size
            response_size = int(response.headers.get("content-length", 0))
            http_response_size_bytes.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(response_size)

            return response

        except Exception as e:
            # Track errors
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            raise

        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()


def get_metrics_response() -> StarletteResponse:
    """Generate Prometheus metrics response.

    Returns:
        Response with metrics in Prometheus format
    """
    metrics = generate_latest()
    return StarletteResponse(
        content=metrics,
        media_type=CONTENT_TYPE_LATEST
    )
