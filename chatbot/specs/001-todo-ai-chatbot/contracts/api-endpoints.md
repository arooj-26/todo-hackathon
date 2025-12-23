# FastAPI Endpoints Contract: AI-Powered Todo Chatbot

**Date**: 2025-12-21
**Feature**: 001-todo-ai-chatbot
**Purpose**: Define HTTP API contracts for frontend-backend communication

## Overview

The FastAPI backend exposes a single chat endpoint that handles all user interactions. The stateless architecture retrieves conversation context from the database on each request and orchestrates the AI agent with MCP tools.

## Base Configuration

**Base URL**: `http://localhost:8000` (development)
**API Version**: v1 (implicit, no version in path for MVP)
**Content-Type**: `application/json`
**CORS**: Enabled for frontend origin

## Endpoints

### POST /api/{user_id}/chat

Processes a user message and returns an AI-generated response.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | string (UUID) | Yes | User identifier (from authentication) |

**Request Body**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `conversation_id` | string (UUID) | No | Valid UUID if provided | Existing conversation to continue (null for new conversation) |
| `message` | string | Yes | 1-5000 chars, non-empty | User's natural language message |

**Request Schema (Pydantic)**:
```python
from pydantic import BaseModel, Field, UUID4

class ChatRequest(BaseModel):
    conversation_id: UUID4 | None = Field(None, description="Conversation to continue (null for new)")
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
```

**Request Example**:
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Add buy groceries to my todo list"
}
```

**Response Body**:

| Field | Type | Description |
|-------|------|-------------|
| `conversation_id` | string (UUID) | The conversation ID (new or existing) |
| `response` | string | AI assistant's natural language response |
| `tool_calls` | array | List of MCP tools invoked (for debugging/transparency) |
| `error` | string | Error message if request failed (null on success) |

**Tool Call Object**:
```json
{
  "tool": "add_task",
  "parameters": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries"
  },
  "result": {
    "task_id": "789e4567-e89b-12d3-a456-426614174000",
    "status": "created",
    "title": "Buy groceries"
  }
}
```

**Response Schema (Pydantic)**:
```python
from pydantic import BaseModel, Field, UUID4

class ToolCall(BaseModel):
    tool: str = Field(..., description="MCP tool name")
    parameters: dict = Field(..., description="Tool parameters")
    result: dict = Field(..., description="Tool execution result")

class ChatResponse(BaseModel):
    conversation_id: UUID4 = Field(..., description="Conversation ID")
    response: str = Field(..., description="AI assistant response")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="Tools invoked")
    error: str | None = Field(None, description="Error message if failed")
```

**Success Response Example**:
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I've added 'Buy groceries' to your tasks!",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Buy groceries"
      },
      "result": {
        "task_id": "789e4567-e89b-12d3-a456-426614174000",
        "status": "created",
        "title": "Buy groceries",
        "error": null
      }
    }
  ],
  "error": null
}
```

**Error Response Example** (Validation Error):
```json
{
  "conversation_id": null,
  "response": "",
  "tool_calls": [],
  "error": "Message cannot be empty"
}
```

**Error Response Example** (Agent Failure):
```json
{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I'm having trouble processing your request right now. Please try again.",
  "tool_calls": [],
  "error": "OpenAI API timeout"
}
```

**HTTP Status Codes**:

| Code | Condition | Response |
|------|-----------|----------|
| 200 | Success (message processed) | ChatResponse with data |
| 400 | Bad request (invalid input) | ChatResponse with error field |
| 401 | Unauthorized (invalid user_id) | Error object |
| 500 | Internal server error | Error object |
| 503 | Service unavailable (database down, OpenAI API down) | Error object |

**Implementation Flow**:

1. **Validate Input**:
   - Check user_id is valid UUID
   - Check message is non-empty and within length limits

2. **Get or Create Conversation**:
   - If conversation_id provided: fetch from database (verify user owns it)
   - If null: create new conversation for user

3. **Retrieve Conversation History**:
   - Fetch last 50 messages from database (or configurable limit)
   - Convert to OpenAI message format: `[{"role": "user", "content": "..."}, ...]`

4. **Store User Message**:
   - Insert new message: `(conversation_id, user_id, role="user", content=message)`
   - Update conversation.updated_at

5. **Run AI Agent**:
   - Initialize agent with MCP tools
   - Pass conversation history + new message
   - Agent invokes tools as needed
   - Collect tool calls for transparency

6. **Store Assistant Response**:
   - Extract final response from agent
   - Insert message: `(conversation_id, user_id, role="assistant", content=response)`
   - Update conversation.updated_at

7. **Return Response**:
   - conversation_id, response, tool_calls

**Error Handling**:

