"""Contract tests for update_task MCP tool.

Verifies that the update_task tool conforms to its interface contract:
- Parameters match UpdateTaskParams schema
- Response matches expected structure
- Partial update behavior
"""

import pytest
from pydantic import BaseModel, Field, UUID4, ValidationError
from datetime import datetime
from enum import Enum
from uuid import uuid4


class Priority(str, Enum):
    """Priority enum as per contract."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UpdateTaskParams(BaseModel):
    """Parameter schema for update_task tool as per contract."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to update")
    title: str | None = Field(None, min_length=1, max_length=500, description="New task title")
    description: str | None = Field(None, max_length=10000, description="New task description")
    priority: Priority | None = Field(None, description="New priority")
    due_date: datetime | None = Field(None, description="New due date")


class TestUpdateTaskContract:
    """Contract tests for update_task tool."""

    def test_update_task_params_schema_validation(self):
        """Test that UpdateTaskParams schema validates correctly."""
        user_id = uuid4()
        task_id = uuid4()

        # Minimal params (only required fields)
        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id
        )
        assert params.user_id == user_id
        assert params.task_id == task_id
        assert params.title is None
        assert params.description is None
        assert params.priority is None
        assert params.due_date is None

        # Full params (all optional fields provided)
        due_date = datetime.now()
        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="Updated title",
            description="Updated description",
            priority=Priority.HIGH,
            due_date=due_date
        )
        assert params.title == "Updated title"
        assert params.description == "Updated description"
        assert params.priority == Priority.HIGH
        assert params.due_date == due_date

    def test_update_task_params_validation_failures(self):
        """Test that UpdateTaskParams rejects invalid inputs."""
        user_id = uuid4()
        task_id = uuid4()

        # Missing required field (user_id)
        with pytest.raises(ValidationError):
            UpdateTaskParams(task_id=task_id)

        # Missing required field (task_id)
        with pytest.raises(ValidationError):
            UpdateTaskParams(user_id=user_id)

        # Empty title (if provided, must be non-empty)
        with pytest.raises(ValidationError):
            UpdateTaskParams(user_id=user_id, task_id=task_id, title="")

        # Title too long
        with pytest.raises(ValidationError):
            UpdateTaskParams(user_id=user_id, task_id=task_id, title="a" * 501)

        # Invalid priority
        with pytest.raises(ValidationError):
            UpdateTaskParams(user_id=user_id, task_id=task_id, priority="invalid")

    def test_update_task_response_structure(self):
        """Test that update_task tool returns correct response structure."""
        from src.mcp.tools.update_task import update_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # Create a task first
        user_id = uuid4()
        add_params = AddTaskParams(
            user_id=user_id,
            title="Original title"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Update the task
        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="Updated title"
        )
        response = update_task(params)

        # Verify response has all required fields
        assert "task_id" in response
        assert "status" in response
        assert "title" in response
        assert "error" in response

        # Verify success response values
        assert response["status"] == "updated"
        assert response["task_id"] == str(task_id)
        assert response["title"] == "Updated title"
        assert response["error"] is None

    def test_update_task_partial_update(self):
        """Test that update_task supports partial updates (only provided fields updated)."""
        from src.mcp.tools.update_task import update_task
        from src.mcp.tools.add_task import add_task, AddTaskParams
        from src.mcp.tools.list_tasks import list_tasks, ListTasksParams

        # Create a task with all fields
        user_id = uuid4()
        original_due_date = datetime(2025, 12, 25, 10, 0, 0)
        add_params = AddTaskParams(
            user_id=user_id,
            title="Original title",
            description="Original description",
            priority=Priority.LOW,
            due_date=original_due_date
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Update only the title
        update_params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="Updated title"
            # description, priority, due_date not provided
        )
        update_task(update_params)

        # Verify only title was updated
        list_params = ListTasksParams(user_id=user_id)
        list_response = list_tasks(list_params)
        updated_task = list_response["tasks"][0]

        assert updated_task["title"] == "Updated title"
        assert updated_task["description"] == "Original description"
        assert updated_task["priority"] == "low"

    def test_update_task_error_for_nonexistent_task(self):
        """Test that update_task returns error for non-existent task."""
        from src.mcp.tools.update_task import update_task

        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=uuid4(),  # Non-existent task
            title="New title"
        )

        response = update_task(params)

        # Verify error response structure
        assert response["status"] == "error"
        assert response["error"] is not None
        assert "not found" in response["error"].lower()

    def test_update_task_user_isolation(self):
        """Test that users cannot update other users' tasks."""
        from src.mcp.tools.update_task import update_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # User 1 creates a task
        user1_id = uuid4()
        add_params = AddTaskParams(
            user_id=user1_id,
            title="User 1's task"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # User 2 tries to update user 1's task
        user2_id = uuid4()
        params = UpdateTaskParams(
            user_id=user2_id,
            task_id=task_id,
            title="Hacked title"
        )
        response = update_task(params)

        # Should return error (not found due to user isolation)
        assert response["status"] == "error"
        assert response["error"] is not None

    def test_update_task_clear_optional_fields(self):
        """Test that optional fields can be cleared by setting to None."""
        from src.mcp.tools.update_task import update_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # Create a task with description and due_date
        user_id = uuid4()
        add_params = AddTaskParams(
            user_id=user_id,
            title="Task with details",
            description="Initial description",
            due_date=datetime.now()
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Update to clear description (set to None)
        # Note: The contract says "null to clear", which we test here
        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            description=None  # Explicitly clear
        )
        response = update_task(params)

        # Verify the update succeeded
        assert response["status"] == "updated"
