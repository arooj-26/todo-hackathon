"""Reminder model for task due date notifications."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class DeliveryStatus(str, Enum):
    """Reminder delivery status."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationChannel(str, Enum):
    """Notification delivery channel."""

    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"


class ReminderBase(SQLModel):
    """Base reminder fields."""

    task_id: int = Field(foreign_key="tasks.id")
    user_id: int = Field(foreign_key="users.id")  # Changed from UUID to int to match Phase-4 User model
    remind_at: datetime = Field(description="When to send the reminder (UTC)")
    notification_channel: NotificationChannel = Field(
        default=NotificationChannel.IN_APP, description="Delivery channel"
    )


class Reminder(ReminderBase, table=True):
    """Reminder entity for scheduled notifications."""

    __tablename__ = "reminders"

    id: int = Field(default=None, primary_key=True)
    delivery_status: DeliveryStatus = Field(
        default=DeliveryStatus.PENDING, description="Current delivery status"
    )
    retry_count: int = Field(default=0, ge=0, le=10, description="Number of delivery attempts")
    error_message: Optional[str] = Field(default=None, description="Error message if delivery failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReminderCreate(ReminderBase):
    """Reminder creation schema."""

    pass


class ReminderUpdate(SQLModel):
    """Reminder update schema."""

    delivery_status: Optional[DeliveryStatus] = None
    retry_count: Optional[int] = Field(default=None, ge=0, le=10)
    error_message: Optional[str] = None


class ReminderResponse(ReminderBase):
    """Reminder response schema."""

    id: int
    delivery_status: DeliveryStatus
    retry_count: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
