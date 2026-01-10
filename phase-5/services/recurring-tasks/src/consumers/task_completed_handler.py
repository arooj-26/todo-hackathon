"""Task completed event handler with recurring task generation."""

import logging
from datetime import datetime
from typing import Any, Optional

from ..services.recurrence_calculator import RecurrenceCalculator
from ..services.task_creator import TaskCreator

logger = logging.getLogger(__name__)


class TaskCompletedHandler:
    """Handler for task completed events with recurrence support."""

    def __init__(self):
        """Initialize task completed handler."""
        self.recurrence_calculator = RecurrenceCalculator()
        self.task_creator = TaskCreator()

    async def handle(self, event_data: dict[str, Any]) -> None:
        """
        Handle task completed event.

        Filters for recurring tasks and generates next instance if applicable.

        Args:
            event_data: Task event data from Kafka
        """
        correlation_id = event_data.get("correlation_id")

        logger.info(
            "Processing task completed event",
            extra={
                "correlation_id": correlation_id,
                "event_type": event_data.get("event_type"),
            },
        )

        # Extract task snapshot
        task_snapshot = event_data.get("task_snapshot", {})
        event_type = event_data.get("event_type")

        # Only process completed events
        if event_type != "completed":
            logger.debug(
                "Skipping non-completed event",
                extra={
                    "event_type": event_type,
                    "task_id": task_snapshot.get("id"),
                },
            )
            return

        # Check if task has recurrence pattern
        recurrence_pattern_id = task_snapshot.get("recurrence_pattern_id")
        if not recurrence_pattern_id:
            logger.debug(
                "Skipping non-recurring task",
                extra={
                    "task_id": task_snapshot.get("id"),
                },
            )
            return

        logger.info(
            "Processing recurring task completion",
            extra={
                "task_id": task_snapshot.get("id"),
                "recurrence_pattern_id": recurrence_pattern_id,
                "correlation_id": correlation_id,
            },
        )

        # Get recurrence pattern from task snapshot
        # In a full implementation, we would fetch the pattern from database
        # For now, we'll work with the data available in the event
        # NOTE: The Chat API should include recurrence pattern in task snapshot
        recurrence_pattern = task_snapshot.get("recurrence_pattern")

        if not recurrence_pattern:
            logger.warning(
                "Recurrence pattern not found in task snapshot",
                extra={
                    "task_id": task_snapshot.get("id"),
                    "recurrence_pattern_id": recurrence_pattern_id,
                },
            )
            # In production, we would query the database here
            return

        # Calculate next due date
        try:
            next_due_date = await self._calculate_next_due_date(
                task_snapshot=task_snapshot,
                recurrence_pattern=recurrence_pattern,
            )

            if not next_due_date:
                logger.info(
                    "Recurrence ended - no more instances to create",
                    extra={
                        "task_id": task_snapshot.get("id"),
                        "end_condition": recurrence_pattern.get("end_condition"),
                    },
                )
                return

            # Create next task instance
            await self._create_next_instance(
                task_snapshot=task_snapshot,
                next_due_date=next_due_date,
                correlation_id=correlation_id,
            )

        except Exception as e:
            logger.error(
                "Error processing recurring task",
                extra={
                    "task_id": task_snapshot.get("id"),
                    "error": str(e),
                    "correlation_id": correlation_id,
                },
                exc_info=True,
            )

    async def _calculate_next_due_date(
        self,
        task_snapshot: dict[str, Any],
        recurrence_pattern: dict[str, Any],
    ) -> Optional[datetime]:
        """
        Calculate next due date for recurring task.

        Args:
            task_snapshot: Completed task data
            recurrence_pattern: Recurrence pattern configuration

        Returns:
            Next due date or None if recurrence should end
        """
        # Get current due date
        current_due_date_str = task_snapshot.get("due_at")
        if not current_due_date_str:
            logger.warning(
                "Recurring task has no due_at - cannot calculate next instance",
                extra={
                    "task_id": task_snapshot.get("id"),
                },
            )
            return None

        # Parse current due date
        if isinstance(current_due_date_str, str):
            current_due_date = datetime.fromisoformat(
                current_due_date_str.replace("Z", "+00:00")
            )
        else:
            current_due_date = current_due_date_str

        # Extract pattern fields
        pattern_type = recurrence_pattern.get("pattern_type")
        interval = recurrence_pattern.get("interval", 1)
        days_of_week = recurrence_pattern.get("days_of_week")
        day_of_month = recurrence_pattern.get("day_of_month")
        end_condition = recurrence_pattern.get("end_condition", "never")
        occurrence_count = recurrence_pattern.get("occurrence_count")
        current_occurrence = recurrence_pattern.get("current_occurrence", 0)

        # Parse end_date if present
        end_date = None
        end_date_str = recurrence_pattern.get("end_date")
        if end_date_str:
            if isinstance(end_date_str, str):
                end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
            else:
                end_date = end_date_str

        # Calculate next due date
        next_due_date = self.recurrence_calculator.calculate_next_due_date(
            pattern_type=pattern_type,
            interval=interval,
            current_due_date=current_due_date,
            days_of_week=days_of_week,
            day_of_month=day_of_month,
            end_condition=end_condition,
            end_date=end_date,
            occurrence_count=occurrence_count,
            current_occurrence=current_occurrence,
        )

        if next_due_date:
            logger.info(
                "Calculated next due date",
                extra={
                    "task_id": task_snapshot.get("id"),
                    "current_due_date": current_due_date.isoformat(),
                    "next_due_date": next_due_date.isoformat(),
                },
            )

        return next_due_date

    async def _create_next_instance(
        self,
        task_snapshot: dict[str, Any],
        next_due_date: datetime,
        correlation_id: Optional[str],
    ) -> None:
        """
        Create next recurring task instance.

        Args:
            task_snapshot: Original completed task data
            next_due_date: Due date for next instance
            correlation_id: Optional correlation ID for tracing
        """
        logger.info(
            "Creating next recurring task instance",
            extra={
                "original_task_id": task_snapshot.get("id"),
                "next_due_date": next_due_date.isoformat(),
                "correlation_id": correlation_id,
            },
        )

        # Create next instance via Chat API
        created_task = await self.task_creator.create_next_task_instance(
            original_task=task_snapshot,
            next_due_date=next_due_date,
            correlation_id=correlation_id,
        )

        if created_task:
            logger.info(
                "Successfully created next recurring task instance",
                extra={
                    "original_task_id": task_snapshot.get("id"),
                    "new_task_id": created_task.get("id"),
                    "next_due_date": next_due_date.isoformat(),
                    "correlation_id": correlation_id,
                },
            )
        else:
            logger.error(
                "Failed to create next recurring task instance",
                extra={
                    "original_task_id": task_snapshot.get("id"),
                    "next_due_date": next_due_date.isoformat(),
                    "correlation_id": correlation_id,
                },
            )
