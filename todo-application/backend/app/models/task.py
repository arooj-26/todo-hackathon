"""Task model."""
from datetime import datetime
from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    """
    Task model for user's todo items.

    Attributes:
        id: Primary key, auto-incremented
        user_id: Foreign key to users table
        description: Task description (1-1000 characters)
        completed: Completion status (default: False)
        priority: Priority level (low, medium, high)
        created_at: Timestamp of task creation
        updated_at: Timestamp of last update
    """

    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    description: str = Field(nullable=False, min_length=1, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    priority: str = Field(default="medium", nullable=False, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
