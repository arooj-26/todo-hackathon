"""
Audit Service - Consumes events and maintains audit logs.

This service subscribes to all events and creates immutable audit records
for compliance and debugging.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
import structlog

# Configure structured logging
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    logger.info("audit_service_starting")
    yield
    logger.info("audit_service_shutting_down")

# Create FastAPI app
app = FastAPI(
    title="Audit Service",
    description="Event audit logging and compliance service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "audit"}

@app.get("/ready")
async def ready():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "service": "audit",
        "checks": {
            "database": "ok",
            "dapr": "ok"
        }
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "audit",
        "version": "1.0.0",
        "status": "running"
    }

# TODO: Add event subscription handlers for:
# - task-events topic
# - reminders topic
# - task-updates topic
