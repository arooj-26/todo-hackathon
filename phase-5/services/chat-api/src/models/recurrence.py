"""Recurrence pattern model for repeating tasks."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class PatternType(str, Enum):
    """Recurrence pattern type."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class EndCondition(str, Enum):
    """Recurrence end condition."""

    NEVER = "never"
    AFTER_OCCURRENCES = "after_occurrences"
    BY_DATE = "by_date"


class RecurrencePatternBase(SQLModel):
    """Base recurrence pattern fields."""

    pattern_type: PatternType = Field(description="Type of recurrence pattern")
    interval: int = Field(
        default=1, ge=1, le=365, description="Repeat every N days/weeks/months"
    )
    days_of_week: Optional[list[int]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Days of week for weekly pattern (0=Monday, 6=Sunday)",
    )
    day_of_month: Optional[int] = Field(
        default=None, ge=1, le=31, description="Day of month for monthly pattern"
    )
    end_condition: EndCondition = Field(description="When to stop creating instances")
    occurrence_count: Optional[int] = Field(
        default=None,
        ge=1,
        le=365,
        description="Max occurrences (for after_occurrences)",
    )
    end_date: Optional[datetime] = Field(
        default=None, description="End date (for by_date)"
    )


class RecurrencePattern(RecurrencePatternBase, table=True):
    """Recurrence pattern entity."""

    __tablename__ = "recurrence_patterns"

    id: int = Field(default=None, primary_key=True)
    task_id: int = Field(unique=True, foreign_key="tasks.id")
    current_occurrence: int = Field(
        default=0, description="Number of instances created so far"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RecurrencePatternCreate(RecurrencePatternBase):
    """Recurrence pattern creation schema."""

    pass


class RecurrencePatternResponse(RecurrencePatternBase):
    """Recurrence pattern response schema."""

    id: int
    task_id: int
    current_occurrence: int
    created_at: datetime
    updated_at: datetime
