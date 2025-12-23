"""
Message model for conversation messages.

Represents individual messages within a conversation.
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime
from uuid import UUID, uuid4

from . import RoleEnum


class Message(SQLModel, table=True):
    """
    Message model representing a message in a conversation.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Parent conversation (UUID, foreign key)
        user_id: Owner of the message (UUID, for data isolation)
        role: Message author ('user' or 'assistant')
        content: Message text content
        created_at: Message timestamp (UTC)
    """
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: UUID = Field(index=True, nullable=False)
    role: RoleEnum = Field(
        sa_column=Column(SQLEnum(RoleEnum), nullable=False)
    )
    content: str = Field(nullable=False, max_length=50000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    class Config:
        arbitrary_types_allowed = True
