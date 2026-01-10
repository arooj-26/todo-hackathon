# Data Model: Advanced Cloud Deployment

**Feature**: Advanced Cloud Deployment with Event-Driven Architecture
**Date**: 2026-01-05
**Status**: Complete

## Overview

This document defines the data model for Phase V, including entities, relationships, validation rules, state transitions, and event schemas. The model supports advanced features (recurring tasks, reminders), intermediate features (priorities, tags, search), and event-driven architecture (immutable event log).

**Storage Strategy**:
- **Primary Storage**: Neon Serverless PostgreSQL (relational data: tasks, users, tags, recurrence patterns)
- **Event Log**: Kafka topics with 90-day retention (immutable event history)
- **Search Index**: PostgreSQL GIN index on tsvector (full-text search)

---

## Core Entities

### 1. User

Represents a person using the Todo Chatbot system.

**Fields**:
- `id` (UUID, primary key): Unique user identifier
- `username` (string, unique, max 50 chars): User's display name
- `email` (string, unique, email format): User's email address
- `timezone` (string, default "UTC"): IANA timezone for due date display (e.g., "America/New_York")
- `notification_preferences` (JSONB): Notification channels enabled (email, push, in-app)
- `created_at` (timestamp): User registration timestamp
- `updated_at` (timestamp): Last profile update timestamp

**Validation Rules**:
- `username`: Must be 3-50 characters, alphanumeric with underscores/hyphens only
- `email`: Must match RFC 5322 email format
- `timezone`: Must be valid IANA timezone from pytz.all_timezones
- `notification_preferences`: Must be valid JSON with keys: email (bool), push (bool), in_app (bool)

**Indexes**:
- Primary key: `id`
- Unique: `username`, `email`

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "alice_dev",
  "email": "alice@example.com",
  "timezone": "America/Los_Angeles",
  "notification_preferences": {
    "email": true,
    "push": false,
    "in_app": true
  },
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-01T10:00:00Z"
}
```

---

### 2. Task

Represents a unit of work with optional recurrence pattern and due date.

**Fields**:
- `id` (integer, primary key, auto-increment): Unique task identifier
- `user_id` (UUID, foreign key → User.id): Owner of the task
- `title` (string, max 200 chars): Task title (required)
- `description` (text, nullable): Task description/notes
- `status` (enum: "todo", "in_progress", "completed"): Current task state
- `priority` (enum: "high", "medium", "low", default "medium"): Task priority level
- `due_at` (timestamp with timezone, nullable): When task is due (optional)
- `completed_at` (timestamp, nullable): When task was marked complete
- `created_at` (timestamp): Task creation timestamp
- `updated_at` (timestamp): Last modification timestamp
- `recurrence_pattern_id` (integer, nullable, foreign key → RecurrencePattern.id): Link to recurrence rule (if recurring)
- `parent_task_id` (integer, nullable, foreign key → Task.id): Link to original task (for recurring instances)
- `search_vector` (tsvector, generated): Full-text search index (generated from title + description)

**Validation Rules**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 10,000 characters
- `status`: Must be one of ["todo", "in_progress", "completed"]
- `priority`: Must be one of ["high", "medium", "low"]
- `due_at`: If set, must be in future (at creation time)
- `completed_at`: Can only be set when status = "completed"
- `recurrence_pattern_id`: If set, task is recurring (parent task in series)
- `parent_task_id`: If set, task is instance of recurring task (points to parent)

**Constraints**:
- Task cannot have both `recurrence_pattern_id` AND `parent_task_id` (either parent or instance, not both)
- `completed_at` must be NULL if status != "completed"
- `completed_at` must be non-NULL if status = "completed"

**Indexes**:
- Primary key: `id`
- Foreign key: `user_id` → User.id (ON DELETE CASCADE)
- Foreign key: `recurrence_pattern_id` → RecurrencePattern.id (ON DELETE SET NULL)
- Foreign key: `parent_task_id` → Task.id (ON DELETE SET NULL)
- Composite: `(user_id, status)` for filtering user's tasks by status
- Composite: `(user_id, priority, due_at)` for sorting by priority + due date
- GIN index: `search_vector` for full-text search

**State Transitions**:
```
todo → in_progress → completed
 ↓                      ↓
 ↓← ← ← ← ← ← ← ← ← ← ←↓  (can move back to todo from any state)
