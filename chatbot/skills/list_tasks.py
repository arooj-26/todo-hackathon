from typing import Optional
from pydantic import BaseModel, Field, UUID4
from enum import Enum


class TaskStatus(str, Enum):
    """Task status filter options"""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SortBy(str, Enum):
    """Sort field options"""
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"


class ListTasksParams(BaseModel):
    """Parameters for listing tasks"""
    user_id: UUID4 = Field(..., description="User ID whose tasks to list")
    status: TaskStatus = Field(TaskStatus.ALL, description="Filter by completion status")
    priority: Optional[Priority] = Field(None, description="Filter by priority")
    sort_by: SortBy = Field(SortBy.CREATED_AT, description="Sort field")


class ListTasksResponse(BaseModel):
    """Response from listing tasks"""
    tasks: list[dict]
    count: int
    error: Optional[str] = None


def list_tasks(params: ListTasksParams) -> dict:
    """
    List todo tasks for the user with optional filters for completion status and priority, and sorting options.

    This is the primary tool for retrieving task information. Use it whenever a user wants to see their tasks.
    Examples:
    - "What do I need to do?" → list_tasks(status="pending")
    - "Show my completed tasks" → list_tasks(status="completed")
    - "What's urgent?" → list_tasks(priority="high", status="pending")
    - "What's due soon?" → list_tasks(sort_by="due_date", status="pending")

    The AI should:
    - Default to showing pending tasks if user doesn't specify
    - Understand "done", "finished" as completed status
    - Infer priority filters from user language
    - Sort appropriately based on user intent

    Args:
        params: ListTasksParams object containing:
            - user_id: Unique identifier for the user (UUID)
            - status: Filter by status ('all', 'pending', 'completed') - defaults to 'all'
            - priority: Optional filter by priority ('low', 'medium', 'high')
            - sort_by: Sort field ('created_at', 'due_date', 'priority') - defaults to 'created_at'

    Returns:
        dict: Response with structure:
            {
                "tasks": [                 # Array of task objects
                    {
                        "id": "uuid-string",
                        "title": "Task title",
                        "description": "Details or null",
                        "completed": false,
                        "created_at": "2025-12-21T10:00:00Z",
                        "updated_at": "2025-12-21T10:00:00Z",
                        "due_date": "2025-12-22T12:00:00Z or null",
                        "priority": "medium"
                    }
                ],
                "count": 1,                # Number of tasks returned
                "error": null              # null on success, error message on failure
            }

    Example Response (Success):
        {
            "tasks": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "completed": false,
                    "created_at": "2025-12-21T10:00:00Z",
                    "updated_at": "2025-12-21T10:00:00Z",
                    "due_date": "2025-12-22T12:00:00Z",
                    "priority": "medium"
                }
            ],
            "count": 1,
            "error": null
        }

    Example Response (Empty):
        {
            "tasks": [],
            "count": 0,
            "error": null
        }

    Example Response (Error):
        {
            "tasks": [],
            "count": 0,
            "error": "Invalid user_id format"
        }
    """
    # TODO: Implementation will be added during /sp.implement phase
    # This is a placeholder that returns the expected structure
    pass
