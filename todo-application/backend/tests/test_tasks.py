"""Integration tests for task management endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


def create_user_and_get_token(client: TestClient, email: str, password: str = "password123"):
    """Helper function to create a user and get their auth token."""
    response = client.post(
        "/auth/signup",
        json={"email": email, "password": password}
    )
    assert response.status_code == 201
    return response.json()["access_token"], response.json()["user"]["id"]


def test_create_task_success(client: TestClient, session: Session):
    """
    Test T052: Task creation - submit form → task created → appears in list
    """
    # Create user and get token
    token, user_id = create_user_and_get_token(client, "tasks@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    task_data = {"description": "Buy groceries"}
    response = client.post(
        f"/api/{user_id}/tasks",
        json=task_data,
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()

    # Verify task data
    assert data["description"] == "Buy groceries"
    assert data["completed"] is False
    assert data["user_id"] == user_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify task appears in list
    list_response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == data["id"]
    assert tasks[0]["description"] == "Buy groceries"


def test_create_task_unauthorized(client: TestClient, session: Session):
    """Test creating task for another user returns 403."""
    # Create user
    token, user_id = create_user_and_get_token(client, "user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Try to create task for different user_id
    task_data = {"description": "Unauthorized task"}
    response = client.post(
        f"/api/{user_id + 999}/tasks",
        json=task_data,
        headers=headers
    )

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"].lower()


def test_create_task_without_auth(client: TestClient, session: Session):
    """Test creating task without authentication returns 403."""
    task_data = {"description": "Unauthenticated task"}
    response = client.post(
        "/api/1/tasks",
        json=task_data
    )

    assert response.status_code == 403


def test_get_tasks_list(client: TestClient, session: Session):
    """
    Test T053: Task listing - multiple tasks → all displayed → sorted by created_at
    """
    # Create user and get token
    token, user_id = create_user_and_get_token(client, "list@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create multiple tasks
    tasks_to_create = [
        "First task",
        "Second task",
        "Third task"
    ]

    created_ids = []
    for desc in tasks_to_create:
        response = client.post(
            f"/api/{user_id}/tasks",
            json={"description": desc},
            headers=headers
        )
        assert response.status_code == 201
        created_ids.append(response.json()["id"])

    # Get tasks list
    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()

    # Verify all tasks are returned
    assert len(tasks) == 3

    # Verify tasks are sorted by created_at descending (newest first)
    # The last created task should be first in the list
    assert tasks[0]["description"] == "Third task"
    assert tasks[1]["description"] == "Second task"
    assert tasks[2]["description"] == "First task"


def test_get_tasks_empty_list(client: TestClient, session: Session):
    """Test getting tasks for user with no tasks returns empty list."""
    token, user_id = create_user_and_get_token(client, "empty@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get(f"/api/{user_id}/tasks", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_data_isolation(client: TestClient, session: Session):
    """
    Test T054: Data isolation - user A tasks not visible to user B
    """
    # Create user A and their task
    token_a, user_a_id = create_user_and_get_token(client, "usera@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    task_a_response = client.post(
        f"/api/{user_a_id}/tasks",
        json={"description": "User A's task"},
        headers=headers_a
    )
    assert task_a_response.status_code == 201
    task_a_id = task_a_response.json()["id"]

    # Create user B and their task
    token_b, user_b_id = create_user_and_get_token(client, "userb@example.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    task_b_response = client.post(
        f"/api/{user_b_id}/tasks",
        json={"description": "User B's task"},
        headers=headers_b
    )
    assert task_b_response.status_code == 201
    task_b_id = task_b_response.json()["id"]

    # Verify user A only sees their own tasks
    tasks_a = client.get(f"/api/{user_a_id}/tasks", headers=headers_a).json()
    assert len(tasks_a) == 1
    assert tasks_a[0]["description"] == "User A's task"
    assert tasks_a[0]["user_id"] == user_a_id

    # Verify user B only sees their own tasks
    tasks_b = client.get(f"/api/{user_b_id}/tasks", headers=headers_b).json()
    assert len(tasks_b) == 1
    assert tasks_b[0]["description"] == "User B's task"
    assert tasks_b[0]["user_id"] == user_b_id

    # Verify user B cannot access user A's tasks
    response = client.get(f"/api/{user_a_id}/tasks", headers=headers_b)
    assert response.status_code == 403

    # Verify user A cannot access user B's tasks
    response = client.get(f"/api/{user_b_id}/tasks", headers=headers_a)
    assert response.status_code == 403


def test_get_specific_task(client: TestClient, session: Session):
    """Test getting a specific task by ID."""
    token, user_id = create_user_and_get_token(client, "specific@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Specific task"},
        headers=headers
    )
    task_id = create_response.json()["id"]

    # Get specific task
    response = client.get(f"/api/{user_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["description"] == "Specific task"


def test_update_task(client: TestClient, session: Session):
    """Test updating a task's description and completion status."""
    token, user_id = create_user_and_get_token(client, "update@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Original description"},
        headers=headers
    )
    task_id = create_response.json()["id"]

    # Update task
    update_response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"description": "Updated description", "completed": True},
        headers=headers
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["description"] == "Updated description"
    assert data["completed"] is True


def test_toggle_task_completion(client: TestClient, session: Session):
    """Test toggling task completion status."""
    token, user_id = create_user_and_get_token(client, "toggle@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Toggle task"},
        headers=headers
    )
    task_id = create_response.json()["id"]
    assert create_response.json()["completed"] is False

    # Toggle to completed
    toggle_response = client.patch(
        f"/api/{user_id}/tasks/{task_id}/toggle",
        headers=headers
    )
    assert toggle_response.status_code == 200
    assert toggle_response.json()["completed"] is True

    # Toggle back to incomplete
    toggle_response2 = client.patch(
        f"/api/{user_id}/tasks/{task_id}/toggle",
        headers=headers
    )
    assert toggle_response2.status_code == 200
    assert toggle_response2.json()["completed"] is False


def test_delete_task(client: TestClient, session: Session):
    """Test deleting a task."""
    token, user_id = create_user_and_get_token(client, "delete@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create a task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Task to delete"},
        headers=headers
    )
    task_id = create_response.json()["id"]

    # Delete task
    delete_response = client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers=headers
    )
    assert delete_response.status_code == 204

    # Verify task is deleted
    get_response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers=headers
    )
    assert get_response.status_code == 404


def test_task_persistence_across_sessions(client: TestClient, session: Session):
    """Test that tasks persist across sessions."""
    # Create user and task
    token, user_id = create_user_and_get_token(client, "persist@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        f"/api/{user_id}/tasks",
        json={"description": "Persistent task"},
        headers=headers
    )

    # Sign in again (simulate new session)
    signin_response = client.post(
        "/auth/signin",
        json={"email": "persist@example.com", "password": "password123"}
    )
    new_token = signin_response.json()["access_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}

    # Verify task still exists
    tasks_response = client.get(f"/api/{user_id}/tasks", headers=new_headers)
    assert tasks_response.status_code == 200
    tasks = tasks_response.json()
    assert len(tasks) == 1
    assert tasks[0]["description"] == "Persistent task"
