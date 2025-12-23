from typing import Optional
from pydantic import BaseModel, Field, UUID4


class DeleteTaskParams(BaseModel):
    """Parameters for deleting a task"""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to delete")


class TaskResponse(BaseModel):
    """Response from task operations"""
    task_id: Optional[str] = None
    status: str
    title: Optional[str] = None
    error: Optional[str] = None


def delete_task(params: DeleteTaskParams) -> dict:
    """
    Permanently delete a todo task by its ID.

    Use this tool when a user wants to remove, cancel, or delete a task. This action is IRREVERSIBLE.
    IMPORTANT: This tool requires a task_id (UUID). If the user doesn't provide a specific ID,
    you MUST use the list_tasks tool first to find the task, confirm with the user, then delete.

    Examples:
    - "Delete task 2" → First list_tasks to get the 2nd task's UUID, then delete_task
    - "Remove the meeting task" → First list_tasks to find "meeting" task, confirm, then delete_task
    - "Cancel the doctor appointment" → First list_tasks to find task, confirm, then delete_task

    The AI should:
    - Extract task reference from user message
    - Call list_tasks if user refers to task by position or name
    - CONFIRM with user before deleting (important tasks)
    - Map user reference to actual task UUID
    - Provide clear confirmation after deletion

    This tool is NOT idempotent: Deleting a non-existent task returns an error.

    Args:
        params: DeleteTaskParams object containing:
            - user_id: Unique identifier for the user who owns the task (UUID)
            - task_id: Unique identifier (UUID) of the task to delete permanently

    Returns:
        dict: Response with structure:
            {
                "task_id": "uuid-string",  # ID of deleted task
                "status": "deleted",       # "deleted" on success, "error" on failure
                "title": "Task title",     # Title of the deleted task (for confirmation)
                "error": null              # null on success, error message on failure
            }

    Example Response (Success):
        {
            "task_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "deleted",
            "title": "Old meeting notes",
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
