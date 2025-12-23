"""Unit tests for delete_task MCP tool.

Tests the business logic with mock database to verify:
- Task deletion logic
- User isolation
- Task not found handling
- Title retrieval for confirmation
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from pydantic import BaseModel, Field


class DeleteTaskParams(BaseModel):
    """Parameter schema for delete_task."""
    user_id: UUID = Field(...)
    task_id: UUID = Field(...)


class TestDeleteTask:
    """Unit tests for delete_task tool."""

    @patch('src.mcp.tools.delete_task.Session')
    def test_delete_task_success(self, mock_session_class):
        """Test successfully deleting a task."""
        from src.mcp.tools.delete_task import delete_task

        # Setup mock task
        mock_task = Mock()
        task_id = uuid4()
        mock_task.id = task_id
        mock_task.title = "Task to delete"

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = DeleteTaskParams(
            user_id=uuid4(),
            task_id=task_id
        )

        # Call the tool
        response = delete_task(params)

        # Verify response
        assert response["status"] == "deleted"
        assert response["title"] == "Task to delete"
        assert response["task_id"] == str(task_id)
        assert response["error"] is None

        # Verify task was deleted
        mock_session.delete.assert_called_once_with(mock_task)
        mock_session.commit.assert_called_once()

    @patch('src.mcp.tools.delete_task.Session')
    def test_delete_task_not_found(self, mock_session_class):
        """Test error when task is not found."""
        from src.mcp.tools.delete_task import delete_task

        # Setup mock to return None (task not found)
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = None
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        task_id = uuid4()
        params = DeleteTaskParams(
            user_id=uuid4(),
            task_id=task_id
        )

        # Call the tool
        response = delete_task(params)

        # Verify error response
        assert response["status"] == "error"
        assert response["error"] is not None
        assert "not found" in response["error"].lower()
        assert response["task_id"] == str(task_id)

    @patch('src.mcp.tools.delete_task.Session')
    def test_delete_task_user_isolation(self, mock_session_class):
        """Test that user_id filter is applied for data isolation."""
        from src.mcp.tools.delete_task import delete_task

        # Setup mock
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = None  # Not found due to user mismatch
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        user_id = uuid4()
        task_id = uuid4()
        params = DeleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )

        # Call the tool
        response = delete_task(params)

        # Verify user_id filter was applied in query
        assert mock_session.query.return_value.filter.called

        # Verify error response (task not found due to user isolation)
        assert response["status"] == "error"

    @patch('src.mcp.tools.delete_task.Session')
    def test_delete_task_returns_title_for_confirmation(self, mock_session_class):
        """Test that task title is returned for user confirmation."""
        from src.mcp.tools.delete_task import delete_task

        # Setup mock task with specific title
        mock_task = Mock()
        mock_task.id = uuid4()
        task_title = "Important meeting notes"
        mock_task.title = task_title

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = DeleteTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id
        )

        # Call the tool
        response = delete_task(params)

        # Verify title is returned
        assert response["title"] == task_title

    @patch('src.mcp.tools.delete_task.Session')
    def test_delete_task_database_error_handling(self, mock_session_class):
        """Test error handling when database operation fails."""
        from src.mcp.tools.delete_task import delete_task

        # Setup mock to raise exception on delete
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Test task"

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session.delete.side_effect = Exception("Database error")
        mock_session_class.return_value = mock_session

        # Prepare params
        params = DeleteTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id
        )

        # Call the tool
        response = delete_task(params)

        # Verify error response
        assert response["status"] == "error"
        assert response["error"] is not None

    @patch('src.mcp.tools.delete_task.Session')
    def test_delete_task_not_idempotent(self, mock_session_class):
        """Test that deleting non-existent task returns error (not idempotent)."""
        from src.mcp.tools.delete_task import delete_task

        # Setup mock to return None (already deleted)
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = None
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = DeleteTaskParams(
            user_id=uuid4(),
            task_id=uuid4()
        )

        # Call the tool
        response = delete_task(params)

        # Verify error (not idempotent)
        assert response["status"] == "error"
        assert response["error"] is not None
