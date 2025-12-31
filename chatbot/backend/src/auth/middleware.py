"""
Authentication middleware for chatbot endpoints.

Provides dependency injection for authentication.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt import verify_token


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    Extract and verify user ID from JWT token.

    This dependency can be injected into any endpoint that requires authentication.
    It automatically extracts the Bearer token from the Authorization header,
    verifies it, and returns the authenticated user's ID.

    Args:
        credentials: HTTP Authorization credentials (injected by FastAPI)

    Returns:
        Authenticated user's ID (integer)

    Raises:
        HTTPException: If token is missing, invalid, or expired

    Example:
        @app.post("/api/chat")
        async def chat(user_id: int = Depends(get_current_user_id)):
            # user_id is automatically extracted from JWT token
            ...
    """
    token = credentials.credentials
    user_id = verify_token(token)
    return user_id
