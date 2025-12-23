"""User model."""
from datetime import datetime
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    User model for authentication and task ownership.

    Attributes:
        id: Primary key, auto-incremented
        email: Unique email address for authentication
        password_hash: Hashed password (never store plain text)
        created_at: Timestamp of account creation
        updated_at: Timestamp of last update
    """

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
