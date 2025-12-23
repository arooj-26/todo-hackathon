"""
Unit tests for Message model.

Tests creation, foreign key relationships, and role enum validation.
Following Test-First Quality - these tests should FAIL until Message model is implemented.
"""
import pytest
from datetime import datetime
from uuid import UUID
from sqlmodel import Session

from src.models.message import Message, RoleEnum
from src.models.conversation import Conversation


class TestMessageModel:
    """Test suite for Message model."""

    def test_message_creation(self, session: Session):
        """Test creating a message."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        # Create conversation first
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Create message
        message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content="Hello, add buy groceries"
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        assert message.id is not None
        assert isinstance(message.id, UUID)
        assert message.conversation_id == conversation.id
        assert message.user_id == user_id
        assert message.role == RoleEnum.USER
        assert message.content == "Hello, add buy groceries"
        assert isinstance(message.created_at, datetime)

    def test_message_role_enum(self, session: Session):
        """Test that role enum accepts valid values."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()

        # Test USER role
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content="User message"
        )
        session.add(user_message)
        session.commit()
        assert user_message.role == RoleEnum.USER

        # Test ASSISTANT role
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.ASSISTANT,
            content="Assistant response"
        )
        session.add(assistant_message)
        session.commit()
        assert assistant_message.role == RoleEnum.ASSISTANT

    def test_message_foreign_key_relationship(self, session: Session):
        """Test that message is linked to conversation via foreign key."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()

        message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content="Test message"
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        assert message.conversation_id == conversation.id

    def test_multiple_messages_per_conversation(self, session: Session):
        """Test that a conversation can have multiple messages."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()

        msg1 = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content="First message"
        )
        msg2 = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.ASSISTANT,
            content="Response"
        )
        msg3 = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content="Follow-up"
        )

        session.add_all([msg1, msg2, msg3])
        session.commit()

        assert msg1.conversation_id == msg2.conversation_id == msg3.conversation_id

    def test_message_timestamps(self, session: Session):
        """Test that created_at timestamp is set."""
        user_id = UUID("550e8400-e29b-41d4-a716-446655440000")

        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()

        before = datetime.utcnow()
        message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=RoleEnum.USER,
            content="Test"
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        after = datetime.utcnow()

        assert before <= message.created_at <= after
