"""
update_task MCP tool implementation.

Modifies task title, description, due date, or recurrence.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from sqlmodel import Session, select
from typing import Optional

from ...database.connection import engine
from ...models.task import Task
from ...models import PriorityEnum


class UpdateTaskParams(BaseModel):
    """Parameter schema for update_task tool."""
    user_id: int = Field(..., description="User ID who owns the task")
    task_id: int = Field(None, description="Task ID to update (optional if task_name is provided)")
    task_name: str = Field(None, description="Task name/title to search and update (optional if task_id is provided)")
    title: str | None = Field(None, min_length=1, max_length=500, description="New task title")
    description: str | None = Field(None, max_length=10000, description="New task description")
    priority: Optional[str] = Field(None, description="New priority level (low, medium, high)")
    due_date: Optional[datetime] = Field(None, description="New due date for the task")
    recurrence: Optional[str] = Field(None, description="New recurrence pattern (daily, weekly, monthly)")


def update_task(user_id: int, task_id: int = None, task_name: str = None, title: str = None, description: str = None, priority: Optional[str] = None, due_date: Optional[datetime] = None, recurrence: Optional[str] = None) -> dict:
    """
    Update a todo task's properties using todo application schema (partial update supported).

    Args:
        user_id: User ID who owns the task
        task_id: Task ID to update (optional if task_name is provided)
        task_name: Task name/title to search and update (optional if task_id is provided)
        title: New task title (used as description in todo app) (optional)
        description: New task description (optional)
        priority: New priority level (low, medium, high) (optional)
        due_date: New due date for the task (optional)
        recurrence: New recurrence pattern (daily, weekly, monthly) (optional)

    Returns:
        dict: Response containing task_id, status, title, and error
            {
                "task_id": str (integer),
                "status": "updated" | "error",
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

            # Update only provided fields (partial update)
            if title is not None:
                # Trim whitespace
                title = title.strip()
                if not title:
                    return {
                        "task_id": str(task_id),
                        "status": "error",
                        "title": None,
                        "error": "Title cannot be empty"
                    }
                task.description = title  # Use title as description for todo app compatibility

            if description is not None:
                task.description = description

            if priority is not None:
                # Validate priority if provided
                if priority not in ["low", "medium", "high"]:
                    return {
                        "task_id": str(task_id),
                        "status": "error",
                        "title": None,
                        "error": "Invalid priority value. Must be 'low', 'medium', or 'high'"
                    }
                task.priority = priority

            if due_date is not None:
                task.due_date = due_date

            if recurrence is not None:
                # Validate recurrence if provided
                if recurrence not in ["daily", "weekly", "monthly"]:
                    return {
                        "task_id": str(task_id),
                        "status": "error",
                        "title": None,
                        "error": "Invalid recurrence value. Must be 'daily', 'weekly', or 'monthly'"
                    }
                task.recurrence = recurrence

            # Always update timestamp
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "task_id": str(task.id),
                "status": "updated",
                "title": task.description,  # Return description as title for consistency
                "error": None
            }

    except Exception as e:
        return {
            "task_id": str(task_id),
            "status": "error",
            "title": None,
            "error": f"Database operation failed: {str(e)}"
        }
