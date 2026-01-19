"""Event handlers for audit service."""

import structlog
from datetime import datetime
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.audit_log import AuditLog

logger = structlog.get_logger()


class EventHandler:
    """Handler for processing events and creating audit logs."""

    def __init__(self, session: AsyncSession):
        """Initialize event handler.
        
        Args:
            session: Database session
        """
        self.session = session

    async def handle_event(self, event_data: dict[str, Any]) -> AuditLog:
        """Handle incoming event and create audit log entry.
        
        Args:
            event_data: Event data from Dapr Pub/Sub
            
        Returns:
            Created audit log entry
        """
        # Extract CloudEvents wrapper if present
        if "data" in event_data and isinstance(event_data["data"], dict):
            actual_event = event_data["data"]
        else:
            actual_event = event_data

        event_type = actual_event.get("event_type", "unknown")
        task_id = actual_event.get("task_id")
        user_id = actual_event.get("user_id")
        correlation_id = actual_event.get("correlation_id")
        
        logger.info(
            "Processing event for audit log",
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        # Parse user_id as UUID if it's a string
        if user_id and isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                # If it's an integer string, leave it as string in event_data
                pass
        elif user_id and isinstance(user_id, int):
            # Store integer user_id in event_data, set to None for UUID field
            user_id = None

        # Parse correlation_id
        if correlation_id and isinstance(correlation_id, str):
            try:
                correlation_id = UUID(correlation_id)
            except ValueError:
                # Generate new correlation ID if invalid
                import uuid
                correlation_id = uuid.uuid4()
        else:
            # Generate new correlation ID if missing
            import uuid
            correlation_id = uuid.uuid4()

        # Create audit log entry
        audit_log = AuditLog(
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            event_data=actual_event,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow(),
        )

        self.session.add(audit_log)
        await self.session.commit()
        await self.session.refresh(audit_log)

        logger.info(
            "Audit log created",
            audit_log_id=audit_log.id,
            event_type=event_type,
            task_id=task_id,
        )

        return audit_log
