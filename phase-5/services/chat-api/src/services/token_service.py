"""Token service for refresh token management and JWT generation."""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..logging_config import get_logger
from ..models.refresh_token import RefreshToken, RefreshTokenCreate
from ..models.user import User

logger = get_logger(__name__)


class TokenService:
    """Service for managing refresh tokens and generating JWTs."""

    def __init__(self, session: AsyncSession):
        """Initialize token service.
        
        Args:
            session: Database session
        """
        self.session = session
        self.jwt_secret = os.getenv("JWT_SECRET")
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable not set")
        
        # Token configuration
        self.access_token_expire_minutes = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        )
        self.refresh_token_expire_days = int(
            os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30")
        )

    async def create_tokens(
        self,
        user_id: int,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> tuple[str, str]:
        """Create access and refresh tokens for a user.
        
        Args:
            user_id: User ID from Phase-4
            user_agent: User agent string
            ip_address: IP address
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        # Generate access token (short-lived JWT)
        access_token = self._generate_access_token(user_id)
        
        # Generate refresh token (long-lived, stored in database)
        refresh_token = self._generate_refresh_token()
        refresh_token_hash = self._hash_token(refresh_token)
        
        # Store refresh token in database
        db_refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=refresh_token_hash,
            expires_at=datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        
        self.session.add(db_refresh_token)
        await self.session.commit()
        
        logger.info(
            "Created token pair",
            user_id=user_id,
            refresh_token_id=str(db_refresh_token.id),
        )
        
        return access_token, refresh_token

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> tuple[str, str]:
        """Refresh access token using a refresh token.
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            Tuple of (new_access_token, new_refresh_token)
            
        Raises:
            ValueError: If refresh token is invalid, expired, or revoked
        """
        # Hash the provided token
        token_hash = self._hash_token(refresh_token)
        
        # Look up refresh token in database
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            logger.warning("Refresh token not found")
            raise ValueError("Invalid refresh token")
        
        # Check if token is valid
        if not db_token.is_valid():
            logger.warning(
                "Refresh token invalid or revoked",
                token_id=str(db_token.id),
                expired=db_token.expires_at < datetime.utcnow(),
                revoked=db_token.revoked_at is not None,
            )
            raise ValueError("Refresh token expired or revoked")
        
        # Update last used timestamp
        db_token.last_used_at = datetime.utcnow()
        await self.session.commit()
        
        # Revoke old refresh token (rotation)
        db_token.revoke()
        await self.session.commit()
        
        logger.info(
            "Rotating refresh token",
            user_id=db_token.user_id,
            old_token_id=str(db_token.id),
        )
        
        # Generate new token pair
        new_access_token, new_refresh_token = await self.create_tokens(
            user_id=db_token.user_id,
            user_agent=db_token.user_agent,
            ip_address=db_token.ip_address,
        )
        
        return new_access_token, new_refresh_token

    async def revoke_refresh_token(
        self,
        refresh_token: str,
    ) -> bool:
        """Revoke a refresh token.
        
        Args:
            refresh_token: Refresh token to revoke
            
        Returns:
            True if token was revoked, False if not found
        """
        token_hash = self._hash_token(refresh_token)
        
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            )
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            return False
        
        db_token.revoke()
        await self.session.commit()
        
        logger.info(
            "Revoked refresh token",
            token_id=str(db_token.id),
            user_id=db_token.user_id,
        )
        
        return True

    async def revoke_all_user_tokens(
        self,
        user_id: int,
    ) -> int:
        """Revoke all refresh tokens for a user.
        
        Useful for logout-all-devices functionality.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of tokens revoked
        """
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.revoke()
            count += 1
        
        await self.session.commit()
        
        logger.info(
            "Revoked all user tokens",
            user_id=user_id,
            count=count,
        )
        
        return count

    def _generate_access_token(self, user_id: int) -> str:
        """Generate JWT access token.
        
        Args:
            user_id: User ID
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user_id),
            "iat": now.timestamp(),
            "exp": expire.timestamp(),
            "type": "access",
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token

    def _generate_refresh_token(self) -> str:
        """Generate cryptographically secure random refresh token.
        
        Returns:
            Random token string (URL-safe)
        """
        # Generate 32 bytes of random data -> 43 character base64 string
        return secrets.token_urlsafe(32)

    def _hash_token(self, token: str) -> str:
        """Hash a token for storage.
        
        Args:
            token: Token to hash
            
        Returns:
            SHA-256 hash of token
        """
        return hashlib.sha256(token.encode()).hexdigest()
