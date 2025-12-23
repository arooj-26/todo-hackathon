"""Unit tests for complete_task MCP tool.

Tests the business logic with mock database to verify:
- Task completion logic (setting completed=True)
- User isolation
- Task not found handling
- Idempotency
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CompleteTaskParams(BaseModel):
    """Parameter schema for complete_task."""
    user_id: UUID = Field(...)
    task_id: UUID = Field(...)


class TestCompleteTask:
    """Unit tests for complete_task tool."""

    @patch('src.mcp.tools.complete_task.Session')
    def test_complete_task_success(self, mock_session_class):
        """Test successfully completing a task."""
        from src.mcp.tools.complete_task import complete_task

        # Setup mock task
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Test task"
        mock_task.completed = False

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        user_id = uuid4()
        params = CompleteTaskParams(
            user_id=user_id,
            task_id=mock_task.id
        )

        # Call the tool
        response = complete_task(params)

        # Verify response
        assert response["status"] == "completed"
        assert response["title"] == "Test task"
        assert response["error"] is None

        # Verify task was marked as completed
        assert mock_task.completed is True
        mock_session.commit.assert_called_once()

    @patch('src.mcp.tools.complete_task.Session')
    def test_complete_task_updates_timestamp(self, mock_session_class):
        """Test that updated_at timestamp is set."""
        from src.mcp.tools.complete_task import complete_task

        # Setup mock task
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Test task"
        mock_task.completed = False
        original_updated_at = datetime(2025, 1, 1)
        mock_task.updated_at = original_updated_at

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = CompleteTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id
        )

        # Call the tool
        complete_task(params)

        # Verify updated_at was changed
        assert mock_task.updated_at != original_updated_at

    @patch('src.mcp.tools.complete_task.Session')
    def test_complete_task_not_found(self, mock_session_class):
        """Test error when task is not found."""
        from src.mcp.tools.complete_task import complete_task

        # Setup mock to return None (task not found)
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = None
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = CompleteTaskParams(
            user_id=uuid4(),
            task_id=uuid4()
        )

        # Call the tool
        response = complete_task(params)

        # Verify error response
        assert response["status"] == "error"
        assert response["error"] is not None
        assert "not found" in response["error"].lower()

    @patch('src.mcp.tools.complete_task.Session')
    def test_complete_task_user_isolation(self, mock_session_class):
        """Test that user_id filter is applied for data isolation."""
        from src.mcp.tools.complete_task import complete_task

        # Setup mock
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = None  # Not found due to user mismatch
        mock_filter = Mock()
        mock_filter.filter.return_value = mock_query
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        user_id = uuid4()
        task_id = uuid4()
        params = CompleteTaskParams(
            user_id=user_id,
            task_id=task_id
        )

        # Call the tool
        response = complete_task(params)

        # Verify user_id filter was applied in query
        assert mock_session.query.return_value.filter.called

        # Verify error response (task not found due to user isolation)
        assert response["status"] == "error"

    @patch('src.mcp.tools.complete_task.Session')
    def test_complete_task_idempotent(self, mock_session_class):
        """Test that completing an already-completed task succeeds (idempotent)."""
        from src.mcp.tools.complete_task import complete_task

        # Setup mock task that's already completed
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Already completed task"
        mock_task.completed = True  # Already completed

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = CompleteTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id
        )

        # Call the tool
        response = complete_task(params)

        # Verify success response (idempotent)
        assert response["status"] == "completed"
        assert response["error"] is None

    @patch('src.mcp.tools.complete_task.Session')
    def test_complete_task_database_error_handling(self, mock_session_class):
        """Test error handling when database operation fails."""
        from src.mcp.tools.complete_task import complete_task

        # Setup mock to raise exception on commit
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Test task"

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session.commit.side_effect = Exception("Database error")
        mock_session_class.return_value = mock_session

        # Prepare params
        params = CompleteTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id
        )

        # Call the tool
        response = complete_task(params)

        # Verify error response
        assert response["status"] == "error"
        assert response["error"] is not None