```

**Allowed Transitions**:
- todo → in_progress: User starts work
- in_progress → completed: User finishes work
- completed → todo: User reopens task
- todo → completed: User completes without "in progress" step
- Any state → todo: User resets task

**Example**:
```json
{
  "id": 1001,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Weekly Team Meeting",
  "description": "Discuss sprint progress and blockers",
  "status": "todo",
  "priority": "high",
  "due_at": "2026-01-06T10:00:00-08:00",
  "completed_at": null,
  "created_at": "2026-01-01T09:00:00Z",
  "updated_at": "2026-01-01T09:00:00Z",
  "recurrence_pattern_id": 101,
  "parent_task_id": null,
  "search_vector": "'discuss':3 'meet':2 'team':1 'week':1"
}
```

---

### 3. RecurrencePattern

Defines how a recurring task repeats (daily, weekly, monthly patterns).

**Fields**:
- `id` (integer, primary key, auto-increment): Unique pattern identifier
- `task_id` (integer, unique, foreign key → Task.id): Parent task this pattern applies to
- `pattern_type` (enum: "daily", "weekly", "monthly"): Recurrence frequency
- `interval` (integer, default 1): Repeat every N days/weeks/months (e.g., interval=2 → every 2 weeks)
- `days_of_week` (integer array, nullable): For weekly: [0=Mon, 1=Tue, ..., 6=Sun] (e.g., [0, 2, 4] = Mon, Wed, Fri)
- `day_of_month` (integer, nullable): For monthly: 1-31 or -1 (last day of month)
- `end_condition` (enum: "never", "after_occurrences", "by_date"): When to stop generating instances
- `end_date` (date, nullable): If end_condition="by_date", stop after this date
- `occurrence_count` (integer, nullable): If end_condition="after_occurrences", stop after N instances
- `current_occurrence` (integer, default 0): Counter for tracking how many instances created
- `created_at` (timestamp): Pattern creation timestamp
- `updated_at` (timestamp): Last modification timestamp

**Validation Rules**:
- `pattern_type`: Required, must be one of ["daily", "weekly", "monthly"]
- `interval`: Must be >= 1, max 365 (prevent excessive future instances)
- `days_of_week`: Required if pattern_type="weekly", must be array of 0-6, length 1-7
- `day_of_month`: Required if pattern_type="monthly", must be 1-31 or -1
- `end_condition`: Required, must be one of ["never", "after_occurrences", "by_date"]
- `end_date`: Required if end_condition="by_date", must be in future
- `occurrence_count`: Required if end_condition="after_occurrences", must be >= 2, max 730 (2 years)
- `current_occurrence`: Read-only, auto-incremented by Recurring Task Service

**Constraints**:
- If pattern_type="weekly", days_of_week must be non-NULL
- If pattern_type="monthly", day_of_month must be non-NULL
- If end_condition="by_date", end_date must be non-NULL
- If end_condition="after_occurrences", occurrence_count must be non-NULL

**Indexes**:
- Primary key: `id`
- Unique: `task_id` (one pattern per task)
- Foreign key: `task_id` → Task.id (ON DELETE CASCADE)

**Example (Weekly Recurrence)**:
```json
{
  "id": 101,
  "task_id": 1001,
  "pattern_type": "weekly",
  "interval": 1,
  "days_of_week": [0],
  "day_of_month": null,
  "end_condition": "never",
  "end_date": null,
  "occurrence_count": null,
  "current_occurrence": 3,
  "created_at": "2026-01-01T09:00:00Z",
  "updated_at": "2026-01-01T09:00:00Z"
}
```

---

### 4. Reminder

Represents a scheduled notification for a task with due date.

**Fields**:
- `id` (integer, primary key, auto-increment): Unique reminder identifier
- `task_id` (integer, foreign key → Task.id): Task this reminder is for
- `remind_at` (timestamp with timezone): When to send reminder
- `delivery_status` (enum: "pending", "sent", "cancelled"): Current reminder state
- `notification_channel` (enum: "email", "push", "in_app"): How to deliver reminder
- `dapr_job_id` (string, nullable): Dapr Jobs API job ID for scheduled trigger
- `created_at` (timestamp): Reminder creation timestamp
- `updated_at` (timestamp): Last status update timestamp

**Validation Rules**:
- `task_id`: Required, must reference existing task with due_at set
- `remind_at`: Required, must be < task.due_at (reminder before due date)
- `delivery_status`: Must be one of ["pending", "sent", "cancelled"]
- `notification_channel`: Must be one of ["email", "push", "in_app"]
- `dapr_job_id`: Must match format "reminder-task-{task_id}"

**State Transitions**:
```
pending → sent (when notification delivered)
pending → cancelled (if task completed before reminder or due date changed)
```

**Indexes**:
- Primary key: `id`
- Foreign key: `task_id` → Task.id (ON DELETE CASCADE)
- Composite: `(task_id, remind_at)` for checking duplicate reminders
- Index: `(remind_at, delivery_status)` for querying pending reminders

**Example**:
```json
{
  "id": 501,
  "task_id": 1001,
  "remind_at": "2026-01-06T09:00:00-08:00",
  "delivery_status": "pending",
  "notification_channel": "email",
  "dapr_job_id": "reminder-task-1001",
  "created_at": "2026-01-01T09:00:00Z",
  "updated_at": "2026-01-01T09:00:00Z"
}
```

---

### 5. Tag

Represents a reusable label for categorizing tasks.

**Fields**:
- `id` (integer, primary key, auto-increment): Unique tag identifier
- `name` (string, unique, max 50 chars): Tag name (e.g., "urgent", "backend", "bug-fix")
- `color` (string, nullable, max 7 chars): Hex color for UI display (e.g., "#FF5733")
- `usage_count` (integer, default 0): Number of tasks tagged (for autocomplete ranking)
- `created_at` (timestamp): Tag creation timestamp
- `updated_at` (timestamp): Last modification timestamp

**Validation Rules**:
- `name`: Required, 1-50 characters, lowercase, alphanumeric with hyphens only (regex: `^[a-z0-9-]+$`)
- `color`: Optional, must match hex color format `^#[0-9A-F]{6}$` if provided
- `usage_count`: Read-only, auto-calculated from TaskTag join table

