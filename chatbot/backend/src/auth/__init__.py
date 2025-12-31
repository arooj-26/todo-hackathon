"""
Authentication module for chatbot backend.

Provides JWT token verification compatible with todo-application backend.
"""
from .jwt import verify_token
from .middleware import get_current_user_id

__all__ = ["verify_token", "get_current_user_id"]
