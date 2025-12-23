"""
Unit tests for Conversation model.

Tests creation, relationships, and timestamps.
Following Test-First Quality - these tests should FAIL until Conversation model is implemented.
"""
import pytest
from datetime import datetime
from uuid import UUID
from sqlmodel import Session

from src.models.conversation import Conversation


class TestConversationModel:
    """Test suite for Conversation model."""

    def test_conversation_creation(self, session: Session):
        """Test creating a conversation."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        conversation = Conversation(user_id=user_id)

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert conversation.id is not None
        assert isinstance(conversation.id, UUID)
        assert conversation.user_id == user_id
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_conversation_uuid_generation(self, session: Session):
        """Test that each conversation gets a unique UUID."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        conv1 = Conversation(user_id=user_id)
        conv2 = Conversation(user_id=user_id)

        session.add(conv1)
        session.add(conv2)
        session.commit()

        assert conv1.id != conv2.id
        assert isinstance(conv1.id, UUID)
        assert isinstance(conv2.id, UUID)

    def test_conversation_timestamps(self, session: Session):
        """Test that timestamps are set on creation."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        before = datetime.utcnow()
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        after = datetime.utcnow()

        assert before <= conversation.created_at <= after
        assert before <= conversation.updated_at <= after

    def test_multiple_conversations_per_user(self, session: Session):
        """Test that a user can have multiple conversations."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        conv1 = Conversation(user_id=user_id)
        conv2 = Conversation(user_id=user_id)
        conv3 = Conversation(user_id=user_id)

        session.add_all([conv1, conv2, conv3])
        session.commit()

        assert conv1.user_id == conv2.user_id == conv3.user_id
        assert conv1.id != conv2.id != conv3.id
