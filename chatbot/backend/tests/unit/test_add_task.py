"""Unit tests for add_task MCP tool.

Tests the business logic with mock database to verify:
- Task creation with valid inputs
- Validation error handling
- Default priority behavior
- Error cases
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class Priority(str, Enum):
    """Priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AddTaskParams(BaseModel):
    """Parameter schema for add_task."""
    user_id: UUID = Field(...)
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=10000)
    due_date: datetime | None = Field(None)
    priority: Priority = Field(Priority.MEDIUM)


class TestAddTask:
    """Unit tests for add_task tool."""

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_with_required_fields_only(self, mock_session_class):
        """Test creating a task with only required fields."""
        from src.mcp.tools.add_task import add_task

        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Prepare params
        user_id = uuid4()
        params = AddTaskParams(
            user_id=user_id,
            title="Buy groceries"
        )

        # Call the tool
        response = add_task(params)

        # Verify response structure
        assert response["status"] == "created"
        assert response["title"] == "Buy groceries"
        assert response["error"] is None
        assert response["task_id"] is not None

        # Verify database interaction
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_with_all_fields(self, mock_session_class):
        """Test creating a task with all optional fields."""
        from src.mcp.tools.add_task import add_task

        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Prepare params with all fields
        user_id = uuid4()
        due_date = datetime(2025, 12, 31, 23, 59, 59)
        params = AddTaskParams(
            user_id=user_id,
            title="Complete project",
            description="Finish all tasks by end of year",
            due_date=due_date,
            priority=Priority.HIGH
        )

        # Call the tool
        response = add_task(params)

        # Verify response
        assert response["status"] == "created"
        assert response["title"] == "Complete project"
        assert response["error"] is None

        # Verify task was added to session
        mock_session.add.assert_called_once()
        task = mock_session.add.call_args[0][0]
        assert task.title == "Complete project"
        assert task.description == "Finish all tasks by end of year"
        assert task.priority == "high"

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_default_priority(self, mock_session_class):
        """Test that priority defaults to 'medium' when not provided."""
        from src.mcp.tools.add_task import add_task

        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Prepare params without priority
        params = AddTaskParams(
            user_id=uuid4(),
            title="Test task"
        )

        # Call the tool
        response = add_task(params)

        # Verify default priority was used
        task = mock_session.add.call_args[0][0]
        assert task.priority == "medium"

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_database_error_handling(self, mock_session_class):
        """Test error handling when database operation fails."""
        from src.mcp.tools.add_task import add_task

        # Setup mock to raise exception on commit
        mock_session = Mock()
        mock_session.commit.side_effect = Exception("Database connection failed")
        mock_session_class.return_value = mock_session

        # Prepare params
        params = AddTaskParams(
            user_id=uuid4(),
            title="Test task"
        )

        # Call the tool
        response = add_task(params)

        # Verify error response
        assert response["status"] == "error"
        assert response["error"] is not None
        assert "database" in response["error"].lower() or "failed" in response["error"].lower()
        assert response["task_id"] is None

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_generates_uuid(self, mock_session_class):
        """Test that task_id is automatically generated as UUID."""
        from src.mcp.tools.add_task import add_task

        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Prepare params
        params = AddTaskParams(
            user_id=uuid4(),
            title="Test task"
        )

        # Call the tool
        response = add_task(params)

        # Verify UUID was generated
        task_id = response["task_id"]
        assert task_id is not None
        # Verify it's a valid UUID string
        UUID(task_id)  # Will raise if not valid UUID

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_sets_timestamps(self, mock_session_class):
        """Test that created_at and updated_at are set."""
        from src.mcp.tools.add_task import add_task

        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Prepare params
        params = AddTaskParams(
            user_id=uuid4(),
            title="Test task"
        )

        # Call the tool
        add_task(params)

        # Verify timestamps were set
        task = mock_session.add.call_args[0][0]
        assert task.created_at is not None
        assert task.updated_at is not None

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_title_trimming(self, mock_session_class):
        """Test that title is trimmed of whitespace."""
        from src.mcp.tools.add_task import add_task

        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Prepare params with whitespace
        params = AddTaskParams(
            user_id=uuid4(),
            title="  Buy groceries  "
        )

        # Call the tool
        response = add_task(params)

        # Verify title was trimmed
        task = mock_session.add.call_args[0][0]
        assert task.title == "Buy groceries"

    @patch('src.mcp.tools.add_task.Session')
    def test_add_task_user_id_stored_correctly(self, mock_session_class):
        """Test that user_id is stored correctly for data isolation."""
        from src.mcp.tools.add_task import add_task

        # Setup mock
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Prepare params
        user_id = uuid4()
        params = AddTaskParams(
            user_id=user_id,
            title="Test task"
        )

        # Call the tool
        add_task(params)

        # Verify user_id was stored
        task = mock_session.add.call_args[0][0]
        assert str(task.user_id) == str(user_id)
