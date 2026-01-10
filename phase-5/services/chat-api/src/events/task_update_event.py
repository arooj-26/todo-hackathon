"""TaskUpdateEvent schema for task-updates Kafka topic."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskUpdateEventType(str, Enum):
    """Task update event type enumeration."""

    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"


class TaskUpdateEvent(BaseModel):
    """Lightweight event for real-time UI updates when tasks change.

    Published to: task-updates Kafka topic
    Consumers: WebSocket Service (future), Frontend (via WebSocket)
    Retention: 1 day (short-lived, real-time updates only)
    """

    # Schema versioning
    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description="Schema version for backward compatibility",
    )

    # Event metadata
    event_type: TaskUpdateEventType = Field(description="Type of task update event")
    task_id: int = Field(gt=0, description="Task identifier that was updated")
    user_id: UUID = Field(description="User who owns the task")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp (UTC)",
    )
    correlation_id: UUID = Field(
        default_factory=uuid4,
        description="Correlation ID for distributed tracing",
    )

    # Change summary (for optimistic UI updates)
    changed_fields: list[str] = Field(
        default_factory=list,
        description="List of fields that changed (for task_updated events)",
    )
    new_status: Optional[str] = Field(
        default=None,
        description="New status if status changed (todo/in_progress/completed)",
    )
    new_priority: Optional[str] = Field(
        default=None,
        description="New priority if priority changed (high/medium/low)",
    )

    # Recurring task support
    next_task_id: Optional[int] = Field(
        default=None,
        description="ID of next recurring task if event_type is task_completed and task is recurring",
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            UUID: lambda v: str(v),
        }

    @classmethod
    def created(
        cls,
        task_id: int,
        user_id: UUID,
        correlation_id: UUID | None = None,
    ) -> "TaskUpdateEvent":
        """Create a task_created event.

        Args:
            task_id: Task ID
            user_id: User ID
            correlation_id: Optional correlation ID

        Returns:
            TaskUpdateEvent instance
        """
        return cls(
            event_type=TaskUpdateEventType.TASK_CREATED,
            task_id=task_id,
            user_id=user_id,
            correlation_id=correlation_id or uuid4(),
        )

    @classmethod
    def completed(
        cls,
        task_id: int,
        user_id: UUID,
        next_task_id: Optional[int] = None,
        correlation_id: UUID | None = None,
    ) -> "TaskUpdateEvent":
        """Create a task_completed event.

        Args:
            task_id: Task ID
            user_id: User ID
            next_task_id: Optional ID of next recurring instance
            correlation_id: Optional correlation ID

        Returns:
            TaskUpdateEvent instance
        """
        return cls(
            event_type=TaskUpdateEventType.TASK_COMPLETED,
            task_id=task_id,
            user_id=user_id,
            changed_fields=["status", "completed_at"],
            new_status="completed",
            next_task_id=next_task_id,
            correlation_id=correlation_id or uuid4(),
        )
