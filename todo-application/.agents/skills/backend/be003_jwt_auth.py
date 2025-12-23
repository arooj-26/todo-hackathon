"""
Skill BE-003: Implement JWT Authentication

Implements JWT token generation, validation, and authentication dependencies.
"""

from pathlib import Path
from typing import List
from ...lib.skill_base import (
    Skill,
    SkillMetadata,
    SkillInput,
    SkillOutput,
    SkillStatus,
    register_skill
)


@register_skill
class ImplementJWTAuthSkill(Skill):
    """Implement JWT authentication."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="BE-003",
            name="Implement JWT Authentication",
            description="Implement JWT token generation, validation, and authentication dependencies",
            category="backend",
            version="1.0.0",
            dependencies=["BE-001"],
            inputs_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "security_module_path": {"type": "string"},
                    "dependencies_path": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        backend_path = Path("backend")
        if not backend_path.exists():
            return False, "Backend directory does not exist. Run BE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        try:
            backend_path = Path("backend")
            core_path = backend_path / "app" / "core"

            # Create security.py
            security_path = core_path / "security.py"
            security_code = """from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/signin")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    \"\"\"Verify a password against a hash.\"\"\"
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    \"\"\"Hash a password.\"\"\"
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    \"\"\"
    Create a JWT access token.

    Args:
        data: Data to encode in the token
        expires_delta: Token expiration time (defaults to ACCESS_TOKEN_EXPIRE_HOURS)

    Returns:
        Encoded JWT token
    \"\"\"
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    \"\"\"
    Decode and validate a JWT access token.

    Args:
        token: JWT token to decode

    Returns:
        Decoded token data or None if invalid
    \"\"\"
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    \"\"\"
    Get the current authenticated user from JWT token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    \"\"\"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user email from token
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    # Get user from database
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()

    if user is None:
        raise credentials_exception

    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    \"\"\"
    Authenticate a user with email and password.

    Args:
        db: Database session
        email: User email
        password: Plain text password

    Returns:
        User if authentication successful, None otherwise
    \"\"\"
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
"""

            security_path.write_text(security_code, encoding="utf-8")
            self.logger.info(f"Created security module: {security_path}")

            # Create dependencies.py
            dependencies_path = core_path / "dependencies.py"
            dependencies_code = """from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.user import User

# Dependency annotations for common use
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
"""

            dependencies_path.write_text(dependencies_code, encoding="utf-8")
            self.logger.info(f"Created dependencies: {dependencies_path}")

            artifacts = [str(security_path), str(dependencies_path)]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "security_module_path": str(security_path),
                    "dependencies_path": str(dependencies_path)
                },
                artifacts=artifacts,
                logs=[f"Created JWT authentication with {len(artifacts)} files"]
            )

        except Exception as e:
            self.logger.exception("Failed to implement JWT authentication")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "Password hashing with bcrypt implemented",
            "JWT token creation with expiration",
            "JWT token validation and decoding",
            "get_current_user dependency extracts user from token",
            "authenticate_user verifies credentials",
            "OAuth2PasswordBearer scheme configured",
            "Proper error handling for invalid tokens",
            "Token includes 'sub' claim with user email"
        ]
