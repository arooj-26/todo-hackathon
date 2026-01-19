"""Client for fetching user data from Phase-4 auth backend."""

import os
from typing import Optional, Dict, Any

import httpx
from ..logging_config import get_logger

logger = get_logger(__name__)

# Phase-4 auth backend URL
PHASE4_AUTH_URL = os.getenv("PHASE4_AUTH_URL", "http://todo-app-backend:8000")


async def fetch_user_from_phase4(user_id: int, token: str) -> Optional[Dict[str, Any]]:
    """
    Fetch user details from Phase-4 auth backend.

    Args:
        user_id: User ID to fetch
        token: JWT token for authentication

    Returns:
        User data dict with email, timezone, etc., or None if not found

    Raises:
        httpx.HTTPError: If API call fails
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Try Phase-4 /auth/me endpoint first
            response = await client.get(
                f"{PHASE4_AUTH_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                user_data = response.json()
                logger.info(
                    "Fetched user from Phase-4",
                    user_id=user_id,
                    email=user_data.get("email")
                )
                return user_data

            # If /auth/me doesn't exist, try /users/{id} endpoint
            response = await client.get(
                f"{PHASE4_AUTH_URL}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                user_data = response.json()
                logger.info(
                    "Fetched user from Phase-4 /users endpoint",
                    user_id=user_id,
                    email=user_data.get("email")
                )
                return user_data

            logger.warning(
                "Could not fetch user from Phase-4",
                user_id=user_id,
                status_code=response.status_code
            )
            return None

    except httpx.TimeoutException:
        logger.error("Timeout fetching user from Phase-4", user_id=user_id)
        # Return None to fall back to default user creation
        return None

    except httpx.HTTPError as e:
        logger.error(
            "Error fetching user from Phase-4",
            user_id=user_id,
            error=str(e)
        )
        # Return None to fall back to default user creation
        return None


def create_default_user_data(user_id: int) -> Dict[str, Any]:
    """
    Create default user data when Phase-4 sync fails.

    Args:
        user_id: User ID

    Returns:
        Default user data dict
    """
    return {
        "id": user_id,
        "email": f"user{user_id}@temp.local",  # Temporary email
        "timezone": "UTC",  # Default timezone
    }
