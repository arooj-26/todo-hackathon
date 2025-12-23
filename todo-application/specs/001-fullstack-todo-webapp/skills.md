# Skills: Todo Full-Stack Web Application

**Feature**: 001-fullstack-todo-webapp
**Date**: 2025-12-17
**Purpose**: Define reusable, atomic skills for agent-based development

## Overview

Skills are discrete, reusable capabilities that agents can execute to accomplish specific tasks. Each skill is atomic (does one thing well), composable (can be combined with other skills), and well-defined (clear inputs, outputs, and success criteria).

### Skill Categories

1. **Frontend Development** - Next.js, React, UI components
2. **Backend Development** - FastAPI, API endpoints, business logic
3. **Database Management** - Schema, migrations, data operations
4. **Authentication & Security** - JWT, auth flows, authorization
5. **Testing & Validation** - Unit tests, integration tests, E2E tests
6. **Documentation** - Specs, API docs, guides
7. **DevOps & Deployment** - Docker, environment setup, CI/CD

---

## Frontend Developer Skills

### FE-001: Initialize Next.js Project

**Description**: Create a new Next.js 16+ application with App Router and TypeScript configuration.

**Inputs**:
- `project_name` (string): Name of the project
- `use_typescript` (boolean): Enable TypeScript (default: true)
- `use_tailwind` (boolean): Enable TailwindCSS (default: true)
- `use_app_router` (boolean): Use App Router (default: true)

**Outputs**:
- Next.js project initialized in `frontend/` directory
- package.json with dependencies
- tsconfig.json configured
- Basic folder structure created

**Dependencies**:
- Node.js 18+
- npm 9+

**Implementation**:
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
npm install
```

**Success Criteria**:
- [x] Project created in frontend/ directory
- [x] package.json contains Next.js 16+
- [x] TypeScript configuration present
- [x] App Router structure (app/ directory)
- [x] npm install completes successfully

---

### FE-002: Create React Component

**Description**: Generate a new React component with TypeScript types and proper file structure.

**Inputs**:
- `component_name` (string): Name of component (PascalCase)
- `component_type` (enum): 'page' | 'component' | 'layout'
- `props_interface` (object): TypeScript interface definition
- `has_state` (boolean): Include useState hooks

**Outputs**:
- Component file created at appropriate path
- TypeScript types defined
- Basic structure with props

**Example**:
```typescript
// Input: TaskList component
// Output: frontend/components/TaskList.tsx

import React from 'react'

interface TaskListProps {
  tasks: Task[]
  onTaskClick: (taskId: number) => void
}

export default function TaskList({ tasks, onTaskClick }: TaskListProps) {
  return (
    <div className="task-list">
      {tasks.map(task => (
        <div key={task.id} onClick={() => onTaskClick(task.id)}>
          {task.description}
        </div>
      ))}
    </div>
  )
}
```

**Success Criteria**:
- [x] Component file created with proper naming
- [x] TypeScript interface defined for props
- [x] Component exports properly
- [x] No TypeScript errors

---

### FE-003: Implement Better Auth

**Description**: Configure Better Auth for JWT-based authentication in Next.js application.

**Inputs**:
- `auth_config` (object): Better Auth configuration
- `jwt_secret` (string): JWT secret key
- `session_duration` (string): Token expiration time

**Outputs**:
- Better Auth configured in frontend/lib/auth.ts
- API routes created in app/api/auth/
- Auth types exported

**Implementation**:
```typescript
// frontend/lib/auth.ts
import { createAuth } from 'better-auth'

export const auth = createAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  session: {
    cookieOptions: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax'
    }
  },
  jwt: {
    expiresIn: '24h'
  }
})
```

**Dependencies**:
- better-auth package
- Environment variables configured

**Success Criteria**:
- [x] Better Auth installed and configured
- [x] Auth API routes created
- [x] JWT tokens generated on signin
- [x] Tokens stored in httpOnly cookies

---

### FE-004: Create API Client

**Description**: Set up Axios-based API client with JWT token injection and error handling.

**Inputs**:
- `api_base_url` (string): Backend API URL
- `timeout` (number): Request timeout in milliseconds

**Outputs**:
- API client configured in frontend/lib/api.ts
- Request interceptor for JWT injection
- Response interceptor for error handling
- Typed API functions exported

**Implementation**:
```typescript
// frontend/lib/api.ts
import axios from 'axios'
import { getCookie } from 'cookies-next'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 10000
})

