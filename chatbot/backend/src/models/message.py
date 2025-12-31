"""
Message model for conversation messages.

Represents individual messages within a conversation.
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from uuid import UUID

from . import RoleEnum


class Message(SQLModel, table=True):
    """
    Message model representing a message in a conversation.

    Attributes:
        id: Unique message identifier (integer)
        conversation_id: Parent conversation (integer, foreign key)
        user_id: Owner of the message (string, for data isolation)
        role: Message author ('user' or 'assistant')
        content: Message text content
        created_at: Message timestamp (UTC)
    """
    __tablename__ = "messages"

    id: int = Field(default=None, primary_key=True, nullable=False)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: int = Field(index=True, nullable=False)  # Integer to match todo app
    role: RoleEnum = Field(
        sa_column=Column(SQLEnum(RoleEnum), nullable=False)
    )
    content: str = Field(nullable=False, max_length=50000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        arbitrary_types_allowed = True
