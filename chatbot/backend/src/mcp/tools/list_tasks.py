"""
list_tasks MCP tool implementation.

Retrieves tasks for the user with optional filtering.
"""
from pydantic import BaseModel, Field
from enum import Enum
from sqlmodel import Session, select
from typing import List, Dict, Any, Optional
from uuid import UUID
import uuid
from datetime import datetime

from ...database.connection import engine
from ...models.task import Task
from ...models import PriorityEnum


class TaskStatus(str, Enum):
    """Task status filter enum."""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class ListTasksParams(BaseModel):
    """Parameter schema for list_tasks tool."""
    user_id: int = Field(..., description="User ID")
    status: TaskStatus = Field("all", description="Filter by completion status")
    due_date: Optional[datetime] = Field(None, description="Filter by specific due date")
    has_due_date: Optional[bool] = Field(None, description="Filter by presence of due date")
    recurrence: Optional[str] = Field(None, description="Filter by recurrence pattern")


def list_tasks(user_id: int, status: str = "all", due_date: Optional[datetime] = None, has_due_date: Optional[bool] = None, recurrence: Optional[str] = None) -> dict:
    """
    List todo tasks for the user with optional filtering using todo application schema.

    Args:
        user_id: User ID
        status: Filter by completion status ("all", "pending", "completed", "overdue")
        due_date: Filter by specific due date
        has_due_date: Filter by presence of due date
        recurrence: Filter by recurrence pattern

    Returns:
        dict: Response containing tasks array, count, and error
            {
                "tasks": List[dict],
                "count": int,
                "error": str | None
            }
    """
    try:
        with Session(engine) as session:
            # Start with base query filtering by user_id (using todo app schema)
            query = select(Task).where(Task.user_id == user_id)

            # Apply status filter
            if status == "PENDING" or status == "pending":
                query = query.where(Task.completed == False)
            elif status == "COMPLETED" or status == "completed":
                query = query.where(Task.completed == True)
            elif status == "OVERDUE" or status == "overdue":
                query = query.where(Task.completed == False).where(Task.due_date < datetime.utcnow())
            # "ALL" or default - no additional filter

            # Apply due date filter
            if due_date:
                query = query.where(Task.due_date == due_date)

            # Apply has due date filter
            if has_due_date is not None:
                if has_due_date:
                    query = query.where(Task.due_date.is_not(None))
                else:
                    query = query.where(Task.due_date.is_(None))

            # Apply recurrence filter
            if recurrence:
                query = query.where(Task.recurrence == recurrence)

            # Execute query
            tasks = session.exec(query).all()

            # Convert to response format (adapt to chatbot format)
            task_dicts = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.description,  # Use description as title for consistency
                    "description": task.description,
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence
                }
                task_dicts.append(task_dict)

            return {
                "tasks": task_dicts,
                "count": len(task_dicts),
                "error": None
            }

    except Exception as e:
        return {
            "tasks": [],
            "count": 0,
            "error": f"Database query failed: {str(e)}"
        }
