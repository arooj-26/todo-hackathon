"""Authentication middleware for Phase-4 JWT token validation."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from ..auth.jwt_validator import verify_token
from ..auth.phase4_client import fetch_user_from_phase4, create_default_user_data
from ..database import get_session
from ..logging_config import get_logger
from ..models.user import User

logger = get_logger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Get current authenticated user from JWT token (issued by Phase-4).

    This validates the JWT token from Phase-4 auth backend and fetches/creates
    the user in Phase-5's database.

    Args:
        credentials: HTTP Bearer token credentials
        session: Database session

    Returns:
        Authenticated User object (Phase-5 representation)

    Raises:
        HTTPException: If token is invalid or user cannot be found/created

    Usage:
        @app.get("/tasks")
        async def get_tasks(current_user: User = Depends(get_current_user)):
            return current_user.id
    """
    token = credentials.credentials

    # Validate JWT token from Phase-4
    token_data = verify_token(token)
    user_id = token_data["user_id"]  # Phase-4's integer user ID

    # Fetch or create user in Phase-5 database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        # User doesn't exist in Phase-5 yet - auto-sync from Phase-4
        logger.info("User not found in Phase-5, syncing from Phase-4", user_id=user_id)

        try:
            # Try to fetch user data from Phase-4
            phase4_user_data = await fetch_user_from_phase4(user_id, token)

            if not phase4_user_data:
                # Phase-4 sync failed, use default user data
                logger.warning(
                    "Phase-4 sync failed, creating user with defaults",
                    user_id=user_id
                )
                phase4_user_data = create_default_user_data(user_id)

            # Create user in Phase-5 database
            user = User(
                id=user_id,
                email=phase4_user_data.get("email", f"user{user_id}@temp.local"),
                timezone=phase4_user_data.get("timezone", "UTC"),
                notification_preferences=phase4_user_data.get("notification_preferences", {})
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            logger.info(
                "User synced successfully from Phase-4",
                user_id=user_id,
                email=user.email
            )

        except Exception as e:
            logger.error(
                "Failed to sync user from Phase-4",
                user_id=user_id,
                error=str(e),
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to synchronize user from Phase-4: {str(e)}",
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
    """
    if current_user.id != requested_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
