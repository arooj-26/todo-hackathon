"""Chat API main application."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.health import router as health_router
from .api.tags import router as tags_router
from .api.tasks import router as tasks_router
from .dapr.pubsub import dapr_pubsub, DaprPubSubClient
from .database import db_manager, DatabaseManager
from .logging_config import configure_logging, get_logger
from .middleware.error_handler import add_error_handler_middleware

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handler middleware
add_error_handler_middleware(app)

# Include routers
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


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
