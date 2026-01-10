"""Recurring Task Service main application with Dapr subscription."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .consumers.task_completed_handler import TaskCompletedHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Recurring Task Service starting up...")
    yield
    logger.info("Recurring Task Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Recurring Task Service",
    description="Processes task completion events and generates next recurring instances",
    version="1.0.0",
    lifespan=lifespan,
)

# Initialize task completed handler
task_handler = TaskCompletedHandler()


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe."""
    return {"status": "healthy", "service": "recurring-tasks"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe."""
    return {"status": "ready", "service": "recurring-tasks"}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns the list of topics this service subscribes to.
    Dapr calls this endpoint to discover subscriptions.
    """
    pubsub_name = os.getenv("PUBSUB_NAME", "kafka-pubsub")

    subscriptions = [
        {
            "pubsubname": pubsub_name,
            "topic": "task-events",
            "route": "/events/task-completed",
            "metadata": {
                "rawPayload": "false",  # Dapr CloudEvents wrapper enabled
            },
        }
    ]

    logger.info(f"Subscription configuration: {subscriptions}")
    return subscriptions


@app.post("/events/task-completed")
async def handle_task_completed(request: Request):
    """
    Handle task completion events from Dapr Pub/Sub.

    This endpoint receives CloudEvents wrapped messages from Dapr.
    Filters for completed tasks with recurrence patterns and generates next instances.
    """
    try:
        event_data = await request.json()
        logger.info(f"Received task event: {event_data}")

        # Extract data from CloudEvents wrapper
        # Dapr wraps the message in CloudEvents format
        if "data" in event_data:
            task_event = event_data["data"]
        else:
            task_event = event_data

        # Process the task completed event
        await task_handler.handle(task_event)

        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "Event processed"},
        )

    except Exception as e:
        logger.error(f"Error processing task completed event: {e}", exc_info=True)
        # Return 200 to acknowledge receipt (avoid Dapr retries for application errors)
        # Application errors should be handled via dead letter queue or manual review
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": str(e)},
        )


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