// Request interceptor: Add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const token = getCookie('better-auth.session')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/signin'
    }
    return Promise.reject(error)
  }
)

// Typed API functions
export const tasksApi = {
  list: (userId: number) => apiClient.get(`/api/${userId}/tasks`),
  create: (userId: number, description: string) =>
    apiClient.post(`/api/${userId}/tasks`, { description }),
  // ... other methods
}
```

**Success Criteria**:
- [x] Axios client configured with base URL
- [x] JWT token automatically added to requests
- [x] 401 errors redirect to signin
- [x] TypeScript types for API responses

---

### FE-005: Implement Route Protection

**Description**: Create Next.js middleware to protect routes and enforce authentication.

**Inputs**:
- `protected_routes` (array): List of routes requiring auth
- `public_routes` (array): List of routes accessible without auth

**Outputs**:
- middleware.ts created at app root
- Route protection logic implemented
- Redirect logic for unauthenticated users

**Implementation**:
```typescript
// frontend/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('better-auth.session')
  const { pathname } = request.nextUrl

  const publicRoutes = ['/signin', '/signup']

  if (publicRoutes.includes(pathname)) {
    if (token) {
      return NextResponse.redirect(new URL('/', request.url))
    }
    return NextResponse.next()
  }

  if (!token) {
    return NextResponse.redirect(new URL('/signin', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/', '/tasks/:path*', '/signin', '/signup']
}
```

**Success Criteria**:
- [x] Middleware protects specified routes
- [x] Unauthenticated users redirected to signin
- [x] Authenticated users can access protected routes
- [x] Auth page redirects logged-in users

---

### FE-006: Style with TailwindCSS

**Description**: Apply TailwindCSS utility classes for responsive, consistent styling.

**Inputs**:
- `component` (string): Component file path
- `design_spec` (object): Design specifications (colors, spacing, typography)

**Outputs**:
- Component styled with Tailwind classes
- Responsive design implemented
- Consistent with design system

**Example**:
```typescript
// Task item with Tailwind styling
export default function TaskItem({ task }: TaskItemProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center space-x-3">
        <input
          type="checkbox"
          checked={task.completed}
          className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
        />
        <span className={`text-gray-800 ${task.completed ? 'line-through text-gray-400' : ''}`}>
          {task.description}
        </span>
      </div>
      <button className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded">
        Delete
      </button>
    </div>
  )
}
```

**Success Criteria**:
- [x] Tailwind classes applied correctly
- [x] Responsive design (mobile-first)
- [x] Hover and focus states defined
- [x] Consistent spacing and colors

---

## Backend Developer Skills

### BE-001: Initialize FastAPI Project

**Description**: Create a new FastAPI project with proper structure and dependencies.

**Inputs**:
- `project_name` (string): Name of the project
- `use_sqlmodel` (boolean): Include SQLModel ORM
- `use_alembic` (boolean): Include Alembic migrations

**Outputs**:
- FastAPI project structure in backend/
- requirements.txt with dependencies
- main.py with FastAPI app
- Basic folder structure

**Implementation**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
alembic==1.12.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
httpx==0.25.2
pytest==7.4.3
EOF

pip install -r requirements.txt

# Create basic structure
mkdir -p routers auth tests
touch main.py models.py database.py config.py schemas.py dependencies.py
```

**Success Criteria**:
- [x] Virtual environment created
- [x] Dependencies installed
- [x] Project structure matches plan
- [x] main.py runs without errors

---

### BE-002: Define API Endpoint

**Description**: Create a FastAPI route handler with request/response schemas and business logic.

**Inputs**:
- `endpoint_path` (string): URL path for endpoint
- `http_method` (enum): 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
- `request_schema` (object): Pydantic model for request body
- `response_schema` (object): Pydantic model for response
- `requires_auth` (boolean): Endpoint requires authentication

**Outputs**:
- Route handler created in appropriate router file
- Request validation with Pydantic
- Response serialization
- Error handling

**Example**:
```python
# backend/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from models import Task
from schemas import TaskCreate, TaskResponse
from database import get_session
from dependencies import get_current_user

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    user_id: int,
    task: TaskCreate,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    # Verify authorization
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create task
    db_task = Task(user_id=user_id, description=task.description)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return db_task

@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    user_id: int,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    # Verify authorization
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Query tasks
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()

    return tasks
```

**Success Criteria**:
- [x] Endpoint responds to correct HTTP method and path
- [x] Request validation with Pydantic
- [x] Authorization check performed
- [x] Database operations correct
- [x] Proper HTTP status codes returned

---

### BE-003: Implement JWT Authentication

**Description**: Set up JWT token generation, validation, and middleware for FastAPI.

**Inputs**:
- `secret_key` (string): JWT signing secret
- `algorithm` (string): JWT algorithm (default: HS256)
- `token_expiration` (string): Token expiration time

**Outputs**:
- JWT utilities in backend/auth/jwt.py
- Authentication middleware
- FastAPI dependency for current user extraction

**Implementation**:
```python
# backend/auth/jwt.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# backend/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwt import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return user_id
```

**Success Criteria**:
- [x] JWT tokens generated with correct claims
- [x] Token validation works correctly
- [x] Expired tokens rejected
- [x] Invalid tokens rejected
- [x] User ID extracted from valid tokens

---

### BE-004: Configure CORS

**Description**: Set up CORS middleware to allow frontend-backend communication.

**Inputs**:
- `allowed_origins` (array): List of allowed origin URLs
- `allow_credentials` (boolean): Allow cookies/auth headers

**Outputs**:
- CORS middleware configured in main.py
- Preflight requests handled

**Implementation**:
```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Todo API", version="1.0.0")

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**Success Criteria**:
- [x] Frontend can make requests to backend
- [x] Preflight OPTIONS requests handled
- [x] Credentials (cookies) allowed
- [x] No CORS errors in browser console

---

### BE-005: Implement User-Scoped Data Access

**Description**: Ensure all database queries filter by authenticated user ID.

**Inputs**:
- `model` (class): SQLModel model class
- `user_id` (int): Authenticated user's ID
- `operation` (enum): 'list' | 'get' | 'create' | 'update' | 'delete'

**Outputs**:
- Query filtered by user_id
- Authorization check performed
- 403 error if unauthorized

**Example**:
```python
# List user's tasks (always filtered)
statement = select(Task).where(Task.user_id == current_user_id)
tasks = session.exec(statement).all()

# Get specific task (verify ownership)
task = session.get(Task, task_id)
if task is None or task.user_id != current_user_id:
    raise HTTPException(status_code=404, detail="Task not found")

# Update task (verify ownership first)
task = session.get(Task, task_id)
if task.user_id != current_user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
task.description = new_description
session.add(task)
session.commit()
```

**Success Criteria**:
- [x] All queries include user_id filter
- [x] Ownership verified before updates/deletes
- [x] 403 returned for unauthorized access
- [x] Users cannot see other users' data

---

## Database Administrator Skills

### DB-001: Define Database Schema

**Description**: Create SQLModel models matching the data model specification.

**Inputs**:
- `entities` (array): List of entities from data model
- `relationships` (array): Relationships between entities

**Outputs**:
- SQLModel models in backend/models.py
- Foreign keys configured
- Indexes defined

**Implementation**:
```python
# backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    description: str = Field(nullable=False, min_length=1, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")
```

**Success Criteria**:
- [x] Models match data model specification
- [x] Foreign keys properly defined
- [x] Indexes on performance-critical columns
- [x] Validation rules applied

---

### DB-002: Connect to Neon Database

**Description**: Establish connection to Neon Serverless PostgreSQL with connection pooling.

**Inputs**:
- `database_url` (string): PostgreSQL connection string
- `pool_size` (int): Number of connections in pool
- `max_overflow` (int): Additional connections under load

**Outputs**:
- Database engine configured in backend/database.py
- Connection pool established
- Session dependency created

**Implementation**:
```python
# backend/database.py
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pool
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True,
)

