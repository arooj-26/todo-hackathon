"""Reminder service with Dapr Jobs API integration for scheduling task reminders."""

import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..logging_config import get_logger
from ..models.reminder import Reminder, ReminderCreate, DeliveryStatus, NotificationChannel
from ..models.task import Task

logger = get_logger(__name__)


class ReminderService:
    """Service for scheduling and managing task reminders using Dapr Jobs API.

    The Dapr Jobs API provides a reliable, distributed scheduler for triggering
    reminders at specified times. Jobs are scheduled with a callback URL that
    points to the Notification Service.
    """

    def __init__(self, session: AsyncSession):
        """Initialize reminder service.

        Args:
            session: Database session
        """
        self.session = session
        self.dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        self.dapr_base_url = f"http://localhost:{self.dapr_http_port}"
        # Callback URL points to Notification Service endpoint
        self.notification_service_url = os.getenv(
            "NOTIFICATION_SERVICE_URL",
            "http://notifications:8000"
        )

    async def schedule_reminder(
        self,
        task_id: int,
        user_id: UUID,
        remind_at: datetime,
        notification_channel: NotificationChannel = NotificationChannel.IN_APP,
        correlation_id: Optional[str] = None,
    ) -> Reminder:
        """Schedule a reminder for a task using Dapr Jobs API.

        Creates a Dapr Job that will trigger at the specified time and invoke
        the Notification Service callback endpoint.

        Args:
            task_id: Task ID to remind about
            user_id: User ID to send reminder to
            remind_at: When to send the reminder (UTC)
            notification_channel: Channel to deliver notification
            correlation_id: Optional correlation ID for tracing

        Returns:
            Created reminder instance

        Raises:
            ValueError: If task not found or remind_at is in the past
            httpx.HTTPStatusError: If Dapr Jobs API fails
        """
        logger.info(
            "Scheduling reminder",
            task_id=task_id,
            user_id=str(user_id),
            remind_at=remind_at.isoformat(),
            channel=notification_channel.value,
        )

        # Validate remind_at is in the future
        if remind_at <= datetime.utcnow():
            raise ValueError("remind_at must be in the future")

        # Get task to verify it exists
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        # Create reminder record in database
        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            remind_at=remind_at,
            notification_channel=notification_channel,
            delivery_status=DeliveryStatus.PENDING,
        )

        self.session.add(reminder)
        await self.session.flush()
        await self.session.refresh(reminder)

        # Create Dapr Job for scheduled execution
        job_id = f"reminder-{reminder.id}"
        job_payload = {
            "reminder_id": reminder.id,
            "task_id": task_id,
            "user_id": str(user_id),
            "task_title": task.title,
            "task_description": task.description,
            "priority": task.priority,
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "notification_channel": notification_channel.value,
            "correlation_id": correlation_id,
        }

        # Calculate schedule time (ISO 8601 format for Dapr)
        schedule_time = remind_at.isoformat() + "Z"

        # Dapr Jobs API endpoint
        jobs_url = f"{self.dapr_base_url}/v1.0-alpha1/jobs/{job_id}"

        job_config = {
            "schedule": f"@once {schedule_time}",  # One-time execution at specific time
            "repeats": 1,
            "data": job_payload,
            "dueTime": schedule_time,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    jobs_url,
                    json=job_config,
                    headers={
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()

            logger.info(
                "Dapr Job scheduled successfully",
                job_id=job_id,
                reminder_id=reminder.id,
                task_id=task_id,
                remind_at=remind_at.isoformat(),
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                "Failed to schedule Dapr Job",
                job_id=job_id,
                reminder_id=reminder.id,
                error=str(e),
                response_body=e.response.text if hasattr(e, 'response') else None,
            )
            # Mark reminder as failed
            reminder.delivery_status = DeliveryStatus.FAILED
            reminder.error_message = f"Failed to schedule job: {str(e)}"
            await self.session.commit()
            raise

        await self.session.commit()
        await self.session.refresh(reminder)

        return reminder

    async def schedule_reminders_for_task(
        self,
        task_id: int,
        user_id: UUID,
        due_at: datetime,
        reminder_offset_minutes: list[int],
        notification_channel: NotificationChannel = NotificationChannel.IN_APP,
        correlation_id: Optional[str] = None,
    ) -> list[Reminder]:
        """Schedule multiple reminders for a task based on offset minutes.

        Args:
            task_id: Task ID to remind about
            user_id: User ID to send reminders to
            due_at: When the task is due (UTC)
            reminder_offset_minutes: List of minutes before due_at to send reminders
            notification_channel: Channel to deliver notifications
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of created reminder instances
        """
        reminders = []

        for offset in reminder_offset_minutes:
            remind_at = due_at - timedelta(minutes=offset)

            # Skip if remind_at is in the past
            if remind_at <= datetime.utcnow():
                logger.warning(
                    "Skipping reminder (in the past)",
                    task_id=task_id,
                    remind_at=remind_at.isoformat(),
                    offset_minutes=offset,
                )
                continue

            try:
                reminder = await self.schedule_reminder(
                    task_id=task_id,
                    user_id=user_id,
                    remind_at=remind_at,
                    notification_channel=notification_channel,
                    correlation_id=correlation_id,
                )
                reminders.append(reminder)
            except Exception as e:
                logger.error(
                    "Failed to schedule reminder",
                    task_id=task_id,
                    offset_minutes=offset,
                    error=str(e),
                )
                # Continue scheduling other reminders

        return reminders

    async def cancel_reminders(
        self,
        task_id: int,
        user_id: UUID,
        correlation_id: Optional[str] = None,
    ) -> int:
        """Cancel all pending reminders for a task.

        Called when a task is completed or deleted.

        Args:
            task_id: Task ID to cancel reminders for
            user_id: User ID (for authorization)
            correlation_id: Optional correlation ID for tracing

        Returns:
            Number of reminders cancelled
        """
        logger.info(
            "Cancelling reminders",
            task_id=task_id,
            user_id=str(user_id),
        )

        # Get all pending reminders for this task
        result = await self.session.execute(
            select(Reminder).where(
                Reminder.task_id == task_id,
                Reminder.user_id == user_id,
                Reminder.delivery_status == DeliveryStatus.PENDING,
            )
        )
        reminders = result.scalars().all()

        cancelled_count = 0

        for reminder in reminders:
            job_id = f"reminder-{reminder.id}"

            # Delete Dapr Job
            try:
                jobs_url = f"{self.dapr_base_url}/v1.0-alpha1/jobs/{job_id}"
                async with httpx.AsyncClient() as client:
                    response = await client.delete(
                        jobs_url,
                        timeout=10.0,
                    )
                    # 204 No Content or 404 Not Found are both acceptable
                    if response.status_code not in [204, 404]:
                        response.raise_for_status()

                logger.info(
                    "Dapr Job deleted successfully",
                    job_id=job_id,
                    reminder_id=reminder.id,
                )
            except Exception as e:
                logger.error(
                    "Failed to delete Dapr Job",
                    job_id=job_id,
                    reminder_id=reminder.id,
                    error=str(e),
                )
                # Continue cancelling other reminders

            # Update reminder status
            reminder.delivery_status = DeliveryStatus.CANCELLED
            reminder.updated_at = datetime.utcnow()
            cancelled_count += 1

        await self.session.commit()

        logger.info(
            "Reminders cancelled",
            task_id=task_id,
            cancelled_count=cancelled_count,
        )

        return cancelled_count

    async def reschedule_reminders(
        self,
        task_id: int,
        user_id: UUID,
        new_due_at: datetime,
        reminder_offset_minutes: list[int],
        notification_channel: NotificationChannel = NotificationChannel.IN_APP,
        correlation_id: Optional[str] = None,
    ) -> list[Reminder]:
        """Reschedule reminders when task due date changes.

        Cancels existing pending reminders and creates new ones based on new due date.

        Args:
            task_id: Task ID to reschedule reminders for
            user_id: User ID (for authorization)
            new_due_at: New due date for the task (UTC)
            reminder_offset_minutes: List of minutes before due_at to send reminders
            notification_channel: Channel to deliver notifications
            correlation_id: Optional correlation ID for tracing

        Returns:
            List of newly created reminder instances
        """
        logger.info(
            "Rescheduling reminders",
            task_id=task_id,
            user_id=str(user_id),
            new_due_at=new_due_at.isoformat(),
        )

        # Cancel existing pending reminders
        await self.cancel_reminders(
            task_id=task_id,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        # Schedule new reminders
        reminders = await self.schedule_reminders_for_task(
            task_id=task_id,
            user_id=user_id,
            due_at=new_due_at,
            reminder_offset_minutes=reminder_offset_minutes,
            notification_channel=notification_channel,
            correlation_id=correlation_id,
        )

        logger.info(
            "Reminders rescheduled",
            task_id=task_id,
            new_reminder_count=len(reminders),
        )

        return reminders

    async def get_reminders_for_task(
        self,
        task_id: int,
        user_id: UUID,
    ) -> list[Reminder]:
        """Get all reminders for a task.

        Args:
            task_id: Task ID to get reminders for
            user_id: User ID (for authorization)

        Returns:
            List of reminder instances
        """
        result = await self.session.execute(
            select(Reminder).where(
                Reminder.task_id == task_id,
                Reminder.user_id == user_id,
            ).order_by(Reminder.remind_at.asc())
        )
        return list(result.scalars().all())
