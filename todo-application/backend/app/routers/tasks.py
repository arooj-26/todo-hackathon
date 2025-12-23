"""Tasks router for task management endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime

from app.database import get_session
from app.models.user import User
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.auth.middleware import get_current_user, verify_user_authorization

router = APIRouter()


@router.get("/{user_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> List[TaskResponse]:
    """
    Get all tasks for a specific user.

    Args:
        user_id: User ID whose tasks to fetch
        session: Database session
        current_user: Current authenticated user

    Returns:
        List of TaskResponse objects sorted by created_at (newest first)

    Raises:
        HTTPException: 403 if user is not authorized to access these tasks

    Example:
        GET /api/1/tasks
        Authorization: Bearer eyJhbGci...

        Response:
        [
            {
                "id": 1,
                "user_id": 1,
                "description": "Buy groceries",
                "completed": false,
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            },
            ...
        ]
    """
    # Verify user is authorized to access these tasks
    verify_user_authorization(current_user, user_id)

    # Fetch tasks for this user, ordered by created_at descending
    statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    tasks = session.exec(statement).all()

    return [TaskResponse.model_validate(task) for task in tasks]


@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TaskResponse:
    """
    Create a new task for a user.

    Args:
        user_id: User ID who owns the task
        task_data: Task creation data (description)
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created TaskResponse object

    Raises:
        HTTPException: 403 if user is not authorized to create tasks for this user_id

    Example:
        POST /api/1/tasks
        Authorization: Bearer eyJhbGci...
        {
            "description": "Buy groceries"
        }

        Response:
        {
            "id": 1,
            "user_id": 1,
            "description": "Buy groceries",
            "completed": false,
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T12:00:00Z"
        }
    """
    # Verify user is authorized to create tasks for this user_id
    verify_user_authorization(current_user, user_id)

    # Create new task
    new_task = Task(
        user_id=user_id,
        description=task_data.description,
        completed=False
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return TaskResponse.model_validate(new_task)


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: int,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TaskResponse:
    """
    Get a specific task by ID.

    Args:
        user_id: User ID who owns the task
        task_id: Task ID to fetch
        session: Database session
        current_user: Current authenticated user

    Returns:
        TaskResponse object

    Raises:
        HTTPException: 403 if user is not authorized
        HTTPException: 404 if task not found

    Example:
        GET /api/1/tasks/1
        Authorization: Bearer eyJhbGci...

        Response:
        {
            "id": 1,
            "user_id": 1,
            "description": "Buy groceries",
            "completed": false,
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T12:00:00Z"
        }
    """
    # Verify user is authorized
    verify_user_authorization(current_user, user_id)

    # Fetch task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.model_validate(task)


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TaskResponse:
    """
    Update a task's description and/or completion status.

    Args:
        user_id: User ID who owns the task
        task_id: Task ID to update
        task_data: Task update data (description and/or completed)
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated TaskResponse object

    Raises:
        HTTPException: 403 if user is not authorized
        HTTPException: 404 if task not found

    Example:
        PUT /api/1/tasks/1
        Authorization: Bearer eyJhbGci...
        {
            "description": "Buy groceries and cook dinner",
            "completed": true
        }

        Response:
        {
            "id": 1,
            "user_id": 1,
            "description": "Buy groceries and cook dinner",
            "completed": true,
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T13:00:00Z"
        }
    """
    # Verify user is authorized
    verify_user_authorization(current_user, user_id)

    # Fetch task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task fields if provided
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.patch("/{user_id}/tasks/{task_id}/toggle", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: int,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> TaskResponse:
    """
    Toggle a task's completion status.

    Args:
        user_id: User ID who owns the task
        task_id: Task ID to toggle
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated TaskResponse object

    Raises:
        HTTPException: 403 if user is not authorized
        HTTPException: 404 if task not found

    Example:
        PATCH /api/1/tasks/1/toggle
        Authorization: Bearer eyJhbGci...

        Response:
        {
            "id": 1,
            "user_id": 1,
            "description": "Buy groceries",
            "completed": true,
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T13:00:00Z"
        }
    """
    # Verify user is authorized
    verify_user_authorization(current_user, user_id)

    # Fetch task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return TaskResponse.model_validate(task)


@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: int,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete a task.

    Args:
        user_id: User ID who owns the task
        task_id: Task ID to delete
        session: Database session
        current_user: Current authenticated user

    Returns:
        204 No Content

    Raises:
        HTTPException: 403 if user is not authorized
        HTTPException: 404 if task not found

    Example:
        DELETE /api/1/tasks/1
        Authorization: Bearer eyJhbGci...

        Response: 204 No Content
    """
    # Verify user is authorized
    verify_user_authorization(current_user, user_id)

    # Fetch task
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete task
    session.delete(task)
    session.commit()

    return None