def init_db():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

**Success Criteria**:
- [x] Connection to Neon database successful
- [x] Connection pool configured
- [x] Sessions work with dependency injection
- [x] Tables can be created

---

### DB-003: Create Database Migration

**Description**: Generate Alembic migration for schema changes.

**Inputs**:
- `migration_message` (string): Description of changes
- `auto_generate` (boolean): Auto-detect model changes

**Outputs**:
- Migration file created in migrations/versions/
- Upgrade and downgrade functions defined

**Implementation**:
```bash
# Initialize Alembic (first time only)
cd backend
alembic init migrations

# Configure alembic.ini with DATABASE_URL
# Edit migrations/env.py to import models

# Create migration
alembic revision --autogenerate -m "Create users and tasks tables"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

**Success Criteria**:
- [x] Migration file created
- [x] Upgrade creates tables/columns
- [x] Downgrade removes changes
- [x] No data loss on upgrade

---

### DB-004: Create Database Indexes

**Description**: Add indexes to optimize query performance.

**Inputs**:
- `table` (string): Table name
- `columns` (array): Columns to index
- `unique` (boolean): Create unique index

**Outputs**:
- Index created in database
- Query performance improved

**Example**:
```python
# Already defined in SQLModel with index=True
email: str = Field(unique=True, index=True)
user_id: int = Field(foreign_key="users.id", index=True)

