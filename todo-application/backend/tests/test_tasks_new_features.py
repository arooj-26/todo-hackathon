"""
Tests for task endpoints with new features (due_date and recurrence)
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.task import Task
from app.models.user import User
from app.database import engine
import json


def test_create_task_with_due_date_and_recurrence():
    """Test creating a task with due_date and recurrence fields."""
    from app.main import app
    client = TestClient(app)
    
    # Create a user first
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    user_response = response.json()
    user_id = user_response["user_id"]
    
    # Create a task with due_date and recurrence
    task_data = {
        "description": "Test task with due date",
        "priority": "high",
        "due_date": "2025-12-31T23:59:59",
        "recurrence": "weekly"
    }
    
    response = client.post(f"/api/{user_id}/tasks", json=task_data)
    assert response.status_code == 200
    
    task_response = response.json()
    assert task_response["description"] == "Test task with due date"
    assert task_response["priority"] == "high"
    assert task_response["due_date"] == "2025-12-31T23:59:59"
    assert task_response["recurrence"] == "weekly"
    assert task_response["completed"] is False


def test_update_task_with_due_date_and_recurrence():
    """Test updating a task with due_date and recurrence fields."""
    from app.main import app
    client = TestClient(app)
    
    # Create a user first
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    user_response = response.json()
    user_id = user_response["user_id"]
    
    # Create a task first
    task_data = {
        "description": "Original task",
        "priority": "medium"
    }
    response = client.post(f"/api/{user_id}/tasks", json=task_data)
    assert response.status_code == 200
    task_id = response.json()["id"]
    
    # Update the task with due_date and recurrence
    update_data = {
        "description": "Updated task",
        "due_date": "2025-06-15T10:30:00",
        "recurrence": "daily"
    }
    
    response = client.put(f"/api/{user_id}/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    
    updated_task = response.json()
    assert updated_task["description"] == "Updated task"
    assert updated_task["due_date"] == "2025-06-15T10:30:00"
    assert updated_task["recurrence"] == "daily"


def test_get_tasks_filters():
    """Test getting tasks with various filters."""
    from app.main import app
    client = TestClient(app)
    
    # Create a user first
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    user_response = response.json()
    user_id = user_response["user_id"]
    
    # Create tasks with different properties
    tasks = [
        {
            "description": "Completed task",
            "completed": True,
            "priority": "medium",
            "due_date": "2024-12-20T10:00:00",  # Past due date
            "recurrence": "weekly"
        },
        {
            "description": "Pending task",
            "completed": False,
            "priority": "high",
            "due_date": "2025-12-31T23:59:59",  # Future due date
            "recurrence": "daily"
        },
        {
            "description": "Overdue task",
            "completed": False,
            "priority": "low",
            "due_date": "2024-12-20T10:00:00",  # Past due date
            "recurrence": None
        }
    ]
    
    for task in tasks:
        response = client.post(f"/api/{user_id}/tasks", json=task)
        assert response.status_code == 200
    
    # Test getting all tasks
    response = client.get(f"/api/{user_id}/tasks")
    assert response.status_code == 200
    all_tasks = response.json()
    assert len(all_tasks) == 3
    
    # Test getting completed tasks
    response = client.get(f"/api/{user_id}/tasks?completed=true")
    assert response.status_code == 200
    completed_tasks = response.json()
    assert len(completed_tasks) == 1
    assert completed_tasks[0]["completed"] is True
    
    # Test getting pending tasks
    response = client.get(f"/api/{user_id}/tasks?completed=false")
    assert response.status_code == 200
    pending_tasks = response.json()
    assert len(pending_tasks) == 2
    for task in pending_tasks:
        assert task["completed"] is False


def test_database_schema_update():
    """Test that the database schema has the new columns."""
    with Session(engine) as session:
        # Check that the tasks table has the new columns by creating and querying a task
        user = User(email="schema_test@example.com", password_hash="hash")
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create a task with the new fields
        task = Task(
            user_id=user.id,
            description="Schema test task",
            due_date=datetime(2025, 12, 31),
            recurrence="monthly"
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        
        # Verify the task was saved with the new fields
        assert task.due_date is not None
        assert task.recurrence == "monthly"
        
        # Query the task back
        queried_task = session.exec(select(Task).where(Task.id == task.id)).first()
        assert queried_task is not None
        assert queried_task.due_date == datetime(2025, 12, 31)
        assert queried_task.recurrence == "monthly"


def test_invalid_recurrence_value():
    """Test that invalid recurrence values are rejected."""
    from app.main import app
    client = TestClient(app)
    
    # Create a user first
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    user_response = response.json()
    user_id = user_response["user_id"]
    
    # Try to create a task with invalid recurrence
    task_data = {
        "description": "Invalid recurrence task",
        "priority": "medium",
        "recurrence": "yearly"  # Invalid value
    }
    
    response = client.post(f"/api/{user_id}/tasks", json=task_data)
    assert response.status_code == 422  # Validation error


def test_task_with_null_due_date_and_recurrence():
    """Test creating a task with null due_date and recurrence."""
    from app.main import app
    client = TestClient(app)
    
    # Create a user first
    user_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 200
    user_response = response.json()
    user_id = user_response["user_id"]
    
    # Create a task without due_date and recurrence
    task_data = {
        "description": "Task without due date or recurrence",
        "priority": "medium"
    }
    
    response = client.post(f"/api/{user_id}/tasks", json=task_data)
    assert response.status_code == 200
    
    task_response = response.json()
    assert task_response["description"] == "Task without due date or recurrence"
    assert task_response["due_date"] is None
    assert task_response["recurrence"] is None