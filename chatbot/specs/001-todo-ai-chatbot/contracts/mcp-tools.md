# MCP Tools Contract: AI-Powered Todo Chatbot

**Date**: 2025-12-21
**Feature**: 001-todo-ai-chatbot
**Purpose**: Define MCP tool interfaces, parameters, and responses for AI agent interaction

## Overview

The MCP server exposes five tools that encapsulate all task operations. The OpenAI Agent calls these tools based on natural language intent recognition. All tools are stateless, atomic, and validate inputs.

## Tool Definitions

### 1. add_task

Creates a new task for the user.

**Tool Name**: `add_task`

**Description**: "Create a new todo task for the user with a title and optional description, due date, and priority"

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID format | User who owns the task |
| `title` | string | Yes | 1-500 chars, non-empty | Task title |
| `description` | string | No | Max 10,000 chars | Detailed task description |
| `due_date` | string (ISO 8601) | No | Valid ISO datetime | When task is due (UTC) |
| `priority` | string | No | One of: 'low', 'medium', 'high' | Task priority (default: 'medium') |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AddTaskParams(BaseModel):
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    description: str | None = Field(None, max_length=10000, description="Optional task description")
    due_date: datetime | None = Field(None, description="Optional due date in ISO 8601 format")
    priority: Priority = Field(Priority.MEDIUM, description="Task priority")
```

**Response**:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string (UUID) | Unique identifier of created task |
| `status` | string | Always "created" for success |
| `title` | string | Echo of task title for confirmation |
| `error` | string | Error message if creation failed (null on success) |

**Success Response Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "created",
  "title": "Buy groceries",
  "error": null
}
```

**Error Response Example**:
```json
{
  "task_id": null,
  "status": "error",
  "title": null,
  "error": "Title cannot be empty"
}
```

**Implementation Notes**:
- Generate UUID for task_id
- Set created_at and updated_at to current UTC time
- Default priority to 'medium' if not provided
- Validate title is non-empty after trimming whitespace
- Return error response for validation failures (don't raise exceptions)

---

### 2. list_tasks

Retrieves tasks for the user with optional filtering and sorting.

**Tool Name**: `list_tasks`

**Description**: "List todo tasks for the user with optional filters for completion status and priority, and sorting options"

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID format | User whose tasks to list |
| `status` | string | No | One of: 'all', 'pending', 'completed' | Filter by completion status (default: 'all') |
| `priority` | string | No | One of: 'low', 'medium', 'high' | Filter by priority level |
| `sort_by` | string | No | One of: 'created_at', 'due_date', 'priority' | Sort field (default: 'created_at') |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field, UUID4
from enum import Enum

class TaskStatus(str, Enum):
    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"

class SortBy(str, Enum):
    CREATED_AT = "created_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"

class ListTasksParams(BaseModel):
    user_id: UUID4 = Field(..., description="User ID whose tasks to list")
    status: TaskStatus = Field(TaskStatus.ALL, description="Filter by completion status")
    priority: Priority | None = Field(None, description="Filter by priority")
    sort_by: SortBy = Field(SortBy.CREATED_AT, description="Sort field")
```

**Response**:

| Field | Type | Description |
|-------|------|-------------|
| `tasks` | array | List of task objects (see Task Object structure below) |
| `count` | integer | Number of tasks returned |
| `error` | string | Error message if retrieval failed (null on success) |

**Task Object Structure**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2025-12-21T10:00:00Z",
  "updated_at": "2025-12-21T10:00:00Z",
  "due_date": "2025-12-22T12:00:00Z",
  "priority": "medium"
}
```

**Success Response Example**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2025-12-21T10:00:00Z",
      "updated_at": "2025-12-21T10:00:00Z",
      "due_date": "2025-12-22T12:00:00Z",
      "priority": "medium"
    }
  ],
  "count": 1,
  "error": null
}
```

**Error Response Example**:
```json
{
  "tasks": [],
  "count": 0,
  "error": "Invalid user_id format"
}
```

**Implementation Notes**:
- Always filter by user_id for data isolation
- Apply status filter: 'pending' → completed=false, 'completed' → completed=true, 'all' → no filter
- Apply priority filter if provided
- Sort by specified field (created_at default)
- Return empty array if no tasks match filters

---

### 3. complete_task

Marks a task as complete.

**Tool Name**: `complete_task`

**Description**: "Mark a todo task as complete by its ID"

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID format | User who owns the task |
| `task_id` | string (UUID) | Yes | Valid UUID format | Task to mark complete |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field, UUID4

class CompleteTaskParams(BaseModel):
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to mark complete")
```

**Response**:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string (UUID) | ID of completed task |
| `status` | string | "completed" on success |
| `title` | string | Title of completed task |
| `error` | string | Error message if operation failed (null on success) |

**Success Response Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "title": "Buy groceries",
  "error": null
}
```

**Error Response Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "error",
  "title": null,
  "error": "Task not found"
}
```

**Implementation Notes**:
- Set completed=true and updated_at=current_time
- Verify task belongs to user_id (data isolation)
- Return error if task not found
- Idempotent: completing already-completed task returns success