# For composite indexes, use Alembic migration:
from alembic import op

def upgrade():
    op.create_index(
        'idx_tasks_user_id_completed',
        'tasks',
        ['user_id', 'completed']
    )
```

**Success Criteria**:
- [x] Index created successfully
- [x] Query plans show index usage
- [x] Query performance improved

---

## Authentication & Security Skills

### AUTH-001: Hash Password

**Description**: Securely hash passwords using bcrypt before storage.

**Inputs**:
- `plain_password` (string): User's plaintext password

**Outputs**:
- `password_hash` (string): Bcrypt-hashed password

**Implementation**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Success Criteria**:
- [x] Password hashed with bcrypt
- [x] Hash is different each time (salt)
- [x] Verification works correctly
- [x] Invalid passwords rejected

---

### AUTH-002: Verify User Credentials

**Description**: Authenticate user by verifying email and password.

**Inputs**:
- `email` (string): User's email
- `password` (string): User's password

**Outputs**:
- `user` (object): User object if valid
- `None`: If credentials invalid

**Implementation**:
```python
from sqlmodel import Session, select
from models import User

async def authenticate_user(
    email: str,
    password: str,
    session: Session
) -> User | None:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
```

**Success Criteria**:
- [x] Valid credentials return user
- [x] Invalid email returns None
- [x] Invalid password returns None
- [x] No timing attacks (constant-time comparison)

---

### AUTH-003: Validate JWT Token

**Description**: Extract and validate JWT token from request headers.

**Inputs**:
- `authorization_header` (string): Bearer token from request

**Outputs**:
- `user_id` (int): Extracted user ID
- Raises exception if invalid

**Implementation**:
```python
from fastapi import HTTPException, status
from jose import JWTError, jwt

def validate_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

**Success Criteria**:
- [x] Valid tokens return user_id
- [x] Expired tokens raise 401
- [x] Invalid signature raises 401
- [x] Malformed tokens raise 401

---

## Testing & Validation Skills

### TEST-001: Write Backend Unit Test

**Description**: Create pytest unit tests for backend functions.

**Inputs**:
- `function_under_test` (function): Function to test
- `test_cases` (array): List of test cases with inputs/outputs

**Outputs**:
- Test file in backend/tests/
- Test cases cover success and error paths

**Example**:
```python
# backend/tests/test_auth.py
import pytest
from auth.jwt import create_access_token, verify_token
from datetime import timedelta

def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": 1}
    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_valid_token():
    """Test verification of valid token."""
    data = {"sub": 1}
    token = create_access_token(data)
    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == 1

def test_verify_expired_token():
    """Test verification of expired token."""
    data = {"sub": 1}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    payload = verify_token(token)

    assert payload is None

def test_verify_invalid_token():
    """Test verification of invalid token."""
    payload = verify_token("invalid.token.here")
    assert payload is None
```

