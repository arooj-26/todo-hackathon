# Research: AI-Powered Todo Chatbot

**Date**: 2025-12-21
**Feature**: 001-todo-ai-chatbot
**Purpose**: Research best practices and technical decisions for implementing the conversational todo chatbot

## Technology Stack Research

### 1. OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK (beta) for natural language interpretation and tool orchestration

**Rationale**:
- Official OpenAI framework for building AI agents with tool-calling capabilities
- Native support for function/tool calling which maps directly to MCP tools
- Manages conversation context and message history automatically
- Handles retry logic and error recovery
- Provides streaming responses for better UX

**Alternatives Considered**:
- Direct OpenAI Chat Completions API: More manual work, less structured for agents
- LangChain: Additional abstraction layer, heavier dependency
- Custom implementation: Reinventing the wheel, higher maintenance

**Best Practices**:
- Initialize agent once per request with fresh conversation history from database
- Pass conversation history as messages array (user/assistant roles)
- Register MCP tools as agent functions with clear descriptions
- Use structured output for tool responses (Pydantic models)
- Handle agent errors gracefully (timeouts, API failures, invalid tool calls)

**Implementation Pattern**:
```python
from openai import OpenAI
from openai.agents import Agent

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create agent with tools
agent = Agent(
    model="gpt-4o",
    tools=[add_task_tool, list_tasks_tool, complete_task_tool, delete_task_tool, update_task_tool],
    instructions="You are a helpful assistant for managing todo tasks..."
)

# Run agent with conversation history
response = agent.run(
    messages=conversation_history + [{"role": "user", "content": user_message}]
)
```

### 2. Model Context Protocol (MCP) Server

**Decision**: Use Official MCP Python SDK for exposing task operations as tools

**Rationale**:
- Standardized protocol for AI-tool interaction
- Clear separation between AI logic and business logic
- Tools are discoverable and self-documenting
- Supports typed parameters and responses
- Future-proof for multi-model support

**Alternatives Considered**:
- Direct function registration: Less standardized, harder to maintain
- REST API for tools: Additional HTTP overhead, less efficient
- Custom tool protocol: Non-standard, reinventing standards

**Best Practices**:
- Each tool should be a pure function (no side effects beyond database)
- Validate all inputs at tool boundaries
- Return structured responses (success/error status)
- Use Pydantic models for tool parameters and responses
- Tools should be idempotent where applicable (delete, complete)
- Include detailed tool descriptions for AI agent understanding

**Implementation Pattern**:
```python
from mcp import Server, Tool
from pydantic import BaseModel

class AddTaskParams(BaseModel):
    user_id: str
    title: str
    description: str | None = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    title: str

@server.tool(
    name="add_task",
    description="Create a new task for the user",
    parameters=AddTaskParams
)
async def add_task(params: AddTaskParams) -> TaskResponse:
    # Implementation
    pass
```

### 3. FastAPI Stateless Architecture

**Decision**: Implement fully stateless FastAPI endpoints with database-backed sessions

**Rationale**:
- Horizontal scaling requires no server affinity
- Server restarts lose no state
- Simplifies deployment and load balancing
- Aligns with constitution Principle II

**Best Practices**:
- Use dependency injection for database sessions
- Retrieve conversation history on each request
- No global variables for user state
- Use connection pooling for database efficiency
- Implement proper request scoping with context managers

**Implementation Pattern**:
```python
from fastapi import FastAPI, Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    # Fetch conversation from database
    conversation = get_or_create_conversation(session, user_id, request.conversation_id)

    # Fetch message history
    messages = get_conversation_messages(session, conversation.id)

    # Store user message
    store_message(session, conversation.id, "user", request.message)

    # Run agent (stateless)
    response = await run_agent(messages + [{"role": "user", "content": request.message}])

    # Store assistant response
    store_message(session, conversation.id, "assistant", response)

    return {"conversation_id": conversation.id, "response": response}
```

### 4. SQLModel for Database Interactions

**Decision**: Use SQLModel for type-safe ORM with Pydantic validation

**Rationale**:
- Combines SQLAlchemy ORM with Pydantic validation
- Type hints for IDE support and type checking
- Automatic validation of data
- Native async support
- Minimal boilerplate

**Best Practices**:
- Define models with proper relationships
- Use UUID for primary keys (better distribution, no collision)
- Add appropriate indexes for query patterns
- Use timestamps for created_at/updated_at
- Implement soft deletes if needed (not required for MVP)

**Implementation Pattern**:
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(index=True)
    title: str = Field(max_length=500)
    description: str | None = None
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = (
        Index("idx_user_completed", "user_id", "completed"),
    )