---

### 4. delete_task

Permanently removes a task.

**Tool Name**: `delete_task`

**Description**: "Permanently delete a todo task by its ID"

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID format | User who owns the task |
| `task_id` | string (UUID) | Yes | Valid UUID format | Task to delete |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field, UUID4

class DeleteTaskParams(BaseModel):
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to delete")
```

**Response**:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string (UUID) | ID of deleted task |
| `status` | string | "deleted" on success |
| `title` | string | Title of deleted task (for confirmation) |
| `error` | string | Error message if operation failed (null on success) |

**Success Response Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "deleted",
  "title": "Old meeting notes",
  "error": null
}
```

**Error Response Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "error",
  "title": null,
  "error": "Task not found"
}
```

**Implementation Notes**:
- Retrieve task title before deletion (for response)
- Verify task belongs to user_id (data isolation)
- Return error if task not found
- Idempotent: deleting non-existent task returns error (not success)

---

### 5. update_task

Modifies task title, description, priority, or due date.

**Tool Name**: `update_task`

**Description**: "Update a todo task's title, description, priority, or due date by its ID"

**Parameters**:

| Parameter | Type | Required | Validation | Description |
|-----------|------|----------|------------|-------------|
| `user_id` | string (UUID) | Yes | Valid UUID format | User who owns the task |
| `task_id` | string (UUID) | Yes | Valid UUID format | Task to update |
| `title` | string | No | 1-500 chars if provided | New task title |
| `description` | string | No | Max 10,000 chars | New description (null to clear) |
| `priority` | string | No | One of: 'low', 'medium', 'high' | New priority |
| `due_date` | string (ISO 8601) | No | Valid ISO datetime | New due date (null to clear) |

**Pydantic Schema**:
```python
from pydantic import BaseModel, Field, UUID4
from datetime import datetime

class UpdateTaskParams(BaseModel):
    user_id: UUID4 = Field(..., description="User ID who owns the task")
    task_id: UUID4 = Field(..., description="Task ID to update")
    title: str | None = Field(None, min_length=1, max_length=500, description="New task title")
    description: str | None = Field(None, max_length=10000, description="New task description")
    priority: Priority | None = Field(None, description="New priority")
    due_date: datetime | None = Field(None, description="New due date")
```

**Response**:

| Field | Type | Description |
|-------|------|-------------|
| `task_id` | string (UUID) | ID of updated task |
| `status` | string | "updated" on success |
| `title` | string | New title of task |
| `error` | string | Error message if operation failed (null on success) |

**Success Response Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "updated",
  "title": "Buy groceries and fruits",
  "error": null
}
```

**Error Response Example**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "error",
  "title": null,
  "error": "Task not found"
}
```

**Implementation Notes**:
- Only update fields provided (partial update)
- Set updated_at=current_time
- Verify task belongs to user_id (data isolation)
- Return error if task not found
- Validate title if provided (non-empty)
- At least one field must be provided for update

---

## MCP Server Configuration

**Server Initialization**:
```python
from mcp import Server

server = Server(name="todo-chatbot-mcp")

# Register tools
server.add_tool(add_task)
server.add_tool(list_tasks)
server.add_tool(complete_task)
server.add_tool(delete_task)
server.add_tool(update_task)
```

**Tool Registration Pattern**:
```python
@server.tool(
    name="add_task",
    description="Create a new todo task for the user with a title and optional description, due date, and priority",
    parameters=AddTaskParams
)
async def add_task(params: AddTaskParams) -> dict:
    # Implementation
    pass
```

## Error Handling Contract

All tools MUST return structured responses, never raise exceptions to the AI agent.

**Error Response Format**:
```json
{
  "task_id": null,  // or actual ID if applicable
  "status": "error",
  "title": null,
  "error": "<user-friendly error message>"
}
```

**Common Error Messages**:
- "Task not found" - task_id doesn't exist for user
- "Title cannot be empty" - validation failure
- "Invalid priority value" - priority not in allowed values
- "Invalid date format" - due_date parsing failed
- "Database connection failed" - temporary failure
- "User not authorized" - user_id mismatch (should not happen with proper isolation)

## Testing Contract

**Contract Tests Must Verify**:
1. Tool parameter schemas match Pydantic models
2. Tool responses match documented structure
3. Error responses follow error contract
4. All required fields are validated
5. Optional fields default correctly
6. Idempotency where specified (complete_task)

**Example Contract Test**:
```python
def test_add_task_contract():
    params = AddTaskParams(
        user_id="550e8400-e29b-41d4-a716-446655440000",
        title="Test task"
    )
    response = add_task(params)

    assert "task_id" in response
    assert response["status"] == "created"
    assert response["title"] == "Test task"
    assert response["error"] is None
```

## Summary

MCP tools provide:
- ✅ Clear, typed interfaces for AI agent
- ✅ Consistent response format across all tools
- ✅ Structured error handling
- ✅ User data isolation through user_id
- ✅ Input validation at tool boundaries
- ✅ Stateless operation (no server memory)

Ready for implementation phase.