**Success Criteria**:
- [x] Tests run with pytest
- [x] Success cases tested
- [x] Error cases tested
- [x] Edge cases covered
- [x] Tests pass

---

### TEST-002: Write API Integration Test

**Description**: Create integration tests for API endpoints using httpx test client.

**Inputs**:
- `endpoint` (string): API endpoint to test
- `test_scenarios` (array): Success, error, and edge cases

**Outputs**:
- Integration test file
- Tests cover full request/response cycle

**Example**:
```python
# backend/tests/test_tasks_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    """Create test user and return auth token."""
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    return response.json()["access_token"]

def test_create_task(auth_token):
    """Test creating a new task."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/api/1/tasks",
        json={"description": "Test task"},
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Test task"
    assert data["completed"] is False
    assert "id" in data

def test_list_tasks(auth_token):
    """Test listing user's tasks."""
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Create tasks
    client.post("/api/1/tasks", json={"description": "Task 1"}, headers=headers)
    client.post("/api/1/tasks", json={"description": "Task 2"}, headers=headers)

    # List tasks
    response = client.get("/api/1/tasks", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_unauthorized_access():
    """Test accessing endpoint without token."""
    response = client.get("/api/1/tasks")
    assert response.status_code == 401
```

**Success Criteria**:
- [x] Tests use test client
- [x] Authentication tested
- [x] Success responses validated
- [x] Error responses validated
- [x] All tests pass

---

### TEST-003: Write Frontend Component Test

**Description**: Create Jest/React Testing Library tests for React components.

**Inputs**:
- `component` (component): React component to test
- `test_cases` (array): Rendering, interaction, and state tests

**Outputs**:
- Test file in frontend/__tests__/
- Tests cover rendering and user interactions

**Example**:
```typescript
// frontend/__tests__/TaskItem.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import TaskItem from '@/components/TaskItem'

describe('TaskItem', () => {
  const mockTask = {
    id: 1,
    description: 'Test task',
    completed: false,
    user_id: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  it('renders task description', () => {
    render(<TaskItem task={mockTask} onToggle={jest.fn()} onDelete={jest.fn()} />)
    expect(screen.getByText('Test task')).toBeInTheDocument()
  })

  it('calls onToggle when checkbox clicked', () => {
    const onToggle = jest.fn()
    render(<TaskItem task={mockTask} onToggle={onToggle} onDelete={jest.fn()} />)

    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)

    expect(onToggle).toHaveBeenCalledWith(1)
  })

  it('applies line-through when completed', () => {
    const completedTask = { ...mockTask, completed: true }
    render(<TaskItem task={completedTask} onToggle={jest.fn()} onDelete={jest.fn()} />)

    const description = screen.getByText('Test task')
    expect(description).toHaveClass('line-through')
  })
})
```

**Success Criteria**:
- [x] Tests run with npm test
- [x] Component rendering tested
- [x] User interactions tested
- [x] Props handled correctly
- [x] All tests pass

---

## Documentation Skills

### DOC-001: Generate OpenAPI Schema

**Description**: Generate OpenAPI/Swagger documentation from FastAPI application.

**Inputs**:
- `app` (FastAPI): FastAPI application instance

**Outputs**:
- OpenAPI schema JSON/YAML
- Interactive docs at /docs endpoint

**Implementation**:
```python
# Automatic in FastAPI
from fastapi import FastAPI

app = FastAPI(
    title="Todo API",
    description="Multi-user task management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Access at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
# http://localhost:8000/openapi.json (OpenAPI schema)
```

**Success Criteria**:
- [x] OpenAPI schema generated
- [x] Interactive docs accessible
- [x] All endpoints documented
- [x] Request/response schemas shown

---

### DOC-002: Write Feature Documentation

**Description**: Create comprehensive documentation for a feature.

**Inputs**:
- `feature_name` (string): Name of feature
- `user_stories` (array): User stories from spec
- `api_endpoints` (array): Related API endpoints

