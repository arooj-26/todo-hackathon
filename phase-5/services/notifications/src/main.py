"""Notification Service - Handles reminder triggers and notification delivery."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

from .jobs.reminder_trigger import handle_reminder_trigger
from .logging_config import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Notification Service starting up")
    yield
    logger.info("Notification Service shutting down")


app = FastAPI(
    title="Notification Service",
    description="Handles reminder triggers from Dapr Jobs API and sends notifications",
    version="1.0.0",
    lifespan=lifespan,
)


class ReminderJobPayload(BaseModel):
    """Payload structure from Dapr Jobs API callback."""

    reminder_id: int
    task_id: int
    user_id: str
    task_title: str
    task_description: str | None = None
    priority: str
    due_at: str | None
    notification_channel: str
    correlation_id: str | None = None


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: Service health status
    """
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "1.0.0",
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint.

    Returns:
        dict: Service readiness status
    """
    return {
        "status": "ready",
        "service": "notification-service",
    }


@app.post("/jobs/reminder-trigger")
async def reminder_trigger_callback(request: Request):
    """Dapr Jobs API callback endpoint for reminder triggers.

    This endpoint is invoked by Dapr Jobs API when a scheduled reminder job is due.
    It processes the reminder and dispatches notifications through configured channels.

    Args:
        request: FastAPI request containing job payload

    Returns:
        dict: Status of reminder processing

    Raises:
        HTTPException: If reminder processing fails
    """
    try:
        # Parse job payload
        payload = await request.json()
        logger.info(
            "Received reminder trigger callback",
            reminder_id=payload.get("reminder_id"),
            task_id=payload.get("task_id"),
            user_id=payload.get("user_id"),
        )

        # Validate payload
        job_payload = ReminderJobPayload(**payload)

        # Process the reminder trigger
        result = await handle_reminder_trigger(job_payload)

        logger.info(
            "Reminder trigger processed successfully",
            reminder_id=job_payload.reminder_id,
            task_id=job_payload.task_id,
            result=result,
        )

        return {
            "status": "success",
            "reminder_id": job_payload.reminder_id,
            "task_id": job_payload.task_id,
            "notifications_sent": result.get("notifications_sent", 0),
        }

    except Exception as e:
        logger.error(
            "Reminder trigger callback failed",
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process reminder trigger: {str(e)}",
        )


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        dict: Service information
    """
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "description": "Handles reminder triggers and notification delivery",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
