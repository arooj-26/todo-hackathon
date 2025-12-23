"""
Task model for todo items.

Represents a single todo task owned by a user.
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

from . import PriorityEnum


class Task(SQLModel, table=True):
    """
    Task model representing a todo item.

    Attributes:
        id: Unique task identifier (UUID)
        user_id: Owner of the task (UUID)
        title: Task title/summary (1-500 chars)
        description: Optional detailed description (max 10,000 chars)
        completed: Completion status (default: False)
        created_at: Creation timestamp (UTC)
        updated_at: Last modification timestamp (UTC)
        due_date: Optional due date (UTC)
        priority: Task priority ('low', 'medium', 'high', default: 'medium')
    """
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    description: Optional[str] = Field(default=None, max_length=10000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    due_date: Optional[datetime] = Field(default=None)
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        sa_column=Column(SQLEnum(PriorityEnum), nullable=False)
    )

    class Config:
        arbitrary_types_allowed = True