**Indexes**:
- Primary key: `id`
- Unique: `name` (case-insensitive)
- Index: `usage_count DESC` for autocomplete sorting

**Example**:
```json
{
  "id": 201,
  "name": "urgent",
  "color": "#FF5733",
  "usage_count": 42,
  "created_at": "2026-01-01T08:00:00Z",
  "updated_at": "2026-01-05T10:30:00Z"
}
```

---

### 6. TaskTag (Junction Table)

Many-to-many relationship between tasks and tags.

**Fields**:
- `task_id` (integer, foreign key → Task.id, part of composite primary key): Task being tagged
- `tag_id` (integer, foreign key → Tag.id, part of composite primary key): Tag applied to task
- `created_at` (timestamp): When tag was applied to task

**Indexes**:
- Composite primary key: `(task_id, tag_id)`
- Foreign key: `task_id` → Task.id (ON DELETE CASCADE)
- Foreign key: `tag_id` → Tag.id (ON DELETE CASCADE)
- Index: `tag_id` for reverse lookup (all tasks with specific tag)

**Example**:
```json
{
  "task_id": 1001,
  "tag_id": 201,
  "created_at": "2026-01-01T09:05:00Z"
}
```

---

### 7. AuditLog

Immutable log of all task operations, consumed from Kafka `task-events` topic.

**Fields**:
- `id` (bigint, primary key, auto-increment): Unique audit log entry identifier
- `event_type` (enum: "created", "updated", "completed", "deleted"): Type of operation
- `task_id` (integer): Task that was operated on (not foreign key - task may be deleted)
- `user_id` (UUID): User who performed operation (not foreign key - user may be deleted)
- `event_data` (JSONB): Complete task snapshot at time of operation (includes all fields)
- `correlation_id` (UUID): Trace ID for distributed tracing (links to request that caused event)
- `timestamp` (timestamp): When operation occurred
- `created_at` (timestamp): When audit log entry was persisted (typically few ms after timestamp)

**Validation Rules**:
- `event_type`: Must be one of ["created", "updated", "completed", "deleted"]
- `task_id`: Required, must be > 0
- `user_id`: Required, must be valid UUID format
- `event_data`: Required, must be valid JSON containing task snapshot
- `correlation_id`: Required, must be valid UUID format
- `timestamp`: Required, must be <= created_at

**Indexes**:
- Primary key: `id`
- Index: `(task_id, timestamp DESC)` for viewing task history
- Index: `(user_id, timestamp DESC)` for viewing user activity
- Index: `correlation_id` for tracing request flows
- BRIN index: `timestamp` for time-range queries (efficient for large tables)

