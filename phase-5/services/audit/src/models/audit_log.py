"""Audit log model for event tracking and compliance."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Column, Field, JSON, SQLModel


class AuditLog(SQLModel, table=True):
    """Immutable audit log entry for all task operations."""

    __tablename__ = "audit_logs"

    id: int = Field(default=None, primary_key=True)
    event_type: str = Field(
        max_length=50,
        description="Event type (created, updated, completed, deleted, reminder_sent)",
    )
    task_id: Optional[int] = Field(default=None, description="Related task ID")
    user_id: Optional[UUID] = Field(default=None, description="User who triggered the event")
    event_data: dict = Field(
        sa_column=Column(JSON), description="Complete event data (JSON)"
    )
    correlation_id: UUID = Field(description="Distributed tracing correlation ID")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Event timestamp (UTC)"
    )


class AuditLogResponse(SQLModel):
    """Audit log response schema."""

    id: int
    event_type: str
    task_id: Optional[int]
    user_id: Optional[UUID]
    event_data: dict
    correlation_id: UUID
    timestamp: datetime


class AuditLogListResponse(SQLModel):
    """Paginated audit log list response."""

    logs: list[AuditLogResponse]
    total: int
    limit: int
    offset: int
