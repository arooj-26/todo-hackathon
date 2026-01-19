"""
Audit Service - Consumes events and maintains audit logs.

This service subscribes to all events and creates immutable audit records
for compliance and debugging.
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .database import DatabaseManager, get_db
from .handlers.event_handler import EventHandler

# Configure structured logging
logger = structlog.get_logger()

# Global database manager
db_manager: DatabaseManager | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global db_manager

    logger.info("audit_service_starting")

    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.create_tables()

    logger.info("audit_service_database_initialized")

    yield

    # Cleanup
    if db_manager:
        await db_manager.close()

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
    try:
        # Check database connection
        async for session in get_db():
            # Simple query to check connection
            await session.execute("SELECT 1")
            return {
                "status": "ready",
                "service": "audit",
                "checks": {
                    "database": "ok",
                    "dapr": "ok"
                }
            }
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return {
            "status": "not_ready",
            "service": "audit",
            "checks": {
                "database": "error",
                "error": str(e)
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


@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription endpoint.

    Returns the list of topics this service subscribes to.
    Dapr calls this endpoint to discover subscriptions.
    """
    pubsub_name = os.getenv("PUBSUB_NAME", "kafka-pubsub")

    subscriptions = [
        {
            "pubsubname": pubsub_name,
            "topic": "task-events",
            "route": "/events/task-events",
            "metadata": {
                "rawPayload": "false",  # Dapr CloudEvents wrapper enabled
            },
        },
        {
            "pubsubname": pubsub_name,
            "topic": "reminders",
            "route": "/events/reminders",
            "metadata": {
                "rawPayload": "false",
            },
        },
        {
            "pubsubname": pubsub_name,
            "topic": "task-updates",
            "route": "/events/task-updates",
            "metadata": {
                "rawPayload": "false",
            },
        },
    ]

    logger.info("subscription_configuration", subscriptions=subscriptions)
    return subscriptions


@app.post("/events/task-events")
async def handle_task_events(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """Handle task events from Dapr Pub/Sub.

    Receives task lifecycle events (created, updated, completed, deleted)
    and creates audit log entries.
    """
    try:
        event_data = await request.json()
        logger.info("received_task_event", event=event_data)

        # Create audit log
        handler = EventHandler(session)
        audit_log = await handler.handle_event(event_data)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "audit_log_id": audit_log.id,
            },
        )
    except Exception as e:
        logger.error("task_event_processing_error", error=str(e), exc_info=True)
        # Return 200 to acknowledge receipt (avoid Dapr retries for application errors)
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)},
        )


@app.post("/events/reminders")
async def handle_reminders(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """Handle reminder events from Dapr Pub/Sub.

    Receives reminder events (sent, failed) and creates audit log entries.
    """
    try:
        event_data = await request.json()
        logger.info("received_reminder_event", event=event_data)

        # Create audit log
        handler = EventHandler(session)
        audit_log = await handler.handle_event(event_data)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "audit_log_id": audit_log.id,
            },
        )
    except Exception as e:
        logger.error("reminder_event_processing_error", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)},
        )


@app.post("/events/task-updates")
async def handle_task_updates(
    request: Request,
    session: AsyncSession = Depends(get_db)
):
    """Handle task update events from Dapr Pub/Sub.

    Receives real-time task update events and creates audit log entries.
    """
    try:
        event_data = await request.json()
        logger.info("received_task_update_event", event=event_data)

        # Create audit log
        handler = EventHandler(session)
        audit_log = await handler.handle_event(event_data)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "audit_log_id": audit_log.id,
            },
        )
    except Exception as e:
        logger.error("task_update_event_processing_error", error=str(e), exc_info=True)
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)},
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
