"""User model with timezone and notification preferences."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Column, Field, JSON, SQLModel


class UserBase(SQLModel):
    """Base user fields for create/update operations."""

    username: str = Field(
        min_length=3,
        max_length=50,
        regex=r"^[a-zA-Z0-9_-]{3,50}$",
        description="Username (3-50 alphanumeric characters, underscores, hyphens)",
    )
    email: str = Field(
        max_length=255,
        regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        description="Email address",
    )
    timezone: str = Field(
        default="UTC",
        max_length=50,
        description="IANA timezone (e.g., America/New_York)",
    )
    notification_preferences: dict = Field(
        default={"email": True, "push": False, "in_app": True},
        sa_column=Column(JSON),
        description="Notification channel preferences",
    )


class User(UserBase, table=True):
    """User account with timezone and notification settings."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    """User creation schema."""

    pass


class UserUpdate(SQLModel):
    """User update schema (all fields optional)."""

    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[str] = Field(default=None, max_length=255)
    timezone: Optional[str] = Field(default=None, max_length=50)
    notification_preferences: Optional[dict] = None


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime
