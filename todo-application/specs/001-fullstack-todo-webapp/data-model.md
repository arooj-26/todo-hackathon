# Data Model: Todo Full-Stack Web Application

**Feature**: 001-fullstack-todo-webapp
**Date**: 2025-12-17
**Database**: Neon Serverless PostgreSQL
**ORM**: SQLModel (SQLAlchemy + Pydantic)

## Overview

The data model supports multi-user task management with strict data isolation. Two primary entities: Users (authentication and ownership) and Tasks (todo items). Each task belongs to exactly one user, enforced through foreign key constraints.

## Entities

### User

Represents an authenticated user account with credentials and owned tasks.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique user identifier |
| email | String | Unique, Not Null, Indexed | User's email address (username for login) |
| password_hash | String | Not Null | Bcrypt-hashed password (never store plaintext) |
| created_at | DateTime | Not Null, Default: current timestamp | Account creation timestamp |
| updated_at | DateTime | Not Null, Default: current timestamp | Last account update timestamp |

**Relationships**:
- One-to-Many with Task (user.tasks) - A user can have many tasks

**Indexes**:
- Primary index on `id` (automatic)
- Unique index on `email` (for fast login lookups)

**Validation Rules**:
- Email must be valid email format
- Email must be unique across all users
- Password must be at least 8 characters before hashing
- Password hash must be generated using bcrypt with minimum 12 rounds

**Business Rules**:
- Email cannot be changed after account creation (MVP limitation)
- Deleting a user cascades to delete all their tasks
- Created_at never changes after creation
- Updated_at changes on any user record update

---

### Task

Represents a todo item with description, completion status, and user ownership.

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique task identifier |
| user_id | Integer | Foreign Key to users.id, Not Null, Indexed | Owner of this task |
| description | Text | Not Null | Task description text |
| completed | Boolean | Not Null, Default: False | Completion status (False = incomplete, True = complete) |
| created_at | DateTime | Not Null, Default: current timestamp | Task creation timestamp |
| updated_at | DateTime | Not Null, Default: current timestamp | Last task update timestamp |

**Relationships**:
- Many-to-One with User (task.user) - Each task belongs to exactly one user

**Indexes**:
- Primary index on `id` (automatic)
- Index on `user_id` (for fast filtering by user)
- Composite index on `(user_id, completed)` for filtered queries

**Validation Rules**:
- Description must be between 1 and 1000 characters
- Description cannot be only whitespace
- User_id must reference existing user
- Completed must be boolean (True/False)

**Business Rules**:
- User_id cannot be changed after task creation
- Description can be updated at any time
- Completed status can be toggled at any time
- Created_at never changes after creation
- Updated_at changes on description or completion status update
- Tasks are automatically deleted when owner user is deleted (CASCADE)

---

## Entity Relationships

```
User (1) ──< has many >── (∞) Task

- One User can have zero or many Tasks
- One Task belongs to exactly one User
- Foreign key: Task.user_id → User.id
- Delete cascade: Deleting User deletes all their Tasks
```

## Database Schema (SQL)

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_id_completed ON tasks(user_id, completed);

-- Trigger to update updated_at on users table
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_users_updated_at();

