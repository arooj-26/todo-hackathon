"""Authentication endpoints for signup, signin, signout, and token refresh."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..logging_config import get_logger
from ..models.user import User
from ..auth.password import hash_password, verify_password
from ..auth.jwt_validator import create_access_token
from ..auth.middleware import get_current_user

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


# Request/Response schemas
class SignUpRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    timezone: Optional[str] = "UTC"


class SignInRequest(BaseModel):
    """Request schema for user sign in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema (excludes password)."""
    id: int
    email: str
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Response schema for auth operations."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: SignUpRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Create a new user account.

    Args:
        user_data: User registration data (email, password, timezone)
        session: Database session

    Returns:
        Access token and user data

    Raises:
        HTTPException: 409 if email already exists
    """
    logger.info("Signup requested", email=user_data.email)

    # Check if user already exists
    result = await session.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()

    if existing_user:
        logger.warning("Signup failed: email already registered", email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    try:
        # Hash password and create user
        password_hash = hash_password(user_data.password)

        new_user = User(
            email=user_data.email,
            password_hash=password_hash,
            timezone=user_data.timezone or "UTC",
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        logger.info("User created successfully", user_id=new_user.id, email=new_user.email)

    except IntegrityError as e:
        await session.rollback()
        logger.warning("Integrity error during signup", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    except Exception as e:
        await session.rollback()
        logger.error("Signup error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

    # Generate access token
    access_token = create_access_token(user_id=new_user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    credentials: SignInRequest,
    session: AsyncSession = Depends(get_session),
) -> AuthResponse:
    """Sign in with email and password.

    Args:
        credentials: User credentials (email, password)
        session: Database session

    Returns:
        Access token and user data

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    logger.info("Signin requested", email=credentials.email)

    # Find user by email
    result = await session.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()

    # Verify user exists and password is correct
    if not user or not user.password_hash or not verify_password(credentials.password, user.password_hash):
        logger.warning("Signin failed: invalid credentials", email=credentials.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    logger.info("User signed in successfully", user_id=user.id, email=user.email)

    # Generate access token
    access_token = create_access_token(user_id=user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout():
    """Sign out the current user.

    Note: JWT tokens are stateless, so signout is handled client-side
    by removing the token. This endpoint exists for API consistency.

    Returns:
        204 No Content
    """
    # In a stateless JWT setup, the client handles token removal
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current authenticated user's information.

    Args:
        current_user: Current authenticated user (from JWT token)

    Returns:
        User data

    Raises:
        HTTPException: 401 if not authenticated
    """
    return UserResponse.model_validate(current_user)
