"""Task API endpoints with recurrence pattern support."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..logging_config import get_correlation_id, get_logger, set_correlation_id
from ..models.reminder import ReminderResponse
from ..models.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from ..services.reminder_service import ReminderService
from ..services.tag_service import TagService
from ..services.task_service import TaskService

logger = get_logger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_user_id_from_request(request: Request) -> UUID:
    """Extract user ID from request.

    In production, this would extract from JWT token.
    For now, using a mock user ID from header.

    Args:
        request: FastAPI request

    Returns:
        User ID

    Raises:
        HTTPException: If user ID not found
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        # Default user for development
        user_id = "00000000-0000-0000-0000-000000000001"

    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


def _get_correlation_id_from_request(request: Request) -> Optional[str]:
    """Extract correlation ID from request headers.

    Args:
        request: FastAPI request

    Returns:
        Correlation ID or None
    """
    return request.headers.get("X-Correlation-ID") or get_correlation_id()


async def _get_task_service(session: AsyncSession = Depends(get_session)) -> TaskService:
    """Get task service instance.

    Args:
        session: Database session

    Returns:
        TaskService instance
    """
    return TaskService(session)


async def _get_reminder_service(session: AsyncSession = Depends(get_session)) -> ReminderService:
    """Get reminder service instance.

    Args:
        session: Database session

    Returns:
        ReminderService instance
    """
    return ReminderService(session)


