# Data Model: AI-Powered Todo Chatbot

**Date**: 2025-12-21
**Feature**: 001-todo-ai-chatbot
**Purpose**: Define database schema, entity relationships, and data validation rules

## Overview

The data model consists of three core entities that enable stateless conversation management and task operations:
- **Task**: User's todo items with metadata
- **Conversation**: Chat sessions between user and AI assistant
- **Message**: Individual messages within conversations

All entities include `user_id` for data isolation and support multi-tenancy.

## Entity Definitions

### Task Entity

Represents a single todo item owned by a user.

**Table Name**: `tasks`

**Fields**:

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUID | PRIMARY KEY | Unique task identifier |
| `user_id` | UUID | NOT NULL, INDEXED | Owner of the task (foreign key to users if auth implemented) |
| `title` | VARCHAR(500) | NOT NULL | Task title/description |
| `description` | TEXT | NULLABLE | Optional detailed description |
| `completed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp (UTC) |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification timestamp (UTC) |
| `due_date` | TIMESTAMP | NULLABLE | Optional due date (UTC) |
| `priority` | ENUM | NOT NULL, DEFAULT 'medium' | Task priority ('low', 'medium', 'high') |

**Indexes**:
- Primary: `id` (automatic)
- Composite: `(user_id, completed)` - For filtering tasks by user and status
- Composite: `(user_id, priority)` - For filtering/sorting by priority
- Composite: `(user_id, due_date)` - For sorting by due date

**Validation Rules**:
- `title` must not be empty string (enforced at API layer)
- `title` maximum length 500 characters
- `description` maximum length 10,000 characters (reasonable limit)
- `priority` must be one of: 'low', 'medium', 'high'
- `updated_at` must be >= `created_at`
- `due_date` if provided should be in the future (soft validation, warnings only)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column, Enum as SQLEnum
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    title: str = Field(max_length=500, nullable=False)
    description: str | None = Field(default=None, max_length=10000)
    completed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    due_date: datetime | None = Field(default=None)
    priority: PriorityEnum = Field(
        default=PriorityEnum.MEDIUM,
        sa_column=Column(SQLEnum(PriorityEnum), nullable=False)
    )

    class Config:
        arbitrary_types_allowed = True
```

### Conversation Entity

Represents a chat session between a user and the AI assistant.

**Table Name**: `conversations`

**Fields**:

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUID | PRIMARY KEY | Unique conversation identifier |
| `user_id` | UUID | NOT NULL, INDEXED | Owner of the conversation |
| `created_at` | TIMESTAMP | NOT NULL | Session start timestamp (UTC) |
| `updated_at` | TIMESTAMP | NOT NULL | Last message timestamp (UTC) |

**Indexes**:
- Primary: `id` (automatic)
- Composite: `(user_id, updated_at)` - For retrieving recent conversations

**Validation Rules**:
- `updated_at` must be >= `created_at`
- Conversation must have at least one message (enforced by application logic, not database constraint)

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to messages (not needed for queries, but useful for ORM)
    messages: list["Message"] = Relationship(back_populates="conversation")
```

### Message Entity

Stores individual messages within a conversation.

**Table Name**: `messages`

**Fields**:

| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUID | PRIMARY KEY | Unique message identifier |
| `conversation_id` | UUID | NOT NULL, FOREIGN KEY | Parent conversation (references conversations.id) |
| `user_id` | UUID | NOT NULL, INDEXED | Owner (for data isolation queries) |
| `role` | ENUM | NOT NULL | Message author ('user' or 'assistant') |
| `content` | TEXT | NOT NULL | Message text content |
| `created_at` | TIMESTAMP | NOT NULL | Message timestamp (UTC) |

**Indexes**:
- Primary: `id` (automatic)
- Composite: `(conversation_id, created_at)` - For retrieving messages in chronological order
- Composite: `(user_id, conversation_id)` - For data isolation queries

**Foreign Keys**:
- `conversation_id` references `conversations(id)` ON DELETE CASCADE

**Validation Rules**:
- `content` must not be empty string
- `content` maximum length 50,000 characters (reasonable for chat messages)
- `role` must be one of: 'user', 'assistant'
- Messages must be ordered by `created_at` within a conversation

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field, Column, Enum as SQLEnum, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class RoleEnum(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False, index=True)
    user_id: UUID = Field(index=True, nullable=False)
    role: RoleEnum = Field(
        sa_column=Column(SQLEnum(RoleEnum), nullable=False)
    )
    content: str = Field(nullable=False, max_length=50000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")

    class Config:
        arbitrary_types_allowed = True
```

## Entity Relationships

### Diagram

```
User (external, not modeled)
│
├── 1:N Conversations
│   │
│   └── 1:N Messages
│
└── 1:N Tasks
```

### Relationship Details

1. **User → Conversations**: One-to-many
   - A user can have multiple conversations
   - Each conversation belongs to exactly one user
   - Enforced by `user_id` field in Conversation

2. **User → Tasks**: One-to-many
   - A user can have multiple tasks
   - Each task belongs to exactly one user
   - Enforced by `user_id` field in Task

