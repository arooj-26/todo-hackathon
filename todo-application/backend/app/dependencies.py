"""Common FastAPI dependencies."""
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

from app.database import get_session
from app.auth.middleware import get_current_user
from app.models.user import User

# Type aliases for dependency injection
DBSession = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]
