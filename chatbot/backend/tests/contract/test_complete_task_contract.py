"""Contract tests for complete_task MCP tool.

Verifies that the complete_task tool conforms to its interface contract:
- Parameters match CompleteTaskParams schema
- Response matches expected structure
- Idempotency behavior
"""

import pytest
from pydantic import BaseModel, Field, UUID4, ValidationError
from uuid import uuid4


class CompleteTaskParams(BaseModel):
    """Parameter schema for complete_task tool as per contract."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to mark complete")


class TestCompleteTaskContract:
    """Contract tests for complete_task tool."""

    def test_complete_task_params_schema_validation(self):
        """Test that CompleteTaskParams schema validates correctly."""
        user_id = uuid4()
        task_id = uuid4()

        params = CompleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )

        assert params.user_id == user_id
        assert params.task_id == task_id

    def test_complete_task_params_validation_failures(self):
        """Test that CompleteTaskParams rejects invalid inputs."""
        # Missing user_id
        with pytest.raises(ValidationError):
            CompleteTaskParams(task_id=uuid4())

        # Missing task_id
        with pytest.raises(ValidationError):
            CompleteTaskParams(user_id=uuid4())

        # Invalid UUID format for user_id
        with pytest.raises(ValidationError):
            CompleteTaskParams(user_id="invalid", task_id=uuid4())

        # Invalid UUID format for task_id
        with pytest.raises(ValidationError):
            CompleteTaskParams(user_id=uuid4(), task_id="invalid")

    def test_complete_task_response_structure(self):
        """Test that complete_task tool returns correct response structure."""
        from src.mcp.tools.complete_task import complete_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # Create a task first
        user_id = uuid4()
        add_params = AddTaskParams(
            user_id=user_id,
            title="Task to complete"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Complete the task
        params = CompleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )
        response = complete_task(params)

        # Verify response has all required fields
        assert "task_id" in response
        assert "status" in response
        assert "title" in response
        assert "error" in response

        # Verify success response values
        assert response["status"] == "completed"
        assert response["task_id"] == str(task_id)
        assert response["title"] == "Task to complete"
        assert response["error"] is None

    def test_complete_task_error_response_for_nonexistent_task(self):
        """Test that complete_task returns error for non-existent task."""
        from src.mcp.tools.complete_task import complete_task

        params = CompleteTaskParams(
            user_id=uuid4(),
            task_id=uuid4()  # Non-existent task
        )

        response = complete_task(params)

        # Verify error response structure
        assert response["status"] == "error"
        assert response["error"] is not None
        assert "not found" in response["error"].lower()

    def test_complete_task_idempotency(self):
        """Test that completing an already-completed task returns success (idempotent)."""
        from src.mcp.tools.complete_task import complete_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # Create a task
        user_id = uuid4()
        add_params = AddTaskParams(
            user_id=user_id,
            title="Task for idempotency test"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Complete the task first time
        params = CompleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )
        response1 = complete_task(params)
        assert response1["status"] == "completed"

        # Complete the same task again (should still succeed)
        response2 = complete_task(params)
        assert response2["status"] == "completed"
        assert response2["error"] is None

    def test_complete_task_user_isolation(self):
        """Test that users cannot complete other users' tasks."""
        from src.mcp.tools.complete_task import complete_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # User 1 creates a task
        user1_id = uuid4()
        add_params = AddTaskParams(
            user_id=user1_id,
            title="User 1's task"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # User 2 tries to complete user 1's task
        user2_id = uuid4()
        params = CompleteTaskParams(
            user_id=user2_id,
            task_id=task_id
        )
        response = complete_task(params)

        # Should return error (not found due to user isolation)
        assert response["status"] == "error"
        assert response["error"] is not None
