"""Authentication middleware and dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.auth.jwt import verify_token
from app.database import get_session
from app.models.user import User

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user from JWT token.

    This is a FastAPI dependency that extracts and validates the JWT token
    from the Authorization header, then fetches the user from the database.

    Args:
        credentials: HTTP Bearer token credentials
        session: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: If token is invalid or user not found

    Usage:
        @app.get("/api/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user

    Example:
        >>> # In a request with header: Authorization: Bearer eyJhbGci...
        >>> user = await get_current_user(credentials, session)
        >>> print(user.email)
        'user@example.com'
    """
    token = credentials.credentials
    user_id = verify_token(token)

    # Fetch user from database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def verify_user_authorization(current_user: User, requested_user_id: int) -> None:
    """
    Verify that the current user is authorized to access resources for the requested user ID.

    Args:
        current_user: Currently authenticated user
        requested_user_id: User ID being accessed in the request

    Raises:
        HTTPException: If user is not authorized (403 Forbidden)

    Usage:
        @app.get("/api/{user_id}/tasks")
        async def get_tasks(
            user_id: int,
            current_user: User = Depends(get_current_user)
        ):
            verify_user_authorization(current_user, user_id)
            # ... fetch tasks

    Example:
        >>> user = User(id=1, email="user@example.com")
        >>> verify_user_authorization(user, 1)  # No error
        >>> verify_user_authorization(user, 2)  # Raises HTTPException
    """
    if current_user.id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
