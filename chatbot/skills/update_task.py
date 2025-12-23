from typing import Optional
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UpdateTaskParams(BaseModel):
    """Parameters for updating a task"""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to update")
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="New task title")
    description: Optional[str] = Field(None, max_length=10000, description="New task description")
    priority: Optional[Priority] = Field(None, description="New priority")
    due_date: Optional[datetime] = Field(None, description="New due date")


class TaskResponse(BaseModel):
    """Response from task operations"""
    task_id: Optional[str] = None
    status: str
    title: Optional[str] = None
    error: Optional[str] = None


def update_task(params: UpdateTaskParams) -> dict:
    """
    Update a todo task's title, description, priority, or due date by its ID.

    A versatile tool to modify any attribute of an existing task. The user can update one or
    multiple attributes at once. This is a PARTIAL UPDATE - only provided fields are changed.

    IMPORTANT: This tool requires a task_id (UUID). If the user doesn't provide a specific ID,
    you MUST use the list_tasks tool first to identify the correct task.

    Examples:
    - "Change task 1 to 'Call mom tonight'" → First get task 1's UUID, then update_task(title="Call mom tonight")
    - "Make the groceries task high priority" → First find task, then update_task(priority="high")
    - "Move the report deadline to next Friday" → First find task, then update_task(due_date="2025-12-28T00:00:00Z")
    - "Update task description to include budget details" → update_task(description="Include budget details")

    The AI should:
    - Extract task reference and what needs updating
    - Call list_tasks if needed to find task UUID
    - Parse new values from natural language
    - Only update specified fields (partial update)
    - Provide clear confirmation with what changed

    Args:
        params: UpdateTaskParams object containing:
            - user_id: Unique identifier for the user who owns the task (UUID)
            - task_id: Unique identifier (UUID) of the task to update
            - title: Optional new title (1-500 chars)
            - description: Optional new description (max 10,000 chars)
            - priority: Optional new priority ('low', 'medium', 'high')
            - due_date: Optional new due date in ISO 8601 format

    Returns:
        dict: Response with structure:
            {
                "task_id": "uuid-string",  # ID of updated task
                "status": "updated",       # "updated" on success, "error" on failure
                "title": "New title",      # New title of the task
                "error": null              # null on success, error message on failure
            }

    Example Response (Success):
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "updated",
            "title": "Buy groceries and fruits",
            "error": null
        }

    Example Response (Error - Task Not Found):
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "error",
            "title": null,
            "error": "Task not found"
        }

    Example Response (Error - Validation):
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "error",
            "title": null,
            "error": "Title cannot be empty"
        }
    """
    # TODO: Implementation will be added during /sp.implement phase
    # This is a placeholder that returns the expected structure
    pass
