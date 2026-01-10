"""TaskEvent schema for task-events Kafka topic."""

from datetime import datetime
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TaskEventType(str, Enum):
    """Task event type enumeration."""

    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"


class TaskEvent(BaseModel):
    """Event published when a task is created, updated, completed, or deleted.

    Published to: task-events Kafka topic
    Consumers: Recurring Task Service, Audit Service
    Retention: 90 days
    """

    # Schema versioning for backward compatibility
    schema_version: Literal["1.0"] = Field(
        default="1.0",
        description="Schema version for backward compatibility",
    )

    # Event metadata
    event_type: TaskEventType = Field(description="Type of task event")
    task_id: int = Field(gt=0, description="Unique task identifier")
    user_id: UUID = Field(description="User who owns the task")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event timestamp (UTC)",
    )
    correlation_id: UUID = Field(
        default_factory=uuid4,
        description="Correlation ID for distributed tracing",
    )

    # Task snapshot at time of event
    task_snapshot: dict = Field(
        description="Complete task state at time of event (includes all fields)"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z",
            UUID: lambda v: str(v),
        }

    @classmethod
    def from_task(
        cls,
        event_type: TaskEventType,
        task: dict,
        correlation_id: UUID | None = None,
    ) -> "TaskEvent":
        """Create TaskEvent from task data.

        Args:
            event_type: Type of event
            task: Task data as dict (from Task.dict())
            correlation_id: Optional correlation ID

        Returns:
            TaskEvent instance
        """
        return cls(
            event_type=event_type,
            task_id=task["id"],
            user_id=task["user_id"],
            task_snapshot=task,
            correlation_id=correlation_id or uuid4(),
        )