**Retention Policy**:
- Audit logs retained for 90 days (matches Kafka topic retention)
- After 90 days, archived to cold storage (S3, Glacier) for compliance

**Example**:
```json
{
  "id": 100001,
  "event_type": "completed",
  "task_id": 1001,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_data": {
    "id": 1001,
    "title": "Weekly Team Meeting",
    "status": "completed",
    "priority": "high",
    "due_at": "2026-01-06T10:00:00-08:00",
    "completed_at": "2026-01-06T10:15:00-08:00"
  },
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-01-06T10:15:00.123Z",
  "created_at": "2026-01-06T10:15:00.456Z"
}
```

---

## Event Schemas

Events published to Kafka topics follow these immutable schemas (version 1.0).

### Base Event Schema

All events inherit from this base schema.

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

class BaseEvent(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    event_type: str
    task_id: int = Field(gt=0)
    user_id: str = Field(pattern=r"^[0-9a-f-]{36}$")  # UUID format
    timestamp: datetime
    correlation_id: str = Field(pattern=r"^[0-9a-f-]{36}$")
```

### TaskEvent Schema

Published to `task-events` topic for all CRUD operations.

```python
class TaskEvent(BaseEvent):
    event_type: Literal["created", "updated", "completed", "deleted"]
    task_snapshot: dict  # Full Task object at time of event

# Example payload
{
  "schema_version": "1.0",
  "event_type": "completed",
  "task_id": 1001,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-06T10:15:00.123Z",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "task_snapshot": {
    "id": 1001,
    "title": "Weekly Team Meeting",
    "status": "completed",
    "priority": "high",
    "due_at": "2026-01-06T10:00:00-08:00",
    "completed_at": "2026-01-06T10:15:00-08:00",
    "recurrence_pattern_id": 101
  }
}
```

**Kafka Configuration**:
- Topic: `task-events`
- Partitions: 3
- Replication Factor: 2 (cloud), 1 (Minikube)
- Retention: 90 days
- Key: `task_id` (ensures ordering per task)

### ReminderEvent Schema

Published to `reminders` topic when Dapr Jobs API fires reminder callback.

```python
class ReminderEvent(BaseEvent):
    event_type: Literal["reminder.due"]
    title: str
    due_at: datetime
    remind_at: datetime

# Example payload
{
  "schema_version": "1.0",
  "event_type": "reminder.due",
  "task_id": 1001,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-06T09:00:00.000Z",
  "correlation_id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "title": "Weekly Team Meeting",
  "due_at": "2026-01-06T10:00:00-08:00",
  "remind_at": "2026-01-06T09:00:00-08:00"
}
```

**Kafka Configuration**:
- Topic: `reminders`
- Partitions: 3
- Replication Factor: 2 (cloud), 1 (Minikube)
- Retention: 7 days (reminders ephemeral, no long-term retention needed)
- Key: `user_id` (distribute reminders across users evenly)

### TaskUpdateEvent Schema

Published to `task-updates` topic for real-time client synchronization.

```python
class TaskUpdateEvent(BaseEvent):
    event_type: Literal["task.changed"]
    change_summary: str  # Human-readable change description (e.g., "Priority changed to High")

