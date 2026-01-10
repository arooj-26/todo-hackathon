"""Task service with create, complete, and recurrence pattern handling."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dapr.pubsub import get_pubsub_client
from ..events.task_event import TaskEvent, TaskEventType
from ..logging_config import get_logger
from ..models.recurrence import RecurrencePattern, RecurrencePatternCreate
from ..models.reminder import NotificationChannel
from ..models.task import Task, TaskCreate, TaskUpdate
from .recurrence_calculator import RecurrenceCalculator
from .reminder_service import ReminderService
from .tag_service import TagService

logger = get_logger(__name__)


class TaskService:
    """Service for task management with recurrence support."""

    def __init__(self, session: AsyncSession):
        """Initialize task service.

        Args:
            session: Database session
        """
        self.session = session
        self.pubsub = get_pubsub_client()
        self.recurrence_calculator = RecurrenceCalculator()
        self.reminder_service = ReminderService(session)
        self.tag_service = TagService(session)

    async def create_task(
        self,
        user_id: UUID,
        task_data: TaskCreate,
        correlation_id: Optional[str] = None,
    ) -> Task:
        """Create a new task with optional recurrence pattern.

        Args:
            user_id: User ID creating the task
            task_data: Task creation data
            correlation_id: Optional correlation ID for tracing

        Returns:
            Created task instance

        Raises:
            ValueError: If recurrence pattern is invalid
        """
        logger.info(
            "Creating task",
            user_id=str(user_id),
            title=task_data.title,
            has_recurrence=task_data.recurrence_pattern is not None,
        )

        # Create task entity
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            due_at=task_data.due_at,
        )

        # Add task to session and flush to get ID
        self.session.add(task)
        await self.session.flush()

        # Create recurrence pattern if provided
        if task_data.recurrence_pattern:
            await self._create_recurrence_pattern(task.id, task_data.recurrence_pattern)
            # Reload task to get recurrence_pattern_id
            await self.session.refresh(task)

        # Associate tags if provided
        if task_data.tag_names:
            await self.tag_service.associate_tags_with_task(
                task_id=task.id,
                tag_names=task_data.tag_names,
                correlation_id=correlation_id,
            )

        # Commit transaction
        await self.session.commit()
        await self.session.refresh(task)

        logger.info(
            "Task created",
            task_id=task.id,
            user_id=str(user_id),
            recurrence_pattern_id=task.recurrence_pattern_id,
        )

        # Schedule reminders if due_at and reminder_offset_minutes provided
        if task_data.due_at and task_data.reminder_offset_minutes:
            try:
                await self.reminder_service.schedule_reminders_for_task(
                    task_id=task.id,
                    user_id=user_id,
                    due_at=task_data.due_at,
                    reminder_offset_minutes=[task_data.reminder_offset_minutes],
                    notification_channel=NotificationChannel.IN_APP,
                    correlation_id=correlation_id,
                )
                logger.info(
                    "Reminders scheduled for new task",
                    task_id=task.id,
                    reminder_offset_minutes=task_data.reminder_offset_minutes,
                )
            except Exception as e:
                logger.error(
                    "Failed to schedule reminders for new task",
                    task_id=task.id,
                    error=str(e),
                )
                # Don't fail task creation if reminder scheduling fails

        # Publish task created event
        await self._publish_task_event(
            TaskEventType.CREATED,
            task,
            correlation_id=correlation_id,
        )

        return task

    async def complete_task(
        self,
        task_id: int,
        user_id: UUID,
        correlation_id: Optional[str] = None,
    ) -> Task:
        """Mark a task as completed and publish event.

        For recurring tasks, the event triggers creation of the next instance
        by the Recurring Task Service.

        Args:
            task_id: Task ID to complete
            user_id: User ID completing the task
            correlation_id: Optional correlation ID for tracing

        Returns:
            Completed task instance

        Raises:
            ValueError: If task not found or not owned by user
        """
        logger.info(
            "Completing task",
            task_id=task_id,
            user_id=str(user_id),
        )

        # Get task with recurrence pattern
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        # Update task status
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        logger.info(
            "Task completed",
            task_id=task.id,
            user_id=str(user_id),
            has_recurrence=task.recurrence_pattern_id is not None,
        )

        # Cancel pending reminders for completed task
        try:
            cancelled_count = await self.reminder_service.cancel_reminders(
                task_id=task_id,
                user_id=user_id,
                correlation_id=correlation_id,
            )
            logger.info(
                "Reminders cancelled for completed task",
                task_id=task_id,
                cancelled_count=cancelled_count,
            )
        except Exception as e:
            logger.error(
                "Failed to cancel reminders for completed task",
                task_id=task_id,
                error=str(e),
            )
            # Don't fail task completion if reminder cancellation fails

        # Publish task completed event
        # This triggers the Recurring Task Service to create next instance if recurring
        await self._publish_task_event(
            TaskEventType.COMPLETED,
            task,
            correlation_id=correlation_id,
        )

        return task

    async def update_task(
        self,
        task_id: int,
        user_id: UUID,
        task_data: TaskUpdate,
        correlation_id: Optional[str] = None,
    ) -> Task:
        """Update an existing task.

        Args:
            task_id: Task ID to update
            user_id: User ID updating the task
            task_data: Task update data
            correlation_id: Optional correlation ID for tracing

        Returns:
            Updated task instance

        Raises:
            ValueError: If task not found or not owned by user
        """
        logger.info(
            "Updating task",
            task_id=task_id,
            user_id=str(user_id),
        )

        # Get task
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        # Track if due_at changed
        old_due_at = task.due_at
        due_at_changed = False

        # Update fields (only if provided)
        update_data = task_data.dict(exclude_unset=True)
        tag_names_to_update = None

        for field, value in update_data.items():
            if field == "tag_names":
                # Handle tags separately
                tag_names_to_update = value
            else:
                if field == "due_at" and value != old_due_at:
                    due_at_changed = True
                setattr(task, field, value)

        # Update tags if provided
        if tag_names_to_update is not None:
            # Remove existing tag associations
            await self.tag_service.remove_task_tags(
                task_id=task_id,
                correlation_id=correlation_id,
            )
            # Add new tag associations
            if tag_names_to_update:
                await self.tag_service.associate_tags_with_task(
                    task_id=task_id,
                    tag_names=tag_names_to_update,
                    correlation_id=correlation_id,
                )

        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        logger.info(
            "Task updated",
            task_id=task.id,
            user_id=str(user_id),
            due_at_changed=due_at_changed,
        )

        # Reschedule reminders if due_at changed and new due_at exists
        if due_at_changed and task.due_at:
            try:
                # Use default offset of 1 hour if not specified
                # In a real implementation, we'd store the reminder_offset_minutes
                # preference per user or retrieve existing reminder offsets
                await self.reminder_service.reschedule_reminders(
                    task_id=task_id,
                    user_id=user_id,
                    new_due_at=task.due_at,
                    reminder_offset_minutes=[60],  # Default: 1 hour before
                    notification_channel=NotificationChannel.IN_APP,
                    correlation_id=correlation_id,
                )
                logger.info(
                    "Reminders rescheduled for updated task",
                    task_id=task_id,
                )
            except Exception as e:
                logger.error(
                    "Failed to reschedule reminders for updated task",
                    task_id=task_id,
                    error=str(e),
                )
                # Don't fail task update if reminder rescheduling fails

        # Publish task updated event
        await self._publish_task_event(
            TaskEventType.UPDATED,
            task,
            correlation_id=correlation_id,
        )

        return task

    async def get_task(
        self,
        task_id: int,
        user_id: UUID,
    ) -> Optional[Task]:
        """Get a task by ID.

        Args:
            task_id: Task ID to get
            user_id: User ID requesting the task

        Returns:
            Task instance or None if not found
        """
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_tasks(
        self,
        user_id: UUID,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[list[str]] = None,
        due_date_start: Optional[datetime] = None,
        due_date_end: Optional[datetime] = None,
        sort: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        """List tasks with optional filters, search, and sorting.

        Args:
            user_id: User ID to filter by
            search: Optional search term for full-text search
            status: Optional status filter
            priority: Optional priority filter
            tags: Optional tags filter (AND logic - task must have all tags)
            due_date_start: Optional start of due date range (inclusive)
            due_date_end: Optional end of due date range (inclusive)
            sort: Optional sort criteria (comma-separated for compound sorting)
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip

        Returns:
            Tuple of (tasks, total_count)
        """
        from .search_service import SearchService

        # Use SearchService for combined search and filtering
        search_service = SearchService(self.session)
        return await search_service.search_and_filter_tasks(
            user_id=str(user_id),
            search=search,
            status=status,
            priority=priority,
            tags=tags,
            due_date_start=due_date_start,
            due_date_end=due_date_end,
            sort=sort,
            limit=limit,
            offset=offset,
        )

    async def stop_recurrence(
        self,
        task_id: int,
        user_id: UUID,
        correlation_id: Optional[str] = None,
    ) -> Task:
        """Stop recurrence for a recurring task.

        Args:
            task_id: Task ID to stop recurrence for
            user_id: User ID requesting the action
            correlation_id: Optional correlation ID for tracing

        Returns:
            Updated task instance

        Raises:
            ValueError: If task not found or not recurring
        """
        logger.info(
            "Stopping recurrence",
            task_id=task_id,
            user_id=str(user_id),
        )

        # Get task
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        if not task.recurrence_pattern_id:
            raise ValueError(f"Task {task_id} is not a recurring task")

        # Remove recurrence pattern
        task.recurrence_pattern_id = None
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        logger.info(
            "Recurrence stopped",
            task_id=task.id,
            user_id=str(user_id),
        )

        # Publish task updated event
        await self._publish_task_event(
            TaskEventType.UPDATED,
            task,
            correlation_id=correlation_id,
        )

        return task

    async def _create_recurrence_pattern(
        self,
        task_id: int,
        pattern_data: dict,
    ) -> RecurrencePattern:
        """Create recurrence pattern for a task.

        Args:
            task_id: Task ID to create pattern for
            pattern_data: Pattern configuration data

        Returns:
            Created recurrence pattern

        Raises:
            ValueError: If pattern data is invalid
        """
        # Validate and create pattern
        pattern_create = RecurrencePatternCreate(**pattern_data)

        pattern = RecurrencePattern(
            task_id=task_id,
            pattern_type=pattern_create.pattern_type,
            interval=pattern_create.interval,
            days_of_week=pattern_create.days_of_week,
            day_of_month=pattern_create.day_of_month,
            end_condition=pattern_create.end_condition,
            occurrence_count=pattern_create.occurrence_count,
            end_date=pattern_create.end_date,
            current_occurrence=0,
        )

        self.session.add(pattern)
        await self.session.flush()

        # Update task with recurrence_pattern_id
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one()
        task.recurrence_pattern_id = pattern.id

        return pattern

    async def _publish_task_event(
        self,
        event_type: TaskEventType,
        task: Task,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Publish task event to Kafka via Dapr.

        Args:
            event_type: Type of event
            task: Task instance
            correlation_id: Optional correlation ID for tracing
        """
        # Convert task to dict for snapshot
        task_dict = {
            "id": task.id,
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_at": task.due_at.isoformat() if task.due_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "recurrence_pattern_id": task.recurrence_pattern_id,
            "parent_task_id": task.parent_task_id,
        }

        # Create event
        event = TaskEvent.from_task(
            event_type=event_type,
            task=task_dict,
            correlation_id=correlation_id,
        )

        # Publish to task-events topic
        try:
            await self.pubsub.publish(
                topic="task-events",
                event=event,
                correlation_id=correlation_id,
            )

            logger.info(
                "Task event published",
                event_type=event_type.value,
                task_id=task.id,
                topic="task-events",
            )
        except Exception as e:
            logger.error(
                "Failed to publish task event",
                event_type=event_type.value,
                task_id=task.id,
                error=str(e),
            )
            # Don't fail the operation if event publishing fails
            # The task is already created/updated in the database
