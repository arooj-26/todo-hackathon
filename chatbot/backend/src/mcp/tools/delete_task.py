"""
delete_task MCP tool implementation.

Permanently removes a task.
"""
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from uuid import UUID
import uuid

from ...database.connection import engine
from ...models.task import Task


class DeleteTaskParams(BaseModel):
    """Parameter schema for delete_task tool."""
    user_id: int = Field(..., description="User ID who owns the task")
    task_id: int = Field(None, description="Task ID to delete (optional if task_name is provided)")
    task_name: str = Field(None, description="Task name/title to delete (optional if task_id is provided)")


def delete_task(user_id: int, task_id: int = None, task_name: str = None) -> dict:
    """
    Permanently delete a todo task using todo application schema.

    Args:
        user_id: User ID who owns the task
        task_id: Task ID to delete (optional if task_name is provided)
        task_name: Task name/title to search and delete (optional if task_id is provided)

    Returns:
        dict: Response containing task_id, status, title, and error
            {
                "task_id": str (integer),
                "status": "deleted" | "error",
                "title": str,
                "error": str | None
            }
    """
    try:
        with Session(engine) as session:
            # If task_name is provided, search for task by name
            if task_name and not task_id:
                # Search for tasks matching the name (case-insensitive partial match)
                query = select(Task).where(
                    Task.user_id == user_id,
                    Task.description.ilike(f"%{task_name}%")
                )
                matching_tasks = session.exec(query).all()

                if not matching_tasks:
                    return {
                        "task_id": None,
                        "status": "error",
                        "title": None,
                        "error": f"No task found with name containing '{task_name}'"
                    }

                if len(matching_tasks) > 1:
                    # Multiple matches found - return error with list
                    task_list = [f"ID {t.id}: {t.description}" for t in matching_tasks]
                    return {
                        "task_id": None,
                        "status": "error",
                        "title": None,
                        "error": f"Multiple tasks found matching '{task_name}': {', '.join(task_list)}. Please specify which one."
                    }

                # Single match found
                task = matching_tasks[0]
                task_id = task.id

            elif task_id:
                # Query for task with user_id and task_id filter (data isolation)
                query = select(Task).where(
                    Task.id == task_id,
                    Task.user_id == user_id
                )
                task = session.exec(query).first()

                if not task:
                    return {
                        "task_id": str(task_id),
                        "status": "error",
                        "title": None,
                        "error": "Task not found"
                    }
            else:
                return {
                    "task_id": None,
                    "status": "error",
                    "title": None,
                    "error": "Either task_id or task_name must be provided"
                }

            # Retrieve title before deletion (for confirmation)
            task_title = task.description  # Use description as title for consistency
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
            "task_id": str(task_id),
            "status": "error",
            "title": None,
            "error": f"Database operation failed: {str(e)}"
        }