| Error Type | Handling |
|------------|----------|
| Invalid input | Return 400 with validation error message |
| Conversation not found | Return 400 "Conversation not found" |
| User mismatch | Return 401 "Unauthorized" |
| Database connection failure | Return 503 with user-friendly message |
| OpenAI API failure | Return 200 with fallback response + error field |
| Agent timeout | Return 200 with fallback response + error field |

**Fallback Response** (when agent fails):
```
"I'm having trouble processing your request right now. Your message was saved, and you can try again in a moment."
```

---

## Health Check Endpoint (Optional)

### GET /health

Returns server health status.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-21T10:00:00Z"
}
```

**HTTP Status Codes**:
- 200: All systems operational
- 503: Database unreachable or other critical failure

---

## CORS Configuration

**Allowed Origins** (configurable via environment):
- Development: `http://localhost:3000` (Next.js default)
- Production: Frontend deployment URL

**Allowed Methods**: `GET`, `POST`, `OPTIONS`

**Allowed Headers**: `Content-Type`, `Authorization` (for future auth)

**Configuration Example**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

---

## Request/Response Examples

### Example 1: Create First Task

**Request**:
```http
POST /api/550e8400-e29b-41d4-a716-446655440000/chat HTTP/1.1
Content-Type: application/json

{
  "conversation_id": null,
  "message": "I need to buy groceries tomorrow"
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I've added 'Buy groceries' to your tasks for tomorrow!",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Buy groceries",
        "due_date": "2025-12-22T00:00:00Z"
      },
      "result": {
        "task_id": "789e4567-e89b-12d3-a456-426614174000",
        "status": "created",
        "title": "Buy groceries",
        "error": null
      }
    }
  ],
  "error": null
}
```

### Example 2: List Tasks

**Request**:
```http
POST /api/550e8400-e29b-41d4-a716-446655440000/chat HTTP/1.1
Content-Type: application/json

{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "What do I need to do?"
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "You have 2 pending tasks:\n1. Buy groceries (due tomorrow)\n2. Call dentist",
  "tool_calls": [
    {
      "tool": "list_tasks",
      "parameters": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "pending"
      },
      "result": {
        "tasks": [...],
        "count": 2,
        "error": null
      }
    }
  ],
  "error": null
}
```

### Example 3: Error - Task Not Found

**Request**:
```http
POST /api/550e8400-e29b-41d4-a716-446655440000/chat HTTP/1.1
Content-Type: application/json

{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Delete task 999"
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
  "response": "I couldn't find task 999. Would you like to see your current tasks?",
  "tool_calls": [
    {
      "tool": "delete_task",
      "parameters": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "task_id": "999"
      },
      "result": {
        "task_id": "999",
        "status": "error",
        "title": null,
        "error": "Task not found"
      }
    }
  ],
  "error": null
}
```

---

## Authentication (Future Enhancement)

**Current MVP**: user_id passed as path parameter (insecure, development only)

**Future**:
- Add Authorization header with JWT token
- Extract user_id from validated token
- Remove user_id from path parameter
- Add 401 Unauthorized for invalid/expired tokens

**Future Endpoint**:
```
POST /api/chat
Authorization: Bearer <jwt-token>
```

---

## Performance Considerations

**Expected Response Times**:
- Simple operations (add task): <1s
- Complex operations (list + delete): <2s
- Agent processing overhead: ~500ms-1s
- Database query time: <100ms per query

**Optimization Strategies**:
- Connection pooling (5-10 connections)
- Limit conversation history (50 messages)
- Async database operations
- Cache OpenAI client initialization

**Rate Limiting** (Future):
- 10 requests per minute per user
- 100 requests per minute per IP
- Implement with middleware (slowapi or custom)

---

## Testing Contract

**Endpoint Tests Must Verify**:
1. Request/response schemas match Pydantic models
2. HTTP status codes correct for each scenario
3. Conversation creation when conversation_id is null
4. Conversation resumption when conversation_id provided
5. Message persistence to database
6. Tool calls logged in response
7. Error handling for all failure modes
8. CORS headers present

**Example Integration Test**:
```python
def test_chat_endpoint_create_conversation(client, test_user_id):
    response = client.post(
        f"/api/{test_user_id}/chat",
        json={"conversation_id": None, "message": "Add test task"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["response"] is not None
    assert len(data["tool_calls"]) > 0
    assert data["error"] is None
```

---

## Summary

FastAPI endpoints provide:
- ✅ Simple single-endpoint API for frontend
- ✅ Stateless request-response cycle
- ✅ Conversation persistence and resumption
- ✅ Clear error handling with user-friendly messages
- ✅ Tool call transparency for debugging
- ✅ Type-safe request/response validation
- ✅ CORS configuration for frontend integration

Ready for implementation phase.
