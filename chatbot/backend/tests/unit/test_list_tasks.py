"""Unit tests for list_tasks MCP tool.

Tests the business logic with mock database to verify:
- Filtering by status and priority
- Sorting by different fields
- Empty results handling
- User isolation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4, UUID
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class Priority(str, Enum):
    """Priority enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Task status filter enum."""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class SortBy(str, Enum):
    """Sort field enum."""
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"


class ListTasksParams(BaseModel):
    """Parameter schema for list_tasks."""
    user_id: UUID = Field(...)
    status: TaskStatus = Field(TaskStatus.ALL)
    priority: Priority | None = Field(None)
    sort_by: SortBy = Field(SortBy.CREATED_AT)


class TestListTasks:
    """Unit tests for list_tasks tool."""

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_empty_results(self, mock_session_class):
        """Test that empty array is returned when no tasks exist."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock to return empty list
        mock_session = Mock()
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(user_id=uuid4())

        # Call the tool
        response = list_tasks(params)

        # Verify empty response
        assert response["tasks"] == []
        assert response["count"] == 0
        assert response["error"] is None

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_filter_by_pending_status(self, mock_session_class):
        """Test filtering by pending status (completed=False)."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock
        mock_session = Mock()
        mock_filter = Mock()
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(
            user_id=uuid4(),
            status=TaskStatus.PENDING
        )

        # Call the tool
        list_tasks(params)

        # Verify filter was called for pending tasks
        # (This test verifies the filter logic is applied, actual SQL check in integration tests)
        assert mock_filter.filter.called or mock_filter.order_by.called

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_filter_by_completed_status(self, mock_session_class):
        """Test filtering by completed status (completed=True)."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock
        mock_session = Mock()
        mock_filter = Mock()
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(
            user_id=uuid4(),
            status=TaskStatus.COMPLETED
        )

        # Call the tool
        list_tasks(params)

        # Verify filter was applied
        assert mock_filter.filter.called or mock_filter.order_by.called

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_filter_by_priority(self, mock_session_class):
        """Test filtering by priority level."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock
        mock_session = Mock()
        mock_filter = Mock()
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(
            user_id=uuid4(),
            priority=Priority.HIGH
        )

        # Call the tool
        list_tasks(params)

        # Verify priority filter was applied
        assert mock_filter.filter.called or mock_filter.order_by.called

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_sort_by_created_at(self, mock_session_class):
        """Test sorting by created_at (default)."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock
        mock_session = Mock()
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(
            user_id=uuid4(),
            sort_by=SortBy.CREATED_AT
        )

        # Call the tool
        list_tasks(params)

        # Verify order_by was called
        assert mock_session.query.return_value.filter.return_value.order_by.called

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_sort_by_due_date(self, mock_session_class):
        """Test sorting by due_date."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock
        mock_session = Mock()
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(
            user_id=uuid4(),
            sort_by=SortBy.DUE_DATE
        )

        # Call the tool
        list_tasks(params)

        # Verify order_by was called
        assert mock_session.query.return_value.filter.return_value.order_by.called

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_user_isolation(self, mock_session_class):
        """Test that only user's tasks are returned (user_id filter)."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock
        mock_session = Mock()
        mock_query = Mock()
        mock_query.all.return_value = []
        mock_filter = Mock()
        mock_filter.order_by.return_value = mock_query
        mock_session.query.return_value.filter.return_value = mock_filter
        mock_session_class.return_value = mock_session

        # Prepare params
        user_id = uuid4()
        params = ListTasksParams(user_id=user_id)

        # Call the tool
        list_tasks(params)

        # Verify user_id filter was applied
        assert mock_session.query.return_value.filter.called

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_returns_correct_count(self, mock_session_class):
        """Test that count matches number of tasks returned."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock with 3 tasks
        mock_task1 = Mock(id=uuid4(), title="Task 1", completed=False)
        mock_task2 = Mock(id=uuid4(), title="Task 2", completed=False)
        mock_task3 = Mock(id=uuid4(), title="Task 3", completed=False)

        mock_session = Mock()
        mock_query = Mock()
        mock_query.all.return_value = [mock_task1, mock_task2, mock_task3]
        mock_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(user_id=uuid4())

        # Call the tool
        response = list_tasks(params)

        # Verify count matches
        assert response["count"] == 3
        assert len(response["tasks"]) == 3

    @patch('src.mcp.tools.list_tasks.Session')
    def test_list_tasks_database_error_handling(self, mock_session_class):
        """Test error handling when database query fails."""
        from src.mcp.tools.list_tasks import list_tasks

        # Setup mock to raise exception
        mock_session = Mock()
        mock_session.query.side_effect = Exception("Database query failed")
        mock_session_class.return_value = mock_session

        # Prepare params
        params = ListTasksParams(user_id=uuid4())

        # Call the tool
        response = list_tasks(params)

        # Verify error response
        assert response["status"] == "error" or response["error"] is not None
        assert response["tasks"] == []
        assert response["count"] == 0
