"""Reminder trigger handler for Dapr Jobs API callbacks."""

from datetime import datetime
from typing import Any
from uuid import UUID

from ..dapr.pubsub import get_pubsub_client
from ..logging_config import get_logger, set_correlation_id
from ..services.notification_dispatcher import NotificationDispatcher, NotificationRequest

logger = get_logger(__name__)


async def handle_reminder_trigger(payload: Any) -> dict:
    """Handle reminder trigger from Dapr Jobs API.

    This function is called when a scheduled reminder job is triggered by Dapr.
    It dispatches the notification through configured channels and publishes
    a ReminderEvent to the reminders topic.

    Args:
        payload: Job payload containing reminder and task details

    Returns:
        dict: Result of reminder processing with notifications_sent count

    Raises:
        Exception: If reminder processing fails
    """
    # Set correlation ID for distributed tracing
    correlation_id = payload.correlation_id or set_correlation_id()
    set_correlation_id(correlation_id)

    logger.info(
        "Processing reminder trigger",
        reminder_id=payload.reminder_id,
        task_id=payload.task_id,
        user_id=payload.user_id,
        notification_channel=payload.notification_channel,
    )

    try:
        # Create notification request
        notification_request = NotificationRequest(
            user_id=UUID(payload.user_id),
            task_id=payload.task_id,
            task_title=payload.task_title,
            task_description=payload.task_description,
            priority=payload.priority,
            due_at=datetime.fromisoformat(payload.due_at.replace("Z", "+00:00"))
            if payload.due_at
            else None,
            channel=payload.notification_channel,
        )

        # Dispatch notification
        dispatcher = NotificationDispatcher()
        success = await dispatcher.send_notification(notification_request)

        if success:
            logger.info(
                "Notification dispatched successfully",
                reminder_id=payload.reminder_id,
                task_id=payload.task_id,
                channel=payload.notification_channel,
            )

            # Publish ReminderEvent to reminders topic
            await _publish_reminder_event(
                event_type="reminder_sent",
                payload=payload,
                correlation_id=correlation_id,
            )

            return {
                "status": "success",
                "notifications_sent": 1,
                "channel": payload.notification_channel,
            }
        else:
            logger.warning(
                "Notification dispatch failed",
                reminder_id=payload.reminder_id,
                task_id=payload.task_id,
                channel=payload.notification_channel,
            )

            # Publish failed event
            await _publish_reminder_event(
                event_type="reminder_failed",
                payload=payload,
                correlation_id=correlation_id,
                error_message="Notification dispatch failed",
            )

            return {
                "status": "failed",
                "notifications_sent": 0,
                "error": "Notification dispatch failed",
            }

    except Exception as e:
        logger.error(
            "Reminder trigger processing failed",
            reminder_id=payload.reminder_id,
            task_id=payload.task_id,
            error=str(e),
            exc_info=True,
        )

        # Publish failed event
        await _publish_reminder_event(
            event_type="reminder_failed",
            payload=payload,
            correlation_id=correlation_id,
            error_message=str(e),
        )

        raise


async def _publish_reminder_event(
    event_type: str,
    payload: Any,
    correlation_id: str,
    error_message: str | None = None,
) -> None:
    """Publish ReminderEvent to Kafka reminders topic.

    Args:
        event_type: Type of reminder event (reminder_sent, reminder_failed)
        payload: Original job payload
        correlation_id: Correlation ID for tracing
        error_message: Optional error message for failed events
    """
    try:
        pubsub = get_pubsub_client()

        event = {
            "schema_version": "1.0",
            "event_type": event_type,
            "reminder_id": payload.reminder_id,
            "task_id": payload.task_id,
            "user_id": payload.user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": correlation_id,
            "due_at": payload.due_at,
            "remind_at": datetime.utcnow().isoformat() + "Z",
            "task_title": payload.task_title,
            "task_description": payload.task_description,
            "priority": payload.priority,
            "notification_channel": payload.notification_channel,
            "retry_count": 0,
            "error_message": error_message,
        }

        await pubsub.publish(
            topic="reminders",
            event=event,
            correlation_id=correlation_id,
        )

        logger.info(
            "ReminderEvent published",
            event_type=event_type,
            reminder_id=payload.reminder_id,
            task_id=payload.task_id,
            topic="reminders",
        )

    except Exception as e:
        logger.error(
            "Failed to publish ReminderEvent",
            event_type=event_type,
            reminder_id=payload.reminder_id,
            task_id=payload.task_id,
            error=str(e),
        )
        # Don't fail the reminder trigger if event publishing fails