```

### 5. Neon Serverless PostgreSQL

**Decision**: Use Neon for serverless PostgreSQL database

**Rationale**:
- Serverless architecture aligns with stateless backend
- Automatic scaling and connection pooling
- Built-in branching for development/staging
- Cost-effective for variable workloads
- PostgreSQL compatibility

**Best Practices**:
- Use connection pooling (built-in with Neon)
- Set appropriate connection limits
- Use prepared statements (automatic with SQLAlchemy)
- Monitor connection usage
- Use environment variables for connection strings

**Connection Pattern**:
```python
from sqlmodel import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for debugging
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,  # Adjust based on load
    max_overflow=10
)
```

### 6. OpenAI ChatKit Frontend

**Decision**: Use OpenAI ChatKit for conversational UI

**Rationale**:
- Official OpenAI component for chat interfaces
- Handles message rendering, input, streaming
- Consistent UX with OpenAI products
- Minimal setup required

**Best Practices**:
- Configure domain allowlist for production deployment
- Use environment variables for API keys
- Implement proper error handling for network failures
- Handle conversation_id persistence (localStorage or URL)
- Provide loading states during agent processing

**Integration Pattern**:
```typescript
import { ChatKit } from '@openai/chatkit'

export default function ChatInterface() {
  return (
    <ChatKit
      apiUrl={process.env.NEXT_PUBLIC_API_URL}
      domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
      onMessage={async (message) => {
        const response = await fetch('/api/chat', {
          method: 'POST',
          body: JSON.stringify({ message })
        })
        return response.json()
      }}
    />
  )
}
```

## Architecture Decisions

### Request Flow Architecture

**Decision**: Single POST endpoint with agent orchestration

**Data Flow**:
1. Client sends user message + optional conversation_id
2. Backend fetches/creates conversation record
3. Backend fetches conversation message history
4. Backend stores new user message
5. Backend initializes agent with history + new message
6. Agent interprets intent, calls MCP tools
7. MCP tools execute database operations
8. Agent generates natural language response
9. Backend stores assistant response
10. Backend returns conversation_id + response

**Benefits**:
- Single API contract simplifies frontend
- Conversation history automatically maintained
- Agent handles routing to tools
- Stateless server enables horizontal scaling

### Error Handling Strategy

**Decision**: Layered error handling with conversational fallbacks

**Layers**:
1. **Tool Layer**: Validate inputs, return structured errors
2. **Agent Layer**: Translate tool errors into natural language
3. **API Layer**: Handle agent failures, database errors
4. **Client Layer**: Display errors gracefully, retry logic

**Example Error Flow**:
```
User: "Delete task 999"
→ Tool: Task not found (structured error)
→ Agent: "I couldn't find task 999. Would you like to see your tasks?"
→ API: Returns success with conversational error message
→ Client: Displays agent's helpful message
```

### Data Isolation Strategy

**Decision**: user_id as primary isolation boundary

**Implementation**:
- All queries filter by user_id
- Conversation and Task models include user_id
- Database-level constraints (foreign keys reference user tables if auth added later)
- No cross-user data access at any layer

## Testing Strategy

### Unit Tests (pytest)
- Test each MCP tool independently with mock database
- Test database models (creation, validation, relationships)
- Test utility functions

### Contract Tests
- Verify MCP tool interfaces match specifications
- Test tool parameter validation
- Test tool response schemas

### Integration Tests (pytest + httpx)
- Test FastAPI endpoints with test database
- Test conversation flow (create, retrieve, update)
- Test agent + tool integration
- Test error handling paths

### End-to-End Tests
- Test full conversational flows
- Test conversation resumption after "restart" (clear server state)
- Test concurrent user scenarios
- Test edge cases from specification

## Security Considerations

### Input Validation
- All MCP tool parameters validated via Pydantic
- SQL injection prevented by SQLModel parameterization
- XSS prevention through proper frontend escaping (ChatKit handles)

### Data Privacy
- user_id isolation at all data access points
- No logging of sensitive user data
- Secure environment variable management

### Authentication (Future)
- Better Auth integration placeholder
- user_id currently passed as URL parameter (insecure, MVP only)
- Production requires proper authentication middleware

## Performance Optimization

### Database Query Optimization
- Appropriate indexes on user_id, conversation_id, completed status
- Limit conversation history retrieval (e.g., last 50 messages)
- Use connection pooling

### Caching Strategy (Future)
- Not required for MVP (YAGNI principle)
- Consider caching conversation history if performance degrades
- Redis could be added later if needed

### Concurrency Handling
- FastAPI async endpoints for I/O-bound operations
- Database connection pooling
- Async database operations with SQLModel + asyncpg

## Development Environment Setup

### Required Environment Variables
```
DATABASE_URL=postgresql://user:pass@host/db
OPENAI_API_KEY=sk-...
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=domain-key (production only)
```

### Development Workflow
1. Backend: `uvicorn src.api.main:app --reload`
2. Frontend: `npm run dev`
3. Database: Neon connection (no local PostgreSQL needed)
4. Tests: `pytest` (backend), `npm test` (frontend)

## Conclusion

All technical decisions align with project constitution principles and enable delivery of the specified features. The architecture supports:
- Stateless horizontal scaling
- 100% conversation persistence
- Natural language interaction via Agents SDK
- Modular tool-based task operations
- Type-safe database interactions
- Test-first development approach

No unresolved questions remain - ready to proceed to Phase 1 (data models and contracts).
