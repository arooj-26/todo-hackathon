"""
update_task MCP tool implementation.

Modifies task title, description, priority, or due date.
"""
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum
from sqlmodel import Session, select

from ...database.connection import engine
from ...models.task import Task
from ...models import PriorityEnum


class Priority(str, Enum):
    """Priority enum for task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UpdateTaskParams(BaseModel):
    """Parameter schema for update_task tool."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to update")
    title: str | None = Field(None, min_length=1, max_length=500, description="New task title")
    description: str | None = Field(None, max_length=10000, description="New task description")
    priority: Priority | None = Field(None, description="New priority")
    due_date: datetime | None = Field(None, description="New due date")


def update_task(params: UpdateTaskParams) -> dict:
    """
    Update a todo task's properties (partial update supported).

    Args:
        params: Update parameters with fields to modify

    Returns:
        dict: Response containing task_id, status, title, and error
            {
                "task_id": str (UUID),
                "status": "updated" | "error",
                "title": str,
                "error": str | None
            }
    """
    try:
        with Session(engine) as session:
            # Query for task with user_id filter (data isolation)
            query = select(Task).where(
                Task.id == params.task_id,
                Task.user_id == params.user_id
            )
            task = session.exec(query).first()

            if not task:
                return {
                    "task_id": str(params.task_id),
                    "status": "error",
                    "title": None,
                    "error": "Task not found"
                }

            # Update only provided fields (partial update)
            if params.title is not None:
                # Trim whitespace
                title = params.title.strip()
                if not title:
                    return {
                        "task_id": str(params.task_id),
                        "status": "error",
                        "title": None,
                        "error": "Title cannot be empty"
                    }
                task.title = title

            if params.description is not None:
                task.description = params.description

            if params.priority is not None:
                task.priority = PriorityEnum(params.priority.value)

            if params.due_date is not None:
                task.due_date = params.due_date

            # Always update timestamp
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": str(task.id),
                "status": "updated",
                "title": task.title,
                "error": None
            }

    except Exception as e:
        return {
            "task_id": str(params.task_id),
            "status": "error",
            "title": None,
            "error": f"Database operation failed: {str(e)}"
        }
