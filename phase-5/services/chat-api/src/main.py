"""Chat API main application."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.auth import router as auth_router
from .api.health import router as health_router
from .api.tags import router as tags_router
from .api.tasks import router as tasks_router
from .dapr.pubsub import dapr_pubsub, DaprPubSubClient
from .database import db_manager, DatabaseManager
from .logging_config import configure_logging, get_logger
from .middleware.error_handler import add_error_handler_middleware
from .middleware.metrics import PrometheusMiddleware, get_metrics_response

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
configure_logging(log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Chat API starting up...")

    # Initialize database manager
    global db_manager
    db_manager = DatabaseManager()

    # Initialize Dapr Pub/Sub client
    global dapr_pubsub
    dapr_pubsub = DaprPubSubClient()

    logger.info("Chat API started successfully")

    yield

    # Cleanup
    logger.info("Chat API shutting down...")
    if db_manager:
        await db_manager.close()
    logger.info("Chat API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Todo Chat API",
    description="REST API for todo management with recurring tasks and event-driven architecture",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
# Configure CORS origins from environment variable
# In production, set CORS_ORIGINS to comma-separated whitelist
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

if "*" in cors_origins:
    logger.warning("CORS is configured to allow all origins (*). Set CORS_ORIGINS env var in production!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
)

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# Add error handler middleware
add_error_handler_middleware(app)

# Include routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(tags_router)
app.include_router(tasks_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Todo Chat API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint.

    Exposes metrics for:
    - HTTP request rate, latency (p50, p95, p99), error rate
    - Tasks created/completed/deleted counts
    - Events published/failed counts
    - Database query duration
    - Active users gauge

    Returns:
        Prometheus-formatted metrics
    """
    return get_metrics_response()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
