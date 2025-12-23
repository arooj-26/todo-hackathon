"""Contract tests for delete_task MCP tool.

Verifies that the delete_task tool conforms to its interface contract:
- Parameters match DeleteTaskParams schema
- Response matches expected structure
- Error on non-existent task
"""

import pytest
from pydantic import BaseModel, Field, UUID4, ValidationError
from uuid import uuid4


class DeleteTaskParams(BaseModel):
    """Parameter schema for delete_task tool as per contract."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to delete")


class TestDeleteTaskContract:
    """Contract tests for delete_task tool."""

    def test_delete_task_params_schema_validation(self):
        """Test that DeleteTaskParams schema validates correctly."""
        user_id = uuid4()
        task_id = uuid4()

        params = DeleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )

        assert params.user_id == user_id
        assert params.task_id == task_id

    def test_delete_task_params_validation_failures(self):
        """Test that DeleteTaskParams rejects invalid inputs."""
        # Missing user_id
        with pytest.raises(ValidationError):
            DeleteTaskParams(task_id=uuid4())

        # Missing task_id
        with pytest.raises(ValidationError):
            DeleteTaskParams(user_id=uuid4())

        # Invalid UUID format for user_id
        with pytest.raises(ValidationError):
            DeleteTaskParams(user_id="invalid", task_id=uuid4())

        # Invalid UUID format for task_id
        with pytest.raises(ValidationError):
            DeleteTaskParams(user_id=uuid4(), task_id="invalid")

    def test_delete_task_response_structure(self):
        """Test that delete_task tool returns correct response structure."""
        from src.mcp.tools.delete_task import delete_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # Create a task first
        user_id = uuid4()
        add_params = AddTaskParams(
            user_id=user_id,
            title="Task to delete"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Delete the task
        params = DeleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )
        response = delete_task(params)

        # Verify response has all required fields
        assert "task_id" in response
        assert "status" in response
        assert "title" in response
        assert "error" in response

        # Verify success response values
        assert response["status"] == "deleted"
        assert response["task_id"] == str(task_id)
        assert response["title"] == "Task to delete"
        assert response["error"] is None

    def test_delete_task_error_response_for_nonexistent_task(self):
        """Test that delete_task returns error for non-existent task (NOT idempotent)."""
        from src.mcp.tools.delete_task import delete_task

        params = DeleteTaskParams(
            user_id=uuid4(),
            task_id=uuid4()  # Non-existent task
        )

        response = delete_task(params)

        # Verify error response structure
        assert response["status"] == "error"
        assert response["error"] is not None
        assert "not found" in response["error"].lower()

    def test_delete_task_not_idempotent(self):
        """Test that deleting an already-deleted task returns error (not idempotent)."""
        from src.mcp.tools.delete_task import delete_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # Create a task
        user_id = uuid4()
        add_params = AddTaskParams(
            user_id=user_id,
            title="Task for deletion test"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Delete the task first time
        params = DeleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )
        response1 = delete_task(params)
        assert response1["status"] == "deleted"

        # Try to delete the same task again (should fail)
        response2 = delete_task(params)
        assert response2["status"] == "error"
        assert response2["error"] is not None

    def test_delete_task_user_isolation(self):
        """Test that users cannot delete other users' tasks."""
        from src.mcp.tools.delete_task import delete_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # User 1 creates a task
        user1_id = uuid4()
        add_params = AddTaskParams(
            user_id=user1_id,
            title="User 1's task"
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # User 2 tries to delete user 1's task
        user2_id = uuid4()
        params = DeleteTaskParams(
            user_id=user2_id,
            task_id=task_id
        )
        response = delete_task(params)

        # Should return error (not found due to user isolation)
        assert response["status"] == "error"
        assert response["error"] is not None

    def test_delete_task_returns_title_for_confirmation(self):
        """Test that delete_task returns the task title for user confirmation."""
        from src.mcp.tools.delete_task import delete_task
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # Create a task with a specific title
        user_id = uuid4()
        task_title = "Important meeting notes"
        add_params = AddTaskParams(
            user_id=user_id,
            title=task_title
        )
        add_response = add_task(add_params)
        task_id = add_response["task_id"]

        # Delete the task
        params = DeleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )
        response = delete_task(params)

        # Verify the title is returned for confirmation
        assert response["title"] == task_title
