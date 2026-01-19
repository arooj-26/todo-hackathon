"""Task model with status, priority, due dates, and full-text search."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class TaskStatus(str, Enum):
    """Task status enumeration."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskBase(SQLModel):
    """Base task fields for create/update operations."""

    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, max_length=10000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    due_at: Optional[datetime] = Field(default=None, description="Due date and time (UTC)")


class Task(TaskBase, table=True):
    """Task entity with full-text search and recurrence support.

    Note: Uses integer user_id to match Phase-4 auth backend.
    """

    __tablename__ = "tasks"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")  # Changed from UUID to int to match Phase-4
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Recurrence support
    recurrence_pattern_id: Optional[int] = Field(
        default=None,
        foreign_key="recurrence_patterns.id",
        description="Link to recurrence pattern (for parent tasks)",
    )
    parent_task_id: Optional[int] = Field(
        default=None,
        foreign_key="tasks.id",
        description="Parent task ID (for recurring instances)",
    )

    # Note: search_vector is a generated column in PostgreSQL, not managed by SQLModel


class TaskCreate(TaskBase):
    """Task creation schema."""

    tag_names: list[str] = Field(default_factory=list, description="Tag names to associate with task")
    recurrence_pattern: Optional[dict] = Field(
        default=None, description="Recurrence pattern configuration"
    )
    reminder_offset_minutes: Optional[int] = Field(
        default=None,
        ge=5,
        le=10080,
        description="Minutes before due_at to send reminder (5 min to 7 days)",
    )


class TaskUpdate(SQLModel):
    """Task update schema (all fields optional)."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=10000)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_at: Optional[datetime] = None
    tag_names: Optional[list[str]] = None


class TaskResponse(TaskBase):
    """Task response schema."""

    id: int
    user_id: int  # Changed from UUID to int to match Phase-4
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    recurrence_pattern_id: Optional[int]
    parent_task_id: Optional[int]
    tags: list[str] = Field(default_factory=list, description="Tag names associated with this task")


class TaskListResponse(SQLModel):
    """Paginated task list response."""

    tasks: list[TaskResponse]
    total: int
    limit: int
    offset: int