-- Trigger to update updated_at on tasks table
CREATE OR REPLACE FUNCTION update_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();
```

## SQLModel Implementation

```python
# backend/models.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    """User account with authentication credentials."""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False, max_length=255)
    password_hash: str = Field(nullable=False, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user", cascade_delete=True)

class Task(SQLModel, table=True):
    """Todo task item owned by a user."""
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    description: str = Field(nullable=False, min_length=1, max_length=1000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    user: Optional[User] = Relationship(back_populates="tasks")
```

## Data Access Patterns

### User Operations

**Create User** (Signup):
```python
user = User(email=email, password_hash=hashed_password)
session.add(user)
session.commit()
session.refresh(user)
return user
```

**Find User by Email** (Login):
```python
user = session.exec(
    select(User).where(User.email == email)
).first()
```

**Get User by ID**:
```python
user = session.get(User, user_id)
```

---

### Task Operations

**List User's Tasks**:
```python
tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
).all()
```

**List User's Incomplete Tasks**:
```python
tasks = session.exec(
    select(Task)
    .where(Task.user_id == user_id, Task.completed == False)
    .order_by(Task.created_at.desc())
).all()
```

**Create Task**:
```python
task = Task(user_id=user_id, description=description)
session.add(task)
session.commit()
session.refresh(task)
return task
```

**Get Task by ID** (with ownership check):
```python
task = session.exec(
    select(Task)
    .where(Task.id == task_id, Task.user_id == user_id)
).first()
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

**Update Task Description**:
```python
task = session.get(Task, task_id)
if task.user_id != user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
task.description = new_description
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
session.refresh(task)
return task
```

**Toggle Task Completion**:
```python
task = session.get(Task, task_id)
if task.user_id != user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
task.completed = not task.completed
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
session.refresh(task)
return task
```

**Delete Task**:
```python
task = session.get(Task, task_id)
if task.user_id != user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
session.delete(task)
session.commit()
```

## Security Considerations

1. **Password Storage**:
   - Never store plaintext passwords
   - Use bcrypt with minimum 12 rounds
   - Hash passwords before storing in database
   - Verify passwords by comparing hashes

2. **Data Isolation**:
   - Always filter tasks by authenticated user_id
   - Verify task ownership before updates/deletes
   - Return 403 for unauthorized access attempts
   - Never expose other users' data

3. **SQL Injection**:
   - SQLModel/SQLAlchemy parameterizes queries automatically
   - Never use string concatenation for queries
   - Use ORM methods for all database access

4. **Data Validation**:
   - Validate email format before storage
   - Enforce description length limits (1-1000 chars)
   - Validate boolean values for completed field
   - Sanitize user input to prevent XSS

## Migration Strategy

**Initial Migration** (create tables):
```bash
alembic revision --autogenerate -m "Create users and tasks tables"
alembic upgrade head
```

**Future Migrations**:
- Adding columns: Use `ALTER TABLE ADD COLUMN` with defaults
- Removing columns: Deprecate first, remove in later migration
- Changing types: Create new column, migrate data, drop old column
- Adding indexes: Use `CREATE INDEX CONCURRENTLY` for zero downtime

## Performance Considerations

1. **Indexes**:
   - `users.email`: Fast login lookups (unique index)
   - `tasks.user_id`: Fast user task filtering (non-unique index)
   - `tasks.(user_id, completed)`: Fast filtered queries (composite index)

2. **Query Optimization**:
   - Always filter by indexed columns (user_id)
   - Use pagination for large task lists (LIMIT/OFFSET)
   - Avoid N+1 queries (use eager loading if needed)
   - Select only needed columns for large datasets

3. **Connection Pooling**:
   - Pool size: 10 connections (for moderate load)
   - Max overflow: 20 (peak load handling)
   - Connection recycling: 1 hour
   - Pre-ping: Verify connection health

## Data Integrity

1. **Foreign Key Constraints**:
   - Task.user_id → User.id (ensures tasks have valid owners)
   - ON DELETE CASCADE (removing user removes their tasks)

2. **Unique Constraints**:
   - User.email (prevents duplicate accounts)

3. **Not Null Constraints**:
   - Critical fields (email, password_hash, user_id, description)
   - Prevents incomplete records

4. **Default Values**:
   - completed: False (new tasks are incomplete)
   - created_at: Current timestamp
   - updated_at: Current timestamp

## Edge Cases

1. **Empty Description**: Rejected by `min_length=1` validation
2. **Extremely Long Description**: Truncated by `max_length=1000` validation
3. **Invalid Email Format**: Rejected at application layer before database
4. **Duplicate Email**: Database unique constraint raises error
5. **Task Without Owner**: Foreign key constraint prevents creation
6. **Orphaned Tasks**: Prevented by CASCADE delete
7. **Concurrent Updates**: Last-write-wins (no optimistic locking in MVP)

## Testing Strategy

1. **Model Tests**:
   - Test model creation with valid data
   - Test validation rules (length limits, required fields)
   - Test relationships (user → tasks)
   - Test cascading deletes

2. **Query Tests**:
   - Test filtering by user_id
   - Test ordering (created_at desc)
   - Test pagination
   - Test ownership verification

3. **Integration Tests**:
   - Test full CRUD operations
   - Test concurrent operations
   - Test transaction rollback on errors
   - Test data isolation between users
