"""JWT token validation and creation for Phase-4 auth integration."""
import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status


def get_jwt_secret() -> str:
    """Get JWT secret from environment."""
    # IMPORTANT: Must match the SECRET_KEY used by Phase-4 auth backend
    # Both backends must use the same secret to validate tokens
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise ValueError("JWT_SECRET environment variable not set")
    return secret


def create_access_token(user_id: int, expires_hours: int = 24) -> str:
    """Create JWT access token.

    Args:
        user_id: User ID to encode in token
        expires_hours: Token validity in hours (default 24)

    Returns:
        JWT token string
    """
    secret = get_jwt_secret()
    expire = datetime.utcnow() + timedelta(hours=expires_hours)

    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }

    return jwt.encode(to_encode, secret, algorithm="HS256")


def verify_token(token: str) -> dict:
    """
    Verify JWT token from Phase-4 auth backend.

    Args:
        token: JWT token string

    Returns:
        Dictionary with user_id and email from token payload

    Raises:
        HTTPException: If token is invalid or expired

    Note:
        Phase-4 creates tokens with 'sub' field containing user_id (integer).
        Phase-5 will use the email to find/create its own User record with UUID.
    """
    try:
        secret = get_jwt_secret()
        # Decode token (validates signature and expiration)
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Phase-4 stores integer user_id in 'sub'
        # We return it for logging/debugging, but Phase-5 will use email
        return {
            "user_id": int(user_id_str),  # Phase-4's integer user ID
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token format: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )
