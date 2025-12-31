"""
JWT token verification for chatbot authentication.

This module verifies JWT tokens issued by the todo-application backend.
IMPORTANT: SECRET_KEY and ALGORITHM must match the todo-application backend.
"""
import os
from jose import jwt, JWTError
from fastapi import HTTPException, status


def verify_token(token: str) -> int:
    """
    Verify JWT token and extract user_id.

    Args:
        token: JWT token string

    Returns:
        User ID from token (integer)

    Raises:
        HTTPException: If token is invalid, expired, or malformed

    Example:
        >>> user_id = verify_token("eyJhbGci...")
        >>> print(user_id)
        1
    """
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    if not SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: SECRET_KEY not set"
        )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")

        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Convert to integer
        return int(user_id_str)

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: malformed user ID",
            headers={"WWW-Authenticate": "Bearer"}
        )
