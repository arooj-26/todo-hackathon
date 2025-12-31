"""
Database models package.

Exports all models and enums for easy importing.
"""
from enum import Enum


class PriorityEnum(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RoleEnum(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"


# Import models after enums to avoid circular imports
from .task import Task
from .conversation import Conversation
from .message import Message

__all__ = [
    "PriorityEnum",
    "RoleEnum",
    "Task",
    "Conversation",
    "Message",
]
