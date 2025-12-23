"""
list_tasks MCP tool implementation.

Retrieves tasks for the user with optional filtering and sorting.
"""
from pydantic import BaseModel, Field, UUID4
from enum import Enum
from sqlmodel import Session, select
from typing import List, Dict, Any

from ...database.connection import engine
from ...models.task import Task
from ...models import PriorityEnum


class TaskStatus(str, Enum):
    """Task status filter enum."""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class SortBy(str, Enum):
    """Sort field enum."""
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"


class Priority(str, Enum):
    """Priority enum for filtering."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ListTasksParams(BaseModel):
    """Parameter schema for list_tasks tool."""
    user_id: UUID4 = Field(..., description="User ID whose tasks to list")
    status: TaskStatus = Field(TaskStatus.ALL, description="Filter by completion status")
    priority: Priority | None = Field(None, description="Filter by priority")
    sort_by: SortBy = Field(SortBy.CREATED_AT, description="Sort field")


def _task_to_dict(task: Task) -> Dict[str, Any]:
    """Convert Task model to dictionary for response."""
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority.value if task.priority else "medium"
    }


def list_tasks(params: ListTasksParams) -> dict:
    """
    List todo tasks for the user with optional filters and sorting.

    Args:
        params: List parameters including filters and sort options

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
            # Start with base query filtering by user_id
            query = select(Task).where(Task.user_id == params.user_id)

            # Apply status filter
            if params.status == TaskStatus.PENDING:
                query = query.where(Task.completed == False)
            elif params.status == TaskStatus.COMPLETED:
                query = query.where(Task.completed == True)
            # TaskStatus.ALL - no additional filter

            # Apply priority filter if provided
            if params.priority:
                query = query.where(Task.priority == PriorityEnum(params.priority.value))

            # Apply sorting
            if params.sort_by == SortBy.CREATED_AT:
                query = query.order_by(Task.created_at)
            elif params.sort_by == SortBy.DUE_DATE:
                query = query.order_by(Task.due_date)
            elif params.sort_by == SortBy.PRIORITY:
                query = query.order_by(Task.priority)

            # Execute query
            tasks = session.exec(query).all()

            # Convert to response format
            task_dicts = [_task_to_dict(task) for task in tasks]

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
