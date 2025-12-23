"""
complete_task MCP tool implementation.

Marks a task as complete.
"""
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from sqlmodel import Session, select

from ...database.connection import engine
from ...models.task import Task


class CompleteTaskParams(BaseModel):
    """Parameter schema for complete_task tool."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to mark complete")


def complete_task(params: CompleteTaskParams) -> dict:
    """
    Mark a todo task as complete.

    Args:
        params: Completion parameters with user_id and task_id

    Returns:
        dict: Response containing task_id, status, title, and error
            {
                "task_id": str (UUID),
                "status": "completed" | "error",
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

            # Mark as completed (idempotent - works even if already completed)
            task.completed = True
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": str(task.id),
                "status": "completed",
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