# Example payload
{
  "schema_version": "1.0",
  "event_type": "task.changed",
  "task_id": 1001,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-06T10:15:00.123Z",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "change_summary": "Task marked completed"
}
```

**Kafka Configuration**:
- Topic: `task-updates`
- Partitions: 3
- Replication Factor: 2 (cloud), 1 (Minikube)
- Retention: 1 day (real-time updates, no historical value)
- Key: `user_id` (all updates for user go to same partition)

---

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│  User                                   Task                     RecurrencePattern  │
│  ────────                              ─────────                ───────────────────  │
│  • id (PK)                             • id (PK)                • id (PK)            │
│  • username (unique)    ┌────────────< • user_id (FK)           • task_id (FK,UK)   │
│  • email (unique)       │              • title                  • pattern_type      │
│  • timezone             │              • description            • interval           │
│  • notification_prefs   │              • status                 • days_of_week      │
│  • created_at           │              • priority               • day_of_month      │
│  • updated_at           │              • due_at                 • end_condition     │
│                         │              • completed_at           • end_date          │
│                         │              • created_at             • occurrence_count  │
│                         │              • updated_at             • current_occurrence│
│                         │              • recurrence_pattern_id  └─────────┬─────────│
│                         │              • parent_task_id                   │         │
│                         │              • search_vector                    │         │
│                         │              └───────────────────────────────<──┘         │
│                         │                     ↓                                     │
│                         │                     ↓                                     │
│                         │              ┌──────────────────┐                         │
│                         │              │   TaskTag (M:N)  │                         │
│                         │              │  ─────────────── │                         │
│                         │              │  • task_id (FK)  │                         │
│                         │              │  • tag_id (FK)   │                         │
│                         │              │  • created_at    │                         │
│                         │              └────────┬─────────┘                         │
│                         │                       │                                   │
│                         │                       ↓                                   │
│                         │              ┌──────────────────┐                         │
│                         │              │      Tag         │                         │
│                         │              │  ───────────────  │                         │
│                         │              │  • id (PK)       │                         │
│                         │              │  • name (unique) │                         │
│                         │              │  • color         │                         │
│                         │              │  • usage_count   │                         │
│                         │              │  • created_at    │                         │
│                         │              │  • updated_at    │                         │
│                         │              └──────────────────┘                         │
│                         │                                                           │
│                         │              ┌──────────────────┐                         │
│                         └───────────>  │     Reminder     │                         │
│                                        │  ───────────────  │                         │
│                                        │  • id (PK)       │                         │
│                                        │  • task_id (FK)  │                         │
│                                        │  • remind_at     │                         │
│                                        │  • delivery_stat │                         │
│                                        │  • notif_channel │                         │
│                                        │  • dapr_job_id   │                         │
│                                        │  • created_at    │                         │
│                                        │  • updated_at    │                         │
│                                        └──────────────────┘                         │
│                                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │                         Event Schemas (Kafka Topics)                         │  │
│  │  ───────────────────────────────────────────────────────────────────────────  │  │
│  │                                                                               │  │
│  │  TaskEvent (task-events topic)              ReminderEvent (reminders topic)  │  │
│  │  ──────────────────────────────              ──────────────────────────────  │  │
│  │  • schema_version: "1.0"                    • schema_version: "1.0"          │  │
│  │  • event_type: created|updated|             • event_type: reminder.due       │  │
│  │    completed|deleted                        • task_id                        │  │
│  │  • task_id                                  • user_id                        │  │
│  │  • user_id                                  • timestamp                      │  │
│  │  • timestamp                                • correlation_id                 │  │
│  │  • correlation_id                           • title                          │  │
│  │  • task_snapshot (full Task JSON)           • due_at                          │  │
│  │                                             • remind_at                      │  │
│  │                                                                               │  │
│  │  TaskUpdateEvent (task-updates topic)       AuditLog (PostgreSQL)           │  │
│  │  ───────────────────────────────────         ──────────────────────────────  │  │
│  │  • schema_version: "1.0"                    • id (PK, bigint)                │  │
│  │  • event_type: task.changed                 • event_type                    │  │
│  │  • task_id                                  • task_id (no FK)               │  │
│  │  • user_id                                  • user_id (no FK)               │  │
│  │  • timestamp                                • event_data (JSONB)            │  │
│  │  • correlation_id                           • correlation_id                │  │
│  │  • change_summary                           • timestamp                     │  │
│  │                                             • created_at                    │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema (SQL DDL)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC' NOT NULL,
    notification_preferences JSONB DEFAULT '{"email": true, "push": false, "in_app": true}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT username_format CHECK (username ~ '^[a-zA-Z0-9_-]{3,50}$'),
    CONSTRAINT email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'todo' NOT NULL CHECK (status IN ('todo', 'in_progress', 'completed')),
    priority VARCHAR(10) DEFAULT 'medium' NOT NULL CHECK (priority IN ('high', 'medium', 'low')),
    due_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recurrence_pattern_id INTEGER,
    parent_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
    ) STORED,
    CONSTRAINT completed_at_status CHECK (
        (status = 'completed' AND completed_at IS NOT NULL) OR
        (status != 'completed' AND completed_at IS NULL)
    ),
    CONSTRAINT not_both_parent_and_instance CHECK (
        NOT (recurrence_pattern_id IS NOT NULL AND parent_task_id IS NOT NULL)
    )
);

-- Indexes for tasks
CREATE INDEX idx_tasks_user_status ON tasks(user_id, status);
CREATE INDEX idx_tasks_user_priority_due ON tasks(user_id, priority, due_at);
CREATE INDEX idx_tasks_search_vector ON tasks USING GIN(search_vector);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);

-- Recurrence patterns table
CREATE TABLE recurrence_patterns (
    id SERIAL PRIMARY KEY,
    task_id INTEGER UNIQUE NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    pattern_type VARCHAR(10) NOT NULL CHECK (pattern_type IN ('daily', 'weekly', 'monthly')),
    interval INTEGER DEFAULT 1 NOT NULL CHECK (interval >= 1 AND interval <= 365),
    days_of_week INTEGER[],
    day_of_month INTEGER,
    end_condition VARCHAR(20) NOT NULL CHECK (end_condition IN ('never', 'after_occurrences', 'by_date')),
    end_date DATE,
    occurrence_count INTEGER,
    current_occurrence INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT weekly_requires_days CHECK (
        pattern_type != 'weekly' OR days_of_week IS NOT NULL
    ),
    CONSTRAINT monthly_requires_day CHECK (
        pattern_type != 'monthly' OR day_of_month IS NOT NULL
    ),
    CONSTRAINT by_date_requires_end_date CHECK (
        end_condition != 'by_date' OR end_date IS NOT NULL
    ),
    CONSTRAINT after_occurrences_requires_count CHECK (
        end_condition != 'after_occurrences' OR occurrence_count IS NOT NULL
    ),
    CONSTRAINT day_of_month_range CHECK (
        day_of_month IS NULL OR (day_of_month >= 1 AND day_of_month <= 31) OR day_of_month = -1
    ),
    CONSTRAINT occurrence_count_range CHECK (
        occurrence_count IS NULL OR (occurrence_count >= 2 AND occurrence_count <= 730)
    )
);

-- Add foreign key from tasks to recurrence_patterns (after table creation to avoid circular dependency)
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_recurrence_pattern
    FOREIGN KEY (recurrence_pattern_id) REFERENCES recurrence_patterns(id) ON DELETE SET NULL;

-- Reminders table
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    remind_at TIMESTAMPTZ NOT NULL,
    delivery_status VARCHAR(20) DEFAULT 'pending' NOT NULL CHECK (delivery_status IN ('pending', 'sent', 'cancelled')),
    notification_channel VARCHAR(10) NOT NULL CHECK (notification_channel IN ('email', 'push', 'in_app')),
    dapr_job_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for reminders
CREATE INDEX idx_reminders_task ON reminders(task_id, remind_at);
CREATE INDEX idx_reminders_pending ON reminders(remind_at, delivery_status) WHERE delivery_status = 'pending';

-- Tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    color VARCHAR(7),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT tag_name_format CHECK (name ~ '^[a-z0-9-]+$'),
    CONSTRAINT color_format CHECK (color IS NULL OR color ~ '^#[0-9A-F]{6}$')
);

-- Index for tag autocomplete
CREATE INDEX idx_tags_usage_count ON tags(usage_count DESC);

-- Task-Tag junction table
CREATE TABLE task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, tag_id)
);

-- Indexes for task-tag lookups
CREATE INDEX idx_task_tags_tag ON task_tags(tag_id);

-- Audit log table
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('created', 'updated', 'completed', 'deleted')),
    task_id INTEGER NOT NULL,
    user_id UUID NOT NULL,
    event_data JSONB NOT NULL,
    correlation_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT timestamp_order CHECK (timestamp <= created_at)
);

-- Indexes for audit log queries
CREATE INDEX idx_audit_logs_task ON audit_logs(task_id, timestamp DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_logs_correlation ON audit_logs(correlation_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs USING BRIN(timestamp);  -- Efficient for large tables

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recurrence_patterns_updated_at BEFORE UPDATE ON recurrence_patterns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reminders_updated_at BEFORE UPDATE ON reminders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tags_updated_at BEFORE UPDATE ON tags
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Data Model Status

✅ **COMPLETE** - All entities, relationships, validation rules, state transitions, event schemas, and SQL DDL defined

**Next Steps**:
1. Generate API contracts in `contracts/` directory
2. Validate data model against functional requirements (FR-001 to FR-032)
3. Create database migration scripts using Alembic or Flyway
4. Implement Pydantic models matching this schema for runtime validation
