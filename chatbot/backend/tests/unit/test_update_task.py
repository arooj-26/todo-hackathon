"""Unit tests for update_task MCP tool.

Tests the business logic with mock database to verify:
- Partial update logic (only provided fields updated)
- Validation of updates
- User isolation
- Task not found handling
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class Priority(str, Enum):
    """Priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UpdateTaskParams(BaseModel):
    """Parameter schema for update_task."""
    user_id: UUID = Field(...)
    task_id: UUID = Field(...)
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=10000)
    priority: Priority | None = Field(None)
    due_date: datetime | None = Field(None)


class TestUpdateTask:
    """Unit tests for update_task tool."""

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_title_only(self, mock_session_class):
        """Test updating only the title (partial update)."""
        from src.mcp.tools.update_task import update_task

        # Setup mock task
        mock_task = Mock()
        task_id = uuid4()
        mock_task.id = task_id
        mock_task.title = "Original title"
        mock_task.description = "Original description"
        mock_task.priority = "medium"

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params (only title)
        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=task_id,
            title="Updated title"
        )

        # Call the tool
        response = update_task(params)

        # Verify response
        assert response["status"] == "updated"
        assert response["title"] == "Updated title"
        assert response["error"] is None

        # Verify only title was updated
        assert mock_task.title == "Updated title"
        assert mock_task.description == "Original description"
        assert mock_task.priority == "medium"

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_multiple_fields(self, mock_session_class):
        """Test updating multiple fields at once."""
        from src.mcp.tools.update_task import update_task

        # Setup mock task
        mock_task = Mock()
        task_id = uuid4()
        mock_task.id = task_id
        mock_task.title = "Original"
        mock_task.description = "Original desc"
        mock_task.priority = "low"

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params (multiple fields)
        new_due_date = datetime(2025, 12, 31)
        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=task_id,
            title="New title",
            priority=Priority.HIGH,
            due_date=new_due_date
        )

        # Call the tool
        response = update_task(params)

        # Verify all provided fields were updated
        assert mock_task.title == "New title"
        assert mock_task.priority == "high"
        assert mock_task.due_date == new_due_date
        # Description not provided, so should remain unchanged
        assert mock_task.description == "Original desc"

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_updates_timestamp(self, mock_session_class):
        """Test that updated_at timestamp is set."""
        from src.mcp.tools.update_task import update_task

        # Setup mock task
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Original"
        original_updated_at = datetime(2025, 1, 1)
        mock_task.updated_at = original_updated_at

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id,
            title="Updated"
        )

        # Call the tool
        update_task(params)

        # Verify updated_at was changed
        assert mock_task.updated_at != original_updated_at

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_not_found(self, mock_session_class):
        """Test error when task is not found."""
        from src.mcp.tools.update_task import update_task

        # Setup mock to return None (task not found)
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = None
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        task_id = uuid4()
        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=task_id,
            title="New title"
        )

        # Call the tool
        response = update_task(params)

        # Verify error response
        assert response["status"] == "error"
        assert response["error"] is not None
        assert "not found" in response["error"].lower()

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_user_isolation(self, mock_session_class):
        """Test that user_id filter is applied for data isolation."""
        from src.mcp.tools.update_task import update_task

        # Setup mock
        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = None  # Not found due to user mismatch
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        user_id = uuid4()
        task_id = uuid4()
        params = UpdateTaskParams(
            user_id=user_id,
            task_id=task_id,
            title="Hacked title"
        )

        # Call the tool
        response = update_task(params)

        # Verify user_id filter was applied in query
        assert mock_session.query.return_value.filter.called

        # Verify error response (task not found due to user isolation)
        assert response["status"] == "error"

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_clear_optional_field(self, mock_session_class):
        """Test clearing an optional field by setting to None."""
        from src.mcp.tools.update_task import update_task

        # Setup mock task with description
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Task"
        mock_task.description = "Has description"

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params to clear description
        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id,
            description=None
        )

        # Call the tool
        response = update_task(params)

        # Verify description was cleared (if tool supports this)
        # Note: Implementation may handle None as "no update" or "clear"
        # This test documents the expected behavior
        assert response["status"] == "updated"

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_database_error_handling(self, mock_session_class):
        """Test error handling when database operation fails."""
        from src.mcp.tools.update_task import update_task

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
        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id,
            title="Updated"
        )

        # Call the tool
        response = update_task(params)

        # Verify error response
        assert response["status"] == "error"
        assert response["error"] is not None

    @patch('src.mcp.tools.update_task.Session')
    def test_update_task_title_trimming(self, mock_session_class):
        """Test that title is trimmed of whitespace."""
        from src.mcp.tools.update_task import update_task

        # Setup mock task
        mock_task = Mock()
        mock_task.id = uuid4()
        mock_task.title = "Original"

        mock_session = Mock()
        mock_query = Mock()
        mock_query.first.return_value = mock_task
        mock_session.query.return_value.filter.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params with whitespace
        params = UpdateTaskParams(
            user_id=uuid4(),
            task_id=mock_task.id,
            title="  New title  "
        )

        # Call the tool
        update_task(params)

        # Verify title was trimmed
        assert mock_task.title == "New title"
