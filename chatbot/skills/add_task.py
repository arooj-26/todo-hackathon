from typing import Optional
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AddTaskParams(BaseModel):
    """Parameters for creating a new task"""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: Optional[str] = Field(None, max_length=10000, description="Optional task description")
    due_date: Optional[datetime] = Field(None, description="Optional due date in ISO 8601 format")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority (default: medium)")


class TaskResponse(BaseModel):
    """Response from task operations"""
    task_id: Optional[str] = None
    status: str
    title: Optional[str] = None
    error: Optional[str] = None


def add_task(params: AddTaskParams) -> dict:
    """
    Create a new todo task for the user with a title and optional description, due date, and priority.

    This tool should be triggered when a user expresses intent to add, create, or remember something.
    Examples:
    - "I need to buy groceries" → add_task(title="Buy groceries")
    - "Remind me to pay bills by Friday" → add_task(title="Pay bills", due_date="2025-12-22T00:00:00Z")
    - "Add a high-priority task to call the client" → add_task(title="Call the client", priority="high")

    The AI should:
    - Extract task title from natural language
    - Parse dates intelligently (tomorrow, next Friday, etc.)
    - Infer priority from keywords (urgent, important, ASAP → high priority)

    Args:
        params: AddTaskParams object containing:
            - user_id: Unique identifier for the user (UUID)
            - title: Concise summary of what needs to be done (1-500 chars)
            - description: Optional detailed description (max 10,000 chars)
            - due_date: Optional due date in ISO 8601 format (e.g., "2025-12-22T15:30:00Z")
            - priority: Task priority ('low', 'medium', 'high') - defaults to 'medium'

    Returns:
        dict: Response with structure:
            {
                "task_id": "uuid-string",  # Unique ID of created task
                "status": "created",       # Always "created" for success
                "title": "Task title",     # Echo of title for confirmation
                "error": null              # null on success, error message on failure
            }

    Example Response (Success):
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "created",
            "title": "Buy groceries",
            "error": null
        }

    Example Response (Error):
        {
            "task_id": null,
            "status": "error",
            "title": null,
            "error": "Title cannot be empty"
        }
    """
    # TODO: Implementation will be added during /sp.implement phase
    # This is a placeholder that returns the expected structure
    pass
