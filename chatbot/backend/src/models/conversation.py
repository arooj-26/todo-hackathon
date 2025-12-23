"""
Conversation model for chat sessions.

Represents a conversation session between a user and the AI assistant.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Owner of the conversation (UUID)
        created_at: Session start timestamp (UTC)
        updated_at: Last message timestamp (UTC)
    """
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
