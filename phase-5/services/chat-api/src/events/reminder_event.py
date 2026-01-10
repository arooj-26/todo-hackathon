"""ReminderEvent schema for reminders Kafka topic."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ReminderEventType(str, Enum):
    """Reminder event type enumeration."""

    REMINDER_DUE = "reminder_due"
    REMINDER_SENT = "reminder_sent"
    REMINDER_FAILED = "reminder_failed"


class NotificationChannel(str, Enum):
    """Notification delivery channel."""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class ReminderEvent(BaseModel):
    """Event published when a reminder is due to be sent to the user.

    Published to: reminders Kafka topic
    Consumers: Notification Service
    Retention: 7 days
    """

    # Schema versioning
    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description="Schema version for backward compatibility",
    )

    # Event metadata
    event_type: ReminderEventType = Field(description="Type of reminder event")
    reminder_id: int = Field(gt=0, description="Unique reminder identifier")
    task_id: int = Field(gt=0, description="Associated task identifier")
    user_id: UUID = Field(description="User to receive the reminder")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp (UTC)",
    )
    correlation_id: UUID = Field(
        default_factory=uuid4,
        description="Correlation ID for distributed tracing",
    )

    # Reminder details
    due_at: datetime = Field(description="When the task is due (UTC)")
    remind_at: datetime = Field(description="When the reminder should be sent (UTC)")
    task_title: str = Field(max_length=200, description="Task title for the reminder message")
    task_description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description",
    )
    priority: str = Field(description="Task priority level (high/medium/low)")

    # Notification settings
    notification_channel: NotificationChannel = Field(
        default=NotificationChannel.IN_APP,
        description="Channel for reminder delivery",
    )
    retry_count: int = Field(
        default=0,
        ge=0,
        description="Number of delivery retry attempts",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if event_type is reminder_failed",
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            UUID: lambda v: str(v),
        }
