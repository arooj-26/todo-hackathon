"""User model with timezone and notification preferences."""

from datetime import datetime
from typing import Optional

from sqlmodel import Column, Field, JSON, SQLModel


class UserBase(SQLModel):
    """Base user fields for create/update operations."""

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


class UserWithPassword(UserBase):
    """User base with password for registration."""

    password_hash: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Hashed password",
    )


class User(UserBase, table=True):
    """User account with timezone and notification settings.

    Note: This model uses integer IDs to match Phase-4 auth backend.
    Users are created in Phase-4, and Phase-5 references them by ID.
    """

    __tablename__ = "users"

    # Use integer ID to match Phase-4 auth backend
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: Optional[str] = Field(default=None, max_length=255)
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

    id: int
    created_at: datetime
    updated_at: datetime
