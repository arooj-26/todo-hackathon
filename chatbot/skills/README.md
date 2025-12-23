# MCP Tools - Todo AI Chatbot

This directory contains MCP (Model Context Protocol) server tools that expose task management operations to the AI agent.

## Overview

These tools provide a standardized interface for the AI agent to interact with the todo task system. All tools follow the MCP protocol specification and use Pydantic validation for type safety.

## Available Tools

### 1. `add_task`
**Purpose**: Create a new todo task

**Parameters**:
- `user_id` (UUID4): User who owns the task
- `title` (str): Task title (1-500 chars)
- `description` (Optional[str]): Detailed description (max 10,000 chars)
- `due_date` (Optional[datetime]): Due date in ISO 8601 format
- `priority` (Priority): 'low', 'medium', or 'high' (default: 'medium')

**Returns**: `{task_id, status, title, error}`

### 2. `list_tasks`
**Purpose**: Retrieve tasks with optional filters

**Parameters**:
- `user_id` (UUID4): User whose tasks to list
- `status` (TaskStatus): 'all', 'pending', or 'completed' (default: 'all')
- `priority` (Optional[Priority]): Filter by priority level
- `sort_by` (SortBy): 'created_at', 'due_date', or 'priority' (default: 'created_at')

**Returns**: `{tasks: [...], count, error}`

### 3. `complete_task`
**Purpose**: Mark a task as complete

**Parameters**:
- `user_id` (UUID4): User who owns the task
- `task_id` (UUID4): Task to mark complete

**Returns**: `{task_id, status, title, error}`

**Note**: This tool is idempotent - completing an already-completed task returns success.

### 4. `delete_task`
**Purpose**: Permanently delete a task

**Parameters**:
- `user_id` (UUID4): User who owns the task
- `task_id` (UUID4): Task to delete

**Returns**: `{task_id, status, title, error}`

**Note**: This action is irreversible. The AI should confirm before deleting important tasks.

### 5. `update_task`
**Purpose**: Modify task attributes (partial update)

**Parameters**:
- `user_id` (UUID4): User who owns the task
- `task_id` (UUID4): Task to update
- `title` (Optional[str]): New title
- `description` (Optional[str]): New description
- `priority` (Optional[Priority]): New priority
- `due_date` (Optional[datetime]): New due date

**Returns**: `{task_id, status, title, error}`

**Note**: Only provided fields are updated. This is a partial update operation.

## Type Safety

All tools use Pydantic validation with:
- **UUID4** for all entity IDs (user_id, task_id)
- **Enum types** for priority and status (string-based enums)
- **datetime** objects for temporal data (ISO 8601 format)
- **Field validation** for string lengths and constraints

## Error Handling

All tools return a consistent response structure with:
- `status`: Operation status ('created', 'updated', 'completed', 'deleted', or 'error')
- `error`: Error message (null on success, descriptive string on failure)

## Usage Example

```python
from skills import add_task, AddTaskParams, Priority
from uuid import UUID
from datetime import datetime

# Create a new task
params = AddTaskParams(
    user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
    title="Buy groceries",
    description="Milk, eggs, bread",
    priority=Priority.HIGH,
    due_date=datetime(2025, 12, 22, 12, 0, 0)
)

result = add_task(params)
# Returns: {'task_id': '...', 'status': 'created', 'title': 'Buy groceries', 'error': None}
```

## Implementation Status

All tool functions are currently stubs with TODO comments. Implementation will be added during the `/sp.implement` phase using the Agentic Dev Stack workflow.

## Contract Specification

Full MCP tool contract specifications are documented in:
- `specs/001-todo-ai-chatbot/contracts/mcp-tools.md`
- `specs/001-todo-ai-chatbot/data-model.md`

## AI Agent Behavior

The AI agent should:
1. Extract user intent from natural language
2. Map to appropriate MCP tool
3. Parse parameters intelligently (dates, priorities, task references)
4. Call `list_tasks` first when user references tasks by position or name
5. Confirm actions with friendly messages
6. Handle errors gracefully
