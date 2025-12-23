"""
Unit tests for Task model.

Tests creation, validation, default values, and UUID generation.
Following Test-First Quality - these tests should FAIL until Task model is implemented.
"""
import pytest
from datetime import datetime
from uuid import UUID
from sqlmodel import Session

from src.models.task import Task, PriorityEnum


class TestTaskModel:
    """Test suite for Task model."""

    def test_task_creation_with_required_fields(self, session: Session):
        """Test creating a task with only required fields."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        task = Task(
            user_id=user_id,
            title="Buy groceries"
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.id is not None
        assert isinstance(task.id, UUID)
        assert task.user_id == user_id
        assert task.title == "Buy groceries"
        assert task.description is None
        assert task.completed is False
        assert task.priority == PriorityEnum.MEDIUM
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert task.due_date is None

    def test_task_creation_with_all_fields(self, session: Session):
        """Test creating a task with all fields specified."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        due_date = datetime(2025, 12, 25, 10, 0, 0)

        task = Task(
            user_id=user_id,
            title="Call mom",
            description="Wish her happy holidays",
            priority=PriorityEnum.HIGH,
            due_date=due_date,
            completed=True
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.title == "Call mom"
        assert task.description == "Wish her happy holidays"
        assert task.priority == PriorityEnum.HIGH
        assert task.due_date == due_date
        assert task.completed is True

    def test_task_uuid_generation(self, session: Session):
        """Test that each task gets a unique UUID."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        task1 = Task(user_id=user_id, title="Task 1")
        task2 = Task(user_id=user_id, title="Task 2")

        session.add(task1)
        session.add(task2)
        session.commit()

        assert task1.id != task2.id
        assert isinstance(task1.id, UUID)
        assert isinstance(task2.id, UUID)

    def test_task_default_values(self, session: Session):
        """Test that default values are set correctly."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        task = Task(user_id=user_id, title="Test task")

        assert task.completed is False
        assert task.priority == PriorityEnum.MEDIUM
        assert task.description is None
        assert task.due_date is None

    def test_task_title_validation(self, session: Session):
        """Test that title validation works (max length 500)."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        # Valid title
        task = Task(user_id=user_id, title="A" * 500)
        session.add(task)
        session.commit()
        assert len(task.title) == 500

        # Title too long should be truncated or raise error
        # This depends on SQLModel/database configuration

    def test_task_timestamps(self, session: Session):
        """Test that timestamps are set on creation."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        before = datetime.utcnow()
        task = Task(user_id=user_id, title="Test")
        session.add(task)
        session.commit()
        session.refresh(task)
        after = datetime.utcnow()

        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after
        # On creation, timestamps should be very close (within 1 second)
        time_diff = abs((task.updated_at - task.created_at).total_seconds())
        assert time_diff < 1
