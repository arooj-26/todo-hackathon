"""
Task model for todo items (matching todo application schema).

Represents a single todo task owned by a user.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class Task(SQLModel, table=True):
    """
    Task model representing a todo item (matching todo application schema).

    Attributes:
        id: Primary key, auto-incremented
        user_id: User ID of the task owner (no foreign key constraint)
        description: Task description (1-1000 characters)
        completed: Completion status (default: False)
        priority: Priority level (low, medium, high)
        due_date: Optional due date for the task
        recurrence: Recurrence pattern (daily, weekly, monthly, or null)
        created_at: Timestamp of task creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False, index=True)  # Integer to match todo app backend
    description: str = Field(nullable=False, min_length=1, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    priority: str = Field(default="medium", nullable=False, max_length=20)
    due_date: Optional[datetime] = Field(default=None, nullable=True)
    recurrence: Optional[str] = Field(default=None, nullable=True, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
