"""
delete_task MCP tool implementation.

Permanently removes a task.
"""
from pydantic import BaseModel, Field, UUID4
from sqlmodel import Session, select

from ...database.connection import engine
from ...models.task import Task


class DeleteTaskParams(BaseModel):
    """Parameter schema for delete_task tool."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to delete")


def delete_task(params: DeleteTaskParams) -> dict:
    """
    Permanently delete a todo task.

    Args:
        params: Deletion parameters with user_id and task_id

    Returns:
        dict: Response containing task_id, status, title, and error
            {
                "task_id": str (UUID),
                "status": "deleted" | "error",
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

            # Retrieve title before deletion (for confirmation)
            task_title = task.title
            task_id = task.id

            # Delete the task
            session.delete(task)
            session.commit()

            return {
                "task_id": str(task_id),
                "status": "deleted",
                "title": task_title,
                "error": None
            }

    except Exception as e:
        return {
            "task_id": str(params.task_id),
            "status": "error",
            "title": None,
            "error": f"Database operation failed: {str(e)}"
        }
