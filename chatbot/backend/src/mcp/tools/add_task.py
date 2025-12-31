"""
add_task MCP tool implementation.

Creates a new todo task for the user.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import uuid4
from sqlmodel import Session, select
from typing import Optional

from ...database.connection import engine
from ...models.task import Task
from ...models import PriorityEnum


class AddTaskParams(BaseModel):
    """Parameter schema for add_task tool."""
    user_id: int = Field(..., description="User ID who owns the task")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, max_length=10000, description="Optional task description")
    priority: Optional[str] = Field(None, description="Optional priority level (low, medium, high)")
    due_date: Optional[datetime] = Field(None, description="Optional due date for the task")
    recurrence: Optional[str] = Field(None, description="Optional recurrence pattern (daily, weekly, monthly)")


def add_task(user_id: int, title: str, description: str = None, priority: Optional[str] = None, due_date: Optional[datetime] = None, recurrence: Optional[str] = None) -> dict:
    """
    Create a new todo task for the user using the todo application schema.

    Args:
        user_id: User ID who owns the task
        title: Task title (used as description in todo app)
        description: Optional task description
        priority: Optional priority level (low, medium, high)
        due_date: Optional due date for the task
        recurrence: Optional recurrence pattern (daily, weekly, monthly)

    Returns:
        dict: Response containing task_id, status, title, and error
            {
                "task_id": str (integer),
                "status": "created" | "error",
                "title": str,
                "error": str | None
            }
    """
    try:
        # Trim whitespace from title
        title = title.strip()

        # Validate title is not empty after trimming
        if not title:
            return {
                "task_id": None,
                "status": "error",
                "title": None,
                "error": "Title cannot be empty"
            }

        # Validate priority if provided
        if priority and priority not in ["low", "medium", "high"]:
            return {
                "task_id": None,
                "status": "error",
                "title": None,
                "error": "Invalid priority value. Must be 'low', 'medium', or 'high'"
            }

        # Validate recurrence if provided
        if recurrence and recurrence not in ["daily", "weekly", "monthly"]:
            return {
                "task_id": None,
                "status": "error",
                "title": None,
                "error": "Invalid recurrence value. Must be 'daily', 'weekly', or 'monthly'"
            }

        # Create task instance compatible with todo app schema - let database auto-generate the ID
        task = Task(
            user_id=user_id,  # Use string user_id as defined in the model
            description=title,  # Use title as description (todo app field name)
            completed=False,
            priority=priority if priority else "medium",  # Use provided priority or default to medium
            due_date=due_date,
            recurrence=recurrence
        )

        # Save to database
        with Session(engine) as session:
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": str(task.id),
                "status": "created",
                "title": task.description,  # Return description as title for consistency
                "error": None
            }

    except Exception as e:
        return {
            "task_id": None,
            "status": "error",
            "title": None,
            "error": f"Database operation failed: {str(e)}"
        }
