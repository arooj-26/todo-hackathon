"""
add_task MCP tool implementation.

Creates a new todo task for the user.
"""
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum
from uuid import uuid4
from sqlmodel import Session, select

from ...database.connection import engine
from ...models.task import Task
from ...models import PriorityEnum


class Priority(str, Enum):
    """Priority enum for task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AddTaskParams(BaseModel):
    """Parameter schema for add_task tool."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, max_length=10000, description="Optional task description")
    due_date: datetime | None = Field(None, description="Optional due date in ISO 8601 format")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority")


def add_task(params: AddTaskParams) -> dict:
    """
    Create a new todo task for the user.

    Args:
        params: Task creation parameters

    Returns:
        dict: Response containing task_id, status, title, and error
            {
                "task_id": str (UUID),
                "status": "created" | "error",
                "title": str,
                "error": str | None
            }
    """
    try:
        # Trim whitespace from title
        title = params.title.strip()

        # Validate title is not empty after trimming
        if not title:
            return {
                "task_id": None,
                "status": "error",
                "title": None,
                "error": "Title cannot be empty"
            }

        # Create task instance
        task = Task(
            id=uuid4(),
            user_id=params.user_id,
            title=title,
            description=params.description,
            due_date=params.due_date,
            priority=PriorityEnum(params.priority.value),
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save to database
        with Session(engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": str(task.id),
                "status": "created",
                "title": task.title,
                "error": None
            }

    except Exception as e:
        return {
            "task_id": None,
            "status": "error",
            "title": None,
            "error": f"Database operation failed: {str(e)}"
        }
