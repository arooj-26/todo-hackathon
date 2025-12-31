"""Task-related Pydantic schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for task creation request."""

    description: str = Field(..., min_length=1, max_length=1000, description="Task description")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$", description="Task priority level")
    due_date: Optional[datetime] = Field(None, description="Optional due date for the task")
    recurrence: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$", description="Optional recurrence pattern")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "description": "Buy groceries",
                    "priority": "high",
                    "due_date": "2025-01-01T12:00:00Z",
                    "recurrence": "weekly"
                }
            ]
        }
    }


class TaskUpdate(BaseModel):
    """Schema for task update request."""

    description: str | None = Field(None, min_length=1, max_length=1000, description="Updated task description")
    completed: bool | None = Field(None, description="Updated completion status")
    priority: str | None = Field(None, pattern="^(low|medium|high)$", description="Updated task priority level")
    due_date: Optional[datetime] | None = Field(None, description="Updated due date for the task")
    recurrence: Optional[str] | None = Field(None, pattern="^(daily|weekly|monthly)$", description="Updated recurrence pattern")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "description": "Buy groceries and cook dinner",
                    "completed": True,
                    "priority": "high",
                    "due_date": "2025-01-01T12:00:00Z",
                    "recurrence": "weekly"
                }
            ]
        }
    }


class TaskResponse(BaseModel):
    """Schema for task data in API responses."""

    id: int = Field(..., description="Task's unique ID")
    user_id: int = Field(..., description="ID of user who owns this task")
    description: str = Field(..., description="Task description")
    completed: bool = Field(..., description="Whether task is completed")
    priority: str = Field(..., description="Task priority level (low, medium, high)")
    due_date: Optional[datetime] = Field(None, description="Optional due date for the task")
    recurrence: Optional[str] = Field(None, description="Recurrence pattern (daily, weekly, monthly, or null)")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "description": "Buy groceries",
                    "completed": False,
                    "priority": "medium",
                    "due_date": "2025-01-01T12:00:00Z",
                    "recurrence": "weekly",
                    "created_at": "2025-01-01T12:00:00Z",
                    "updated_at": "2025-01-01T12:00:00Z"
                }
            ]
        }
    }
