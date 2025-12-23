from typing import Optional
from pydantic import BaseModel, Field, UUID4


class CompleteTaskParams(BaseModel):
    """Parameters for marking a task as complete"""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to mark complete")


class TaskResponse(BaseModel):
    """Response from task operations"""
    task_id: Optional[str] = None
    status: str
    title: Optional[str] = None
    error: Optional[str] = None


def complete_task(params: CompleteTaskParams) -> dict:
    """
    Mark a todo task as complete by its ID.

    Use this tool when a user indicates a task is done, finished, or complete.
    IMPORTANT: This tool requires a task_id (UUID). If the user doesn't provide a specific ID,
    you MUST use the list_tasks tool first to find the task they're referring to.

    Examples:
    - "Mark task 3 as done" → First list_tasks to get the 3rd task's UUID, then complete_task
    - "I finished the groceries task" → First list_tasks to find "groceries" task, then complete_task
    - "Complete task 550e8400-e29b-41d4-a716-446655440000" → complete_task with that UUID

    The AI should:
    - Extract task reference from user message
    - Call list_tasks if user refers to task by position ("the first one") or name
    - Map user reference to actual task UUID
    - Confirm completion with friendly message

    This tool is IDEMPOTENT: Completing an already-completed task returns success.

    Args:
        params: CompleteTaskParams object containing:
            - user_id: Unique identifier for the user who owns the task (UUID)
            - task_id: Unique identifier (UUID) of the task to mark complete

    Returns:
        dict: Response with structure:
            {
                "task_id": "uuid-string",  # ID of completed task
                "status": "completed",     # "completed" on success, "error" on failure
                "title": "Task title",     # Title of the completed task
                "error": null              # null on success, error message on failure
            }

    Example Response (Success):
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "completed",
            "title": "Buy groceries",
            "error": null
        }

    Example Response (Error - Task Not Found):
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "error",
            "title": null,
            "error": "Task not found"
        }
    """
    # TODO: Implementation will be added during /sp.implement phase
    # This is a placeholder that returns the expected structure
    pass