**Outputs**:
- Feature documentation in specs/ directory
- Examples and use cases included

**Success Criteria**:
- [x] Clear feature description
- [x] User scenarios explained
- [x] API usage examples provided
- [x] Error cases documented

---

## DevOps & Deployment Skills

### DEVOPS-001: Create Docker Compose Configuration

**Description**: Set up docker-compose.yml for local development environment.

**Inputs**:
- `services` (array): List of services (frontend, backend)
- `environment_vars` (object): Environment variables

**Outputs**:
- docker-compose.yml file
- Services can be started with `docker-compose up`

**Implementation**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./backend:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev
    depends_on:
      - backend
```

**Success Criteria**:
- [x] docker-compose.yml created
- [x] All services defined
- [x] Environment variables configured
- [x] Services start successfully

---

### DEVOPS-002: Configure Environment Variables

**Description**: Create .env files with required configuration for each environment.

**Inputs**:
- `environment` (enum): 'development' | 'production'
- `required_vars` (array): List of required variables

**Outputs**:
- .env file created
- .env.example file for documentation

**Example**:
```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ENVIRONMENT=development

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
BETTER_AUTH_URL=http://localhost:3000
NODE_ENV=development
```

**Success Criteria**:
- [x] .env files created
- [x] All required variables present
- [x] Secrets not committed to git
- [x] .env.example provided

---

## Skill Usage Patterns

### Sequential Skills (Must be done in order)

1. **Project Initialization**:
   - FE-001: Initialize Next.js Project
   - BE-001: Initialize FastAPI Project
   - DB-002: Connect to Neon Database
   - DEVOPS-002: Configure Environment Variables

2. **Authentication Setup**:
   - AUTH-001: Hash Password
   - BE-003: Implement JWT Authentication
   - FE-003: Implement Better Auth
   - AUTH-002: Verify User Credentials
   - FE-005: Implement Route Protection

3. **API Development**:
   - DB-001: Define Database Schema
   - DB-003: Create Database Migration
   - BE-002: Define API Endpoint
   - BE-005: Implement User-Scoped Data Access
   - BE-004: Configure CORS

4. **Frontend Development**:
   - FE-002: Create React Component
   - FE-004: Create API Client
   - FE-006: Style with TailwindCSS

5. **Testing**:
   - TEST-001: Write Backend Unit Test
   - TEST-002: Write API Integration Test
   - TEST-003: Write Frontend Component Test

### Parallel Skills (Can be done simultaneously)

- FE-002 (Create Components) can run parallel with BE-002 (Define Endpoints)
- TEST-001 (Backend Tests) can run parallel with TEST-003 (Frontend Tests)
- DB-004 (Create Indexes) can run parallel with DOC-001 (Generate API Docs)
- FE-006 (Styling) can run parallel with BE-005 (Data Access)

### Dependent Skills

- FE-004 (API Client) depends on BE-003 (JWT Auth)
- FE-005 (Route Protection) depends on FE-003 (Better Auth)
- BE-005 (User-Scoped Access) depends on BE-003 (JWT Auth)
- TEST-002 (API Tests) depends on BE-002 (API Endpoints)
- TEST-003 (Component Tests) depends on FE-002 (React Components)

---

## Skill Execution Checklist

Before executing a skill:
- [ ] Verify all dependencies are met
- [ ] Check inputs are valid
- [ ] Confirm environment is configured
- [ ] Have test data ready

During skill execution:
- [ ] Follow implementation exactly
- [ ] Handle errors appropriately
- [ ] Log important steps
- [ ] Validate outputs

After skill execution:
- [ ] Verify success criteria
- [ ] Run relevant tests
- [ ] Document any issues
- [ ] Update dependent skills if needed

---

## Skill Metrics

Track these metrics for each skill execution:

- **Success Rate**: % of successful executions
- **Average Duration**: Time to complete skill
- **Error Rate**: % of executions with errors
- **Dependencies Met**: % where dependencies were satisfied
- **Test Pass Rate**: % of tests passing after execution

This helps identify:
- Skills that need improvement
- Common failure patterns
- Optimization opportunities
- Training needs
