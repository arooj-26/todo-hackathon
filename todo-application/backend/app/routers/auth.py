"""Authentication router with signup, signin, signout, and user endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.database import get_session
from app.models.user import User
from app.schemas.auth import UserCreate, UserResponse, TokenResponse, SignInRequest
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.auth.middleware import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)



@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Create a new user account.
    """
    logger.info(f"=== SIGNUP STARTED === Email: {user_data.email}")
    logger.info(f"Attempting to sign up new user: {user_data.email}")

    # Check if user already exists
    try:
        logger.debug("Checking for existing user")
        statement = select(User).where(User.email == user_data.email)
        existing_user = session.exec(statement).first()

        if existing_user:
            logger.warning(f"Sign-up failed: email already registered - {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Hash password and create user
        logger.debug("Hashing password")
        password_hash = hash_password(user_data.password)
        
        logger.debug("Creating new user instance")
        new_user = User(
            email=user_data.email,
            password_hash=password_hash
        )

        logger.debug("Adding user to session and committing")
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        logger.info(f"Successfully created new user: {new_user.email} (ID: {new_user.id})")

    except IntegrityError as e:
        logger.warning(f"Integrity error during user creation: {e}")
        session.rollback()
        # Check if it's a duplicate email error
        if "ix_users_email" in str(e) or "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        # Other integrity errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user account."
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error during user creation: {e}", exc_info=True)
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user account."
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during signup: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )

    # Generate access token
    try:
        logger.debug(f"Generating access token for user {new_user.id}")
        access_token = create_access_token(user_id=new_user.id)
        logger.info(f"Access token generated for user {new_user.id}")
    except Exception as e:
        logger.error(f"Error generating access token for user {new_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token."
        )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/signin", response_model=TokenResponse)
async def signin(
    credentials: SignInRequest,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Sign in with email and password.

    Args:
        credentials: User sign-in credentials (email and password)
        session: Database session

    Returns:
        TokenResponse with JWT token and user data

    Raises:
        HTTPException: 401 if credentials are invalid or 500 on server error

    Example:
        POST /auth/signin
        {
            "email": "user@example.com",
            "password": "securepassword123"
        }

        Response:
        {
            "access_token": "eyJhbGci...",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": "user@example.com",
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }
    """
    try:
        # Find user by email
        logger.debug(f"Attempting to sign in user: {credentials.email}")
        statement = select(User).where(User.email == credentials.email)
        user = session.exec(statement).first()

        # Verify user exists and password is correct
        if not user or not verify_password(credentials.password, user.password_hash):
            logger.warning(f"Sign-in failed for user: {credentials.email} - invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        logger.info(f"User signed in successfully: {user.email} (ID: {user.id})")

        # Generate access token
        logger.debug(f"Generating access token for user {user.id}")
        access_token = create_access_token(user_id=user.id)
        logger.info(f"Access token generated for user {user.id}")

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    except HTTPException:
        # Re-raise HTTPException as-is (don't convert to 500)
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during signin for {credentials.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="A database error occurred."
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during signin for {credentials.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout():
    """
    Sign out the current user.

    Note: JWT tokens are stateless, so signout is handled client-side
    by removing the token. This endpoint exists for API consistency
    and to support future server-side token revocation.

    Returns:
        204 No Content

    Example:
        POST /auth/signout
        Authorization: Bearer eyJhbGci...

        Response: 204 No Content
    """
    # In a stateless JWT setup, the client handles token removal
    # This endpoint can be extended to support token blacklisting
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user's information.

    Args:
        current_user: Current authenticated user (from JWT token)

    Returns:
        UserResponse with current user data

    Raises:
        HTTPException: 401 if not authenticated

    Example:
        GET /auth/me
        Authorization: Bearer eyJhbGci...

        Response:
        {
            "id": 1,
            "email": "user@example.com",
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T12:00:00Z"
        }
    """
    return UserResponse.model_validate(current_user)