3. **Conversation → Messages**: One-to-many
   - A conversation can have multiple messages
   - Each message belongs to exactly one conversation
   - Enforced by `conversation_id` foreign key
   - Cascade delete: Deleting a conversation deletes all its messages

**Note**: User entity is not modeled in Phase 1 (authentication is placeholder). `user_id` is treated as a string identifier passed from authentication layer.

## Database Migrations

### Initial Schema Creation

```sql
-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE priority_enum AS ENUM ('low', 'medium', 'high');
CREATE TYPE role_enum AS ENUM ('user', 'assistant');

-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role role_enum NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_user_conversation ON messages(user_id, conversation_id);

-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    priority priority_enum NOT NULL DEFAULT 'medium'
);

CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_user_priority ON tasks(user_id, priority);
CREATE INDEX idx_tasks_user_due_date ON tasks(user_id, due_date);
```

**Migration Strategy**:
- Use Alembic for schema migrations (SQLModel compatible)
- Initial migration creates all tables and indexes
- Future migrations for schema changes
- Always test migrations on staging branch (Neon branching feature)

## Data Access Patterns

### Task Operations

**Create Task**:
```sql
INSERT INTO tasks (user_id, title, description, priority, due_date)
VALUES ($1, $2, $3, $4, $5)
RETURNING *;
```

**List Tasks** (with filters):
```sql
SELECT * FROM tasks
WHERE user_id = $1
  AND ($2 IS NULL OR completed = $2)  -- status filter
  AND ($3 IS NULL OR priority = $3)   -- priority filter
ORDER BY
  CASE WHEN $4 = 'created_at' THEN created_at END,
  CASE WHEN $4 = 'due_date' THEN due_date END,
  CASE WHEN $4 = 'priority' THEN priority END;
```

**Complete Task**:
```sql
UPDATE tasks
SET completed = TRUE, updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND user_id = $2
RETURNING *;
```

**Delete Task**:
```sql
DELETE FROM tasks
WHERE id = $1 AND user_id = $2
RETURNING *;
```

**Update Task**:
```sql
UPDATE tasks
SET title = COALESCE($3, title),
    description = COALESCE($4, description),
    priority = COALESCE($5, priority),
    due_date = COALESCE($6, due_date),
    updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND user_id = $2
RETURNING *;
```

### Conversation Operations

**Create Conversation**:
```sql
INSERT INTO conversations (user_id)
VALUES ($1)
RETURNING *;
```

**Get Conversation**:
```sql
SELECT * FROM conversations
WHERE id = $1 AND user_id = $2;
```

**Get Recent Conversations**:
```sql
SELECT * FROM conversations
WHERE user_id = $1
ORDER BY updated_at DESC
LIMIT 10;
```

**Update Conversation Timestamp**:
```sql
UPDATE conversations
SET updated_at = CURRENT_TIMESTAMP
WHERE id = $1 AND user_id = $2;
```

### Message Operations

**Store Message**:
```sql
INSERT INTO messages (conversation_id, user_id, role, content)
VALUES ($1, $2, $3, $4)
RETURNING *;
```

**Get Conversation Messages**:
```sql
SELECT * FROM messages
WHERE conversation_id = $1 AND user_id = $2
ORDER BY created_at ASC;
```

**Get Recent Messages** (with limit):
```sql
SELECT * FROM messages
WHERE conversation_id = $1 AND user_id = $2
ORDER BY created_at DESC
LIMIT $3;
```

## Data Integrity Constraints

### Application-Level Constraints
- User isolation: All queries MUST include `WHERE user_id = $user_id`
- Title validation: Non-empty, max 500 chars
- Content validation: Non-empty, max lengths
- Timestamp consistency: `updated_at` >= `created_at`

### Database-Level Constraints
- Foreign keys: `message.conversation_id → conversations.id` with CASCADE DELETE
- NOT NULL constraints on required fields
- ENUM constraints on `priority` and `role`
- Primary key uniqueness

### Concurrency Handling
- Optimistic locking not required for MVP (single-user updates)
- Database-level row locking for concurrent task updates (PostgreSQL handles automatically)
- No distributed transactions needed (single database)

## Performance Considerations

### Query Optimization
- Composite indexes support common query patterns
- `user_id` always first in composite indexes (selectivity)
- Avoid SELECT * in production (specify columns)
- Use LIMIT for message retrieval (prevent loading huge histories)

### Expected Query Volumes
- Task operations: 5-10 queries per conversation turn
- Message storage: 2 inserts per turn (user + assistant)
- Conversation retrieval: 1 query per request
- Message history: 1 query per request (with limit)

### Scaling Considerations
- Partition large tables by `user_id` if > 100M rows (not needed for MVP)
- Archive old conversations if needed (not required initially)
- Connection pooling handles concurrent requests
- Read replicas for analytics queries (future consideration)

## Summary

Data model supports:
- ✅ User data isolation (all queries filter by `user_id`)
- ✅ Conversation persistence across sessions
- ✅ Task CRUD operations with filtering and sorting
- ✅ Efficient query patterns with appropriate indexes
- ✅ Referential integrity with foreign keys
- ✅ Type safety with SQLModel and Pydantic validation
- ✅ Scalability through stateless architecture

Ready to proceed to Phase 1: API Contracts.
