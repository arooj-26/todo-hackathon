# Backend Development Guide

This file contains backend-specific guidance for the Todo Application API built with FastAPI.

## Technology Stack

- **Framework**: FastAPI 0.109+
- **Language**: Python 3.11+
- **ORM**: SQLModel 0.0.14 (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (Neon Serverless)
- **Migrations**: Alembic 1.13+
- **Authentication**: python-jose (JWT tokens)
- **Password Hashing**: passlib with bcrypt
- **Testing**: pytest + httpx
- **Server**: Uvicorn with hot reload

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Settings and configuration
│   ├── database.py          # Database connection and session management
│   ├── dependencies.py      # Dependency injection (auth, db sessions)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py         # User SQLModel
│   │   └── task.py         # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py         # Auth request/response schemas
│   │   ├── user.py         # User schemas
│   │   └── task.py         # Task schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py         # /auth endpoints (signup, signin, signout, me)
│   │   └── tasks.py        # /api/{user_id}/tasks endpoints
│   └── auth/
│       ├── __init__.py
│       ├── jwt.py          # JWT token creation and validation
│       ├── password.py     # Password hashing and verification
│       └── middleware.py   # Authentication middleware
├── alembic/
│   ├── versions/           # Migration files
│   └── env.py             # Alembic configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   ├── test_auth.py       # Auth endpoint tests
│   └── test_tasks.py      # Task endpoint tests
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
└── CLAUDE.md              # This file
```

## FastAPI Patterns

### Application Setup (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, tasks

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix=settings.API_PREFIX, tags=["Tasks"])
```

### Router Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.dependencies import get_current_user, get_session
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter()

@router.post("/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: int,
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Authorization check
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Business logic
    task = Task(**task_data.dict(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## SQLModel Patterns

### Model Definition

```python
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)
```

### Database Session Management

```python
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_size=10,
    max_overflow=20
)

def get_session():
    """Dependency for database sessions."""
    with Session(engine) as session:
        yield session

def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)
```

## Authentication Patterns

### JWT Token Creation

```python
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> int:
    """Verify JWT token and return user_id."""
    from jose import JWTError
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Password Hashing

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.auth.jwt import verify_token
from app.dependencies import get_session
from app.models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    user_id = verify_token(token)

    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

## API Error Handling

### Standard Error Responses

```python
from fastapi import HTTPException, status

# 400 Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input data"
)

# 401 Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"}
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not authorized to access this resource"
)

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found"
)

# 409 Conflict
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Resource already exists"
)
```

## Testing Patterns

### Test Setup (conftest.py)

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app.main import app
from app.dependencies import get_session

@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with dependency override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Test Example

```python
def test_create_task_success(client: TestClient, session: Session):
    """Test successful task creation."""
    # Create user and get token
    signup_data = {"email": "test@example.com", "password": "password123"}
    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == 201
    token = response.json()["access_token"]
    user_id = response.json()["user"]["id"]

    # Create task
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {"description": "Test task"}
    response = client.post(f"/api/{user_id}/tasks", json=task_data, headers=headers)

    assert response.status_code == 201
    assert response.json()["description"] == "Test task"
    assert response.json()["completed"] is False
```

## Configuration Management

### Settings Pattern (config.py)

```python
from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    # CORS
    ALLOWED_ORIGINS: List[str] = []

    # Application
    PROJECT_NAME: str = "Todo API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from string if needed."""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return json.loads(self.ALLOWED_ORIGINS)
        return self.ALLOWED_ORIGINS

settings = Settings()
```

## Alembic Migrations

### Create Migration

```bash
# Auto-generate migration from SQLModel changes
alembic revision --autogenerate -m "Add users and tasks tables"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration File Pattern

```python
"""Add users and tasks tables

Revision ID: xxxxx
Create Date: 2025-01-01
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
```

## Best Practices

### 1. Dependency Injection
- Use FastAPI's `Depends()` for database sessions, authentication, and shared logic
- Keep dependencies in `app/dependencies.py` for reusability

### 2. Schema Separation
- Models (SQLModel): Database representation with relationships
- Schemas (Pydantic): API request/response validation
- Keep them separate even when similar

### 3. Error Handling
- Always use appropriate HTTP status codes
- Provide clear, actionable error messages
- Never expose internal errors or stack traces in production

### 4. Security
- Never log or expose passwords, tokens, or sensitive data
- Always hash passwords with bcrypt (via passlib)
- Validate JWT tokens on every protected endpoint
- Use HTTPS in production

### 5. Testing
- Test all endpoints with both success and failure cases
- Use in-memory SQLite for fast tests
- Test authentication and authorization separately
- Aim for >80% code coverage

### 6. Database
- Use connection pooling for performance
- Always use migrations (Alembic) for schema changes
- Add indexes on frequently queried columns
- Use transactions for multi-step operations

### 7. Code Organization
- One router per resource (auth, tasks, etc.)
- Keep business logic in service layer (if needed)
- Keep routes thin - delegate to services
- Use type hints everywhere

## Common Pitfalls to Avoid

1. **Don't commit .env files** - Use .env.example as template
2. **Don't use synchronous I/O** - FastAPI is async-first
3. **Don't skip input validation** - Use Pydantic schemas
4. **Don't forget CORS** - Required for frontend communication
5. **Don't hardcode secrets** - Use environment variables
6. **Don't expose user_id in tokens without validation** - Always verify authorization
7. **Don't return password_hash in responses** - Exclude sensitive fields

## Performance Considerations

- Use connection pooling (pool_size=10, max_overflow=20)
- Add database indexes on foreign keys and frequently queried fields
- Use `select` statements with filters instead of loading all records
- Consider pagination for list endpoints (limit/offset)
- Use async endpoints when doing I/O operations

## Documentation

FastAPI auto-generates OpenAPI documentation:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

Ensure all endpoints have:
- Clear docstrings
- Proper response_model definitions
- Status code specifications
- Example request/response bodies
