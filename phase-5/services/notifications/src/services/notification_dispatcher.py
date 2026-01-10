"""Notification dispatcher with multiple channel support and retry logic."""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ..logging_config import get_logger

logger = get_logger(__name__)


class NotificationChannel(str, Enum):
    """Notification delivery channel."""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class NotificationRequest(BaseModel):
    """Notification request data."""

    user_id: UUID
    task_id: int
    task_title: str
    task_description: Optional[str] = None
    priority: str
    due_at: Optional[datetime] = None
    channel: str


class NotificationDispatcher:
    """Dispatcher for sending notifications through multiple channels.

    Supports in-app notifications, email, and SMS with retry logic for
    failed deliveries.
    """

    def __init__(self):
        """Initialize notification dispatcher."""
        self.max_retries = 3
        self.retry_delay_seconds = 5

    async def send_notification(
        self,
        request: NotificationRequest,
    ) -> bool:
        """Send notification through specified channel with retry logic.

        Args:
            request: Notification request data

        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        logger.info(
            "Sending notification",
            user_id=str(request.user_id),
            task_id=request.task_id,
            channel=request.channel,
        )

        # Dispatch to appropriate channel
        channel = NotificationChannel(request.channel)

        for attempt in range(1, self.max_retries + 1):
            try:
                if channel == NotificationChannel.IN_APP:
                    success = await self._send_in_app_notification(request)
                elif channel == NotificationChannel.EMAIL:
                    success = await self._send_email_notification(request)
                elif channel == NotificationChannel.SMS:
                    success = await self._send_sms_notification(request)
                else:
                    logger.error(
                        "Unknown notification channel",
                        channel=request.channel,
                    )
                    return False

                if success:
                    logger.info(
                        "Notification sent successfully",
                        user_id=str(request.user_id),
                        task_id=request.task_id,
                        channel=request.channel,
                        attempt=attempt,
                    )
                    return True
                else:
                    logger.warning(
                        "Notification delivery failed",
                        user_id=str(request.user_id),
                        task_id=request.task_id,
                        channel=request.channel,
                        attempt=attempt,
                    )

                    # Retry with exponential backoff
                    if attempt < self.max_retries:
                        delay = self.retry_delay_seconds * (2 ** (attempt - 1))
                        logger.info(
                            "Retrying notification delivery",
                            user_id=str(request.user_id),
                            task_id=request.task_id,
                            delay_seconds=delay,
                            attempt=attempt + 1,
                        )
                        await asyncio.sleep(delay)

            except Exception as e:
                logger.error(
                    "Notification delivery error",
                    user_id=str(request.user_id),
                    task_id=request.task_id,
                    channel=request.channel,
                    attempt=attempt,
                    error=str(e),
                    exc_info=True,
                )

                # Retry on exception
                if attempt < self.max_retries:
                    delay = self.retry_delay_seconds * (2 ** (attempt - 1))
                    logger.info(
                        "Retrying after error",
                        delay_seconds=delay,
                        attempt=attempt + 1,
                    )
                    await asyncio.sleep(delay)

        logger.error(
            "Notification delivery failed after all retries",
            user_id=str(request.user_id),
            task_id=request.task_id,
            channel=request.channel,
            max_retries=self.max_retries,
        )
        return False

    async def _send_in_app_notification(
        self,
        request: NotificationRequest,
    ) -> bool:
        """Send in-app notification.

        In a real implementation, this would:
        - Store notification in database
        - Send via WebSocket to connected clients
        - Push to notification service (e.g., Firebase Cloud Messaging)

        Args:
            request: Notification request data

        Returns:
            bool: True if sent successfully
        """
        logger.info(
            "Sending in-app notification",
            user_id=str(request.user_id),
            task_id=request.task_id,
            task_title=request.task_title,
        )

        # Simulate in-app notification
        # In production, this would:
        # 1. Store in notifications table
        # 2. Send via WebSocket to connected user
        # 3. Push to mobile app via FCM/APNS

        message = self._format_notification_message(request)

        logger.info(
            "In-app notification simulated",
            user_id=str(request.user_id),
            task_id=request.task_id,
            message=message,
        )

        # Simulate success
        return True

    async def _send_email_notification(
        self,
        request: NotificationRequest,
    ) -> bool:
        """Send email notification.

        In a real implementation, this would use an email service like:
        - SendGrid
        - AWS SES
        - Mailgun

        Args:
            request: Notification request data

        Returns:
            bool: True if sent successfully
        """
        logger.info(
            "Sending email notification",
            user_id=str(request.user_id),
            task_id=request.task_id,
            task_title=request.task_title,
        )

        # Simulate email sending
        message = self._format_notification_message(request)

        logger.info(
            "Email notification simulated",
            user_id=str(request.user_id),
            task_id=request.task_id,
            message=message,
        )

        # Simulate success
        return True

    async def _send_sms_notification(
        self,
        request: NotificationRequest,
    ) -> bool:
        """Send SMS notification.

        In a real implementation, this would use an SMS service like:
        - Twilio
        - AWS SNS
        - Vonage

        Args:
            request: Notification request data

        Returns:
            bool: True if sent successfully
        """
        logger.info(
            "Sending SMS notification",
            user_id=str(request.user_id),
            task_id=request.task_id,
            task_title=request.task_title,
        )

        # Simulate SMS sending
        message = self._format_notification_message(request)

        logger.info(
            "SMS notification simulated",
            user_id=str(request.user_id),
            task_id=request.task_id,
            message=message,
        )

        # Simulate success
        return True

    def _format_notification_message(
        self,
        request: NotificationRequest,
    ) -> str:
        """Format notification message.

        Args:
            request: Notification request data

        Returns:
            str: Formatted notification message
        """
        if request.due_at:
            # Calculate time until due
            now = datetime.utcnow()
            time_diff = request.due_at - now
            hours_until_due = time_diff.total_seconds() / 3600

            if hours_until_due < 1:
                time_str = f"{int(time_diff.total_seconds() / 60)} minutes"
            elif hours_until_due < 24:
                time_str = f"{int(hours_until_due)} hours"
            else:
                time_str = f"{int(hours_until_due / 24)} days"

            return (
                f"Reminder: '{request.task_title}' is due in {time_str}. "
                f"Priority: {request.priority.upper()}"
            )
        else:
            return f"Reminder: '{request.task_title}'. Priority: {request.priority.upper()}"
