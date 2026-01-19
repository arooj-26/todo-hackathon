"""Refresh token model for extended user sessions."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class RefreshToken(SQLModel, table=True):
    """Refresh token for extended user sessions.
    
    Refresh tokens allow users to obtain new access tokens without re-authenticating.
    They have longer lifetimes than access tokens and can be revoked.
    """

    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(index=True, description="User ID from Phase-4")
    token_hash: str = Field(
        max_length=256,
        unique=True,
        index=True,
        description="SHA-256 hash of the refresh token"
    )
    expires_at: datetime = Field(
        description="Expiration timestamp (UTC)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC)"
    )
    revoked_at: Optional[datetime] = Field(
        default=None,
        description="Revocation timestamp (UTC), null if active"
    )
    last_used_at: Optional[datetime] = Field(
        default=None,
        description="Last usage timestamp for tracking"
    )
    user_agent: Optional[str] = Field(
        default=None,
        max_length=500,
        description="User agent string from initial request"
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,  # Max length for IPv6
        description="IP address from initial request"
    )

    @staticmethod
    def get_default_expiry() -> datetime:
        """Get default expiration time (30 days from now).
        
        Returns:
            Expiration datetime
        """
        return datetime.utcnow() + timedelta(days=30)

    def is_valid(self) -> bool:
        """Check if refresh token is still valid.
        
        Returns:
            True if token is not expired and not revoked
        """
        now = datetime.utcnow()
        return (
            self.expires_at > now and
            self.revoked_at is None
        )

    def revoke(self) -> None:
        """Revoke this refresh token."""
        self.revoked_at = datetime.utcnow()


class RefreshTokenCreate(SQLModel):
    """Schema for creating a refresh token."""

    user_id: int
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class RefreshTokenResponse(SQLModel):
    """Response schema for refresh token operations."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until access token expires
