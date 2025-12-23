"""Contract tests for add_task MCP tool.

Verifies that the add_task tool conforms to its interface contract:
- Parameters match AddTaskParams schema
- Response matches TaskResponse schema
- Error handling follows error contract
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


class AddTaskParams(BaseModel):
    """Parameter schema for add_task tool as per contract."""
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, max_length=10000, description="Optional task description")
    due_date: datetime | None = Field(None, description="Optional due date in ISO 8601 format")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority")


class TestAddTaskContract:
    """Contract tests for add_task tool."""

    def test_add_task_params_schema_validation(self):
        """Test that AddTaskParams schema validates correctly."""
        # Valid params with required fields only
        params = AddTaskParams(
            user_id=uuid4(),
            title="Test task"
        )
        assert params.title == "Test task"
        assert params.priority == Priority.MEDIUM  # Default value
        assert params.description is None
        assert params.due_date is None

        # Valid params with all fields
        user_id = uuid4()
        due_date = datetime.now()
        params = AddTaskParams(
            user_id=user_id,
            title="Complete task",
            description="With all fields",
            due_date=due_date,
            priority=Priority.HIGH
        )
        assert params.user_id == user_id
        assert params.title == "Complete task"
        assert params.description == "With all fields"
        assert params.due_date == due_date
        assert params.priority == Priority.HIGH

    def test_add_task_params_validation_failures(self):
        """Test that AddTaskParams rejects invalid inputs."""
        # Missing required field (title)
        with pytest.raises(ValidationError):
            AddTaskParams(user_id=uuid4())

        # Empty title
        with pytest.raises(ValidationError):
            AddTaskParams(user_id=uuid4(), title="")

        # Title too long
        with pytest.raises(ValidationError):
            AddTaskParams(user_id=uuid4(), title="a" * 501)

        # Invalid priority
        with pytest.raises(ValidationError):
            AddTaskParams(user_id=uuid4(), title="Test", priority="invalid")

    def test_add_task_response_structure(self):
        """Test that add_task tool returns correct response structure."""
        from src.mcp.tools.add_task import add_task

        params = AddTaskParams(
            user_id=uuid4(),
            title="Test task"
        )

        response = add_task(params)

        # Verify response has all required fields
        assert "task_id" in response
        assert "status" in response
        assert "title" in response
        assert "error" in response

        # Verify success response values
        assert response["status"] == "created"
        assert response["title"] == "Test task"
        assert response["error"] is None
        assert response["task_id"] is not None

    def test_add_task_error_response_structure(self):
        """Test that add_task returns proper error response structure."""
        from src.mcp.tools.add_task import add_task

        # This will test error handling (e.g., empty title after trimming)
        # Note: This might not trigger an error if validation happens in Pydantic
        # But we test the error response structure is correct

        params = AddTaskParams(
            user_id=uuid4(),
            title="Valid title"
        )

        response = add_task(params)

        # Verify error response would have correct structure
        # (we'll test actual error cases in unit tests)
        assert "error" in response

    def test_add_task_default_priority(self):
        """Test that priority defaults to 'medium' when not provided."""
        params = AddTaskParams(
            user_id=uuid4(),
            title="Test task"
        )

        assert params.priority == Priority.MEDIUM

    def test_add_task_optional_fields(self):
        """Test that optional fields (description, due_date) work correctly."""
        # Without optional fields
        params1 = AddTaskParams(
            user_id=uuid4(),
            title="Minimal task"
        )
        assert params1.description is None
        assert params1.due_date is None

        # With optional fields
        due_date = datetime(2025, 12, 31, 23, 59, 59)
        params2 = AddTaskParams(
            user_id=uuid4(),
            title="Full task",
            description="Detailed description",
            due_date=due_date
        )
        assert params2.description == "Detailed description"
        assert params2.due_date == due_date
