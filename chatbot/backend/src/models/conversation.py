"""
Conversation model for chat sessions.

Represents a conversation session between a user and the AI assistant.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session.

    Attributes:
        id: Primary key, auto-incremented
        user_id: User ID of the conversation owner
        created_at: Timestamp of conversation creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(nullable=False, index=True)  # Use integer user_id to match todo app
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