async def _get_tag_service(session: AsyncSession = Depends(get_session)) -> TagService:
    """Get tag service instance.

    Args:
        session: Database session

    Returns:
        TagService instance
    """
    return TagService(session)


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    request: Request,
    service: TaskService = Depends(_get_task_service),
    tag_service: TagService = Depends(_get_tag_service),
) -> TaskResponse:
    """Create a new task with optional recurrence pattern.

    Args:
        task_data: Task creation data including optional recurrence_pattern
        request: FastAPI request
        service: Task service

    Returns:
        Created task

    Raises:
        HTTPException: If validation fails or creation fails

    Example:
        POST /tasks
        {
            "title": "Daily Standup",
            "description": "Team standup meeting",
            "priority": "high",
            "due_at": "2024-01-15T09:00:00Z",
            "recurrence_pattern": {
                "pattern_type": "daily",
                "interval": 1,
                "end_condition": "never"
            }
        }
    """
    user_id = _get_user_id_from_request(request)
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Creating task via API",
        user_id=str(user_id),
        title=task_data.title,
    )

    try:
        # Validate recurrence pattern if provided
        if task_data.recurrence_pattern:
            _validate_recurrence_pattern(task_data.recurrence_pattern)

        task = await service.create_task(
            user_id=user_id,
            task_data=task_data,
            correlation_id=correlation_id,
        )

        # Load tags for response
        task_tags = await tag_service.get_task_tags(task.id)
        tag_names = [tag.name for tag in task_tags]

        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            recurrence_pattern_id=task.recurrence_pattern_id,
            parent_task_id=task.parent_task_id,
            tags=tag_names,
        )
    except ValueError as e:
        logger.error("Task creation validation failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Task creation failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    request: Request,
    service: TaskService = Depends(_get_task_service),
    tag_service: TagService = Depends(_get_tag_service),
) -> TaskResponse:
    """Mark a task as completed.

    For recurring tasks, this triggers automatic creation of the next instance
    by the Recurring Task Service.

    Args:
        task_id: Task ID to complete
        request: FastAPI request
        service: Task service

    Returns:
        Completed task

    Raises:
        HTTPException: If task not found or completion fails

    Example:
        POST /tasks/123/complete
    """
    user_id = _get_user_id_from_request(request)
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Completing task via API",
        task_id=task_id,
        user_id=str(user_id),
    )

    try:
        task = await service.complete_task(
            task_id=task_id,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        # Load tags for response
        task_tags = await tag_service.get_task_tags(task.id)
        tag_names = [tag.name for tag in task_tags]

        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            recurrence_pattern_id=task.recurrence_pattern_id,
            parent_task_id=task.parent_task_id,
            tags=tag_names,
        )
    except ValueError as e:
        logger.error("Task not found", task_id=task_id, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Task completion failed", task_id=task_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to complete task")


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    request: Request,
    search: Optional[str] = Query(None, description="Search term for full-text search across title and description"),
    status: Optional[str] = Query(None, description="Filter by status (todo, in_progress, completed)"),
    priority: Optional[str] = Query(None, description="Filter by priority (high, medium, low)"),
    tags: Optional[list[str]] = Query(None, description="Filter by tags (AND logic - task must have all tags)"),
    due_date_start: Optional[str] = Query(None, description="Start of due date range (ISO 8601 format)"),
    due_date_end: Optional[str] = Query(None, description="End of due date range (ISO 8601 format)"),
    sort: Optional[str] = Query(None, description="Sort criteria (comma-separated for compound sorting). Options: priority_asc, priority_desc, due_date_asc, due_date_desc, created_asc, created_desc, title_asc, title_desc. Default: created_desc (or relevance when searching)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    service: TaskService = Depends(_get_task_service),
    tag_service: TagService = Depends(_get_tag_service),
) -> TaskListResponse:
    """List tasks with optional search, filters, sorting, and pagination.

    Supports:
    - Full-text search across task title and description
    - Status filter (todo, in_progress, completed)
    - Priority filter (high, medium, low)
    - Tag filters with AND logic
    - Due date range filtering
    - Multi-criteria sorting (e.g., priority_desc,due_date_asc)
    - Pagination with limit and offset

    Args:
        request: FastAPI request
        search: Optional search term
        status: Optional status filter
        priority: Optional priority filter
        tags: Optional tags filter (AND logic)
        due_date_start: Optional start of due date range
        due_date_end: Optional end of due date range
        sort: Optional sort criteria (comma-separated for compound sorting)
        limit: Maximum tasks to return (1-100)
        offset: Number of tasks to skip
        service: Task service
        tag_service: Tag service

    Returns:
        Paginated list of tasks

    Example:
        GET /tasks?search=presentation&status=todo&priority=high&sort=priority_desc,due_date_asc&limit=20&offset=0
    """
    from datetime import datetime

    user_id = _get_user_id_from_request(request)
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    # Parse due date parameters
    due_date_start_dt = None
    due_date_end_dt = None

    try:
        if due_date_start:
            due_date_start_dt = datetime.fromisoformat(due_date_start.replace('Z', '+00:00'))
        if due_date_end:
            due_date_end_dt = datetime.fromisoformat(due_date_end.replace('Z', '+00:00'))
    except ValueError as e:
        logger.error("Invalid date format", error=str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format. Use ISO 8601 format (e.g., 2024-01-01T00:00:00Z): {str(e)}"
        )

    logger.info(
        "Listing tasks via API",
        user_id=str(user_id),
        search=search,
        status=status,
        priority=priority,
        tags=tags,
        due_date_start=due_date_start_dt,
        due_date_end=due_date_end_dt,
        sort=sort,
        limit=limit,
        offset=offset,
    )

    try:
        tasks, total = await service.list_tasks(
            user_id=user_id,
            search=search,
            status=status,
            priority=priority,
            tags=tags,
            due_date_start=due_date_start_dt,
            due_date_end=due_date_end_dt,
            sort=sort,
            limit=limit,
            offset=offset,
        )

        # Load tags for each task
        task_responses = []
        for task in tasks:
            task_tags = await tag_service.get_task_tags(task.id)
            tag_names = [tag.name for tag in task_tags]

            task_responses.append(
                TaskResponse(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    priority=task.priority,
                    due_at=task.due_at,
                    completed_at=task.completed_at,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    recurrence_pattern_id=task.recurrence_pattern_id,
                    parent_task_id=task.parent_task_id,
                    tags=tag_names,
                )
            )

        return TaskListResponse(
            tasks=task_responses,
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as e:
        logger.error("Task listing failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list tasks")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    request: Request,
    service: TaskService = Depends(_get_task_service),
    tag_service: TagService = Depends(_get_tag_service),
) -> TaskResponse:
    """Get a single task by ID.

    Args:
        task_id: Task ID to retrieve
        request: FastAPI request
        service: Task service

    Returns:
        Task details

    Raises:
        HTTPException: If task not found

    Example:
        GET /tasks/123
    """
    user_id = _get_user_id_from_request(request)
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Getting task via API",
        task_id=task_id,
        user_id=str(user_id),
    )

    task = await service.get_task(task_id=task_id, user_id=user_id)

    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Load tags for response
    task_tags = await tag_service.get_task_tags(task.id)
    tag_names = [tag.name for tag in task_tags]

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_at=task.due_at,
        completed_at=task.completed_at,
        created_at=task.created_at,
        updated_at=task.updated_at,
        recurrence_pattern_id=task.recurrence_pattern_id,
        parent_task_id=task.parent_task_id,
        tags=tag_names,
    )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    request: Request,
    service: TaskService = Depends(_get_task_service),
    tag_service: TagService = Depends(_get_tag_service),
) -> TaskResponse:
    """Update an existing task.

    Args:
        task_id: Task ID to update
        task_data: Task update data (all fields optional)
        request: FastAPI request
        service: Task service

    Returns:
        Updated task

    Raises:
        HTTPException: If task not found or update fails

    Example:
        PATCH /tasks/123
        {
            "title": "Updated title",
            "priority": "high"
        }
    """
    user_id = _get_user_id_from_request(request)
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Updating task via API",
        task_id=task_id,
        user_id=str(user_id),
    )

    try:
        task = await service.update_task(
            task_id=task_id,
            user_id=user_id,
            task_data=task_data,
            correlation_id=correlation_id,
        )

        # Load tags for response
        task_tags = await tag_service.get_task_tags(task.id)
        tag_names = [tag.name for tag in task_tags]

        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            recurrence_pattern_id=task.recurrence_pattern_id,
            parent_task_id=task.parent_task_id,
            tags=tag_names,
        )
    except ValueError as e:
        logger.error("Task not found", task_id=task_id, error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Task update failed", task_id=task_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.post("/{task_id}/stop-recurrence", response_model=TaskResponse)
async def stop_recurrence(
    task_id: int,
    request: Request,
    service: TaskService = Depends(_get_task_service),
    tag_service: TagService = Depends(_get_tag_service),
) -> TaskResponse:
    """Stop recurrence for a recurring task.

    Args:
        task_id: Task ID to stop recurrence for
        request: FastAPI request
        service: Task service

    Returns:
        Updated task (no longer recurring)

    Raises:
        HTTPException: If task not found or not recurring

    Example:
        POST /tasks/123/stop-recurrence
    """
    user_id = _get_user_id_from_request(request)
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Stopping recurrence via API",
        task_id=task_id,
        user_id=str(user_id),
    )

    try:
        task = await service.stop_recurrence(
            task_id=task_id,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        # Load tags for response
        task_tags = await tag_service.get_task_tags(task.id)
        tag_names = [tag.name for tag in task_tags]

        return TaskResponse(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_at=task.due_at,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            recurrence_pattern_id=task.recurrence_pattern_id,
            parent_task_id=task.parent_task_id,
            tags=tag_names,
        )
    except ValueError as e:
        logger.error("Task not found or not recurring", task_id=task_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Stop recurrence failed", task_id=task_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to stop recurrence")


@router.get("/{task_id}/reminders", response_model=list[ReminderResponse])
async def get_task_reminders(
    task_id: int,
    request: Request,
    service: ReminderService = Depends(_get_reminder_service),
) -> list[ReminderResponse]:
    """Get all reminders for a task.

    Args:
        task_id: Task ID to get reminders for
        request: FastAPI request
        service: Reminder service

    Returns:
        List of reminders for the task

    Raises:
        HTTPException: If retrieval fails

    Example:
        GET /tasks/123/reminders
    """
    user_id = _get_user_id_from_request(request)
    correlation_id = _get_correlation_id_from_request(request)
    set_correlation_id(correlation_id)

    logger.info(
        "Getting task reminders via API",
        task_id=task_id,
        user_id=str(user_id),
    )

    try:
        reminders = await service.get_reminders_for_task(
            task_id=task_id,
            user_id=user_id,
        )

        return [
            ReminderResponse(
                id=reminder.id,
                task_id=reminder.task_id,
                user_id=reminder.user_id,
                remind_at=reminder.remind_at,
                notification_channel=reminder.notification_channel,
                delivery_status=reminder.delivery_status,
                retry_count=reminder.retry_count,
                error_message=reminder.error_message,
                created_at=reminder.created_at,
                updated_at=reminder.updated_at,
            )
            for reminder in reminders
        ]
    except Exception as e:
        logger.error("Failed to get task reminders", task_id=task_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get task reminders")


def _validate_recurrence_pattern(pattern: dict) -> None:
    """Validate recurrence pattern fields.

    Args:
        pattern: Recurrence pattern data

    Raises:
        ValueError: If pattern is invalid
    """
    # Validate pattern_type
    pattern_type = pattern.get("pattern_type")
    if pattern_type not in ["daily", "weekly", "monthly"]:
        raise ValueError(
            f"Invalid pattern_type: {pattern_type}. Must be 'daily', 'weekly', or 'monthly'"
        )

    # Validate interval
    interval = pattern.get("interval", 1)
    if not isinstance(interval, int) or interval < 1 or interval > 365:
        raise ValueError(f"Invalid interval: {interval}. Must be between 1 and 365")

    # Validate days_of_week for weekly pattern
    if pattern_type == "weekly":
        days_of_week = pattern.get("days_of_week")
        if days_of_week is not None:
            if not isinstance(days_of_week, list):
                raise ValueError("days_of_week must be a list")
            if not all(isinstance(d, int) and 0 <= d <= 6 for d in days_of_week):
                raise ValueError("days_of_week must contain integers between 0 (Monday) and 6 (Sunday)")
            if len(days_of_week) == 0:
                raise ValueError("days_of_week must not be empty for weekly pattern")

    # Validate day_of_month for monthly pattern
    if pattern_type == "monthly":
        day_of_month = pattern.get("day_of_month")
        if day_of_month is not None:
            if not isinstance(day_of_month, int) or day_of_month < 1 or day_of_month > 31:
                raise ValueError(f"Invalid day_of_month: {day_of_month}. Must be between 1 and 31")

    # Validate end_condition
    end_condition = pattern.get("end_condition")
    if end_condition not in ["never", "after_occurrences", "by_date"]:
        raise ValueError(
            f"Invalid end_condition: {end_condition}. Must be 'never', 'after_occurrences', or 'by_date'"
        )

    # Validate occurrence_count for after_occurrences
    if end_condition == "after_occurrences":
        occurrence_count = pattern.get("occurrence_count")
        if occurrence_count is None:
            raise ValueError("occurrence_count is required for end_condition 'after_occurrences'")
        if not isinstance(occurrence_count, int) or occurrence_count < 1 or occurrence_count > 365:
            raise ValueError(f"Invalid occurrence_count: {occurrence_count}. Must be between 1 and 365")

    # Validate end_date for by_date
    if end_condition == "by_date":
        end_date = pattern.get("end_date")
        if end_date is None:
            raise ValueError("end_date is required for end_condition 'by_date'")
