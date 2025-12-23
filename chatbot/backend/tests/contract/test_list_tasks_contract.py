"""Contract tests for list_tasks MCP tool.

Verifies that the list_tasks tool conforms to its interface contract:
- Parameters match ListTasksParams schema
- Response has tasks array and count
- Error handling follows error contract
"""

import pytest
from pydantic import BaseModel, Field, UUID4, ValidationError
from enum import Enum
from uuid import uuid4


class Priority(str, Enum):
    """Priority enum as per contract."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Task status filter enum as per contract."""
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


class SortBy(str, Enum):
    """Sort field enum as per contract."""
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"


class ListTasksParams(BaseModel):
    """Parameter schema for list_tasks tool as per contract."""
    user_id: UUID4 = Field(..., description="User ID whose tasks to list")
    status: TaskStatus = Field(TaskStatus.ALL, description="Filter by completion status")
    priority: Priority | None = Field(None, description="Filter by priority")
    sort_by: SortBy = Field(SortBy.CREATED_AT, description="Sort field")


class TestListTasksContract:
    """Contract tests for list_tasks tool."""

    def test_list_tasks_params_schema_validation(self):
        """Test that ListTasksParams schema validates correctly."""
        # Minimal params (only required field)
        params = ListTasksParams(
            user_id=uuid4()
        )
        assert params.status == TaskStatus.ALL  # Default
        assert params.priority is None  # Default
        assert params.sort_by == SortBy.CREATED_AT  # Default

        # Full params
        user_id = uuid4()
        params = ListTasksParams(
            user_id=user_id,
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            sort_by=SortBy.DUE_DATE
        )
        assert params.user_id == user_id
        assert params.status == TaskStatus.PENDING
        assert params.priority == Priority.HIGH
        assert params.sort_by == SortBy.DUE_DATE

    def test_list_tasks_params_validation_failures(self):
        """Test that ListTasksParams rejects invalid inputs."""
        # Missing required field (user_id)
        with pytest.raises(ValidationError):
            ListTasksParams()

        # Invalid status
        with pytest.raises(ValidationError):
            ListTasksParams(user_id=uuid4(), status="invalid")

        # Invalid priority
        with pytest.raises(ValidationError):
            ListTasksParams(user_id=uuid4(), priority="invalid")

        # Invalid sort_by
        with pytest.raises(ValidationError):
            ListTasksParams(user_id=uuid4(), sort_by="invalid")

    def test_list_tasks_response_structure(self):
        """Test that list_tasks tool returns correct response structure."""
        from src.mcp.tools.list_tasks import list_tasks

        params = ListTasksParams(
            user_id=uuid4()
        )

        response = list_tasks(params)

        # Verify response has all required fields
        assert "tasks" in response
        assert "count" in response
        assert "error" in response

        # Verify response types
        assert isinstance(response["tasks"], list)
        assert isinstance(response["count"], int)
        assert response["error"] is None or isinstance(response["error"], str)

    def test_list_tasks_empty_response(self):
        """Test that list_tasks returns empty array when no tasks exist."""
        from src.mcp.tools.list_tasks import list_tasks

        params = ListTasksParams(
            user_id=uuid4()  # New user with no tasks
        )

        response = list_tasks(params)

        assert response["tasks"] == []
        assert response["count"] == 0
        assert response["error"] is None

    def test_list_tasks_task_object_structure(self):
        """Test that task objects in response have correct structure."""
        from src.mcp.tools.list_tasks import list_tasks
        from src.mcp.tools.add_task import add_task, AddTaskParams

        # First create a task
        user_id = uuid4()
        add_params = AddTaskParams(
            user_id=user_id,
            title="Test task"
        )
        add_task(add_params)

        # Now list tasks
        list_params = ListTasksParams(user_id=user_id)
        response = list_tasks(list_params)

        assert response["count"] > 0
        task = response["tasks"][0]

        # Verify task object structure
        required_fields = ["id", "title", "description", "completed",
                          "created_at", "updated_at", "due_date", "priority"]
        for field in required_fields:
            assert field in task

    def test_list_tasks_status_filter_defaults(self):
        """Test that status filter defaults to 'all'."""
        params = ListTasksParams(user_id=uuid4())
        assert params.status == TaskStatus.ALL

    def test_list_tasks_sort_by_defaults(self):
        """Test that sort_by defaults to 'created_at'."""
        params = ListTasksParams(user_id=uuid4())
        assert params.sort_by == SortBy.CREATED_AT
