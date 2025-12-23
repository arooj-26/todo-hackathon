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


__all__ = [
    "PriorityEnum",
    "RoleEnum",
]
