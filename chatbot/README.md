# AI-Powered Todo Chatbot

A conversational AI assistant for managing todo tasks through natural language. Built with FastAPI, OpenAI API, Next.js, and PostgreSQL using the Model Context Protocol (MCP) architecture.

## Features

✅ **Natural Language Task Management**
- Create tasks: "Add buy groceries to my list"
- List tasks: "Show me what I need to do"
- Complete tasks: "Mark the meeting as done"
- Delete tasks: "Remove the grocery task"
- Update tasks: "Change task to 'Call mom tonight'"

✅ **Intelligent Conversation**
- Context-aware responses
- Handles ambiguous requests by asking clarifying questions
- Multi-step operations in single requests
- Conversational task filtering and search

✅ **Persistent Conversations**
- Resume conversations across sessions
- Full conversation history stored
- No data loss on server restart

✅ **Production Ready**
- Request logging and monitoring
- Rate limiting (60 req/min per user)
- Health checks and error handling
- Stateless architecture for horizontal scaling
- Comprehensive test coverage

## Architecture

### Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- OpenAI API with function calling for natural language understanding
- Model Context Protocol (MCP) SDK for tool abstraction
- PostgreSQL (Neon) for data persistence
- SQLModel for type-safe database operations
- Pydantic for request/response validation

**Frontend:**
- Next.js 14 with TypeScript
- React 18 for UI components
- OpenAI ChatKit-like interface
- Server-side rendering support
- Responsive design

**Testing:**
- pytest for backend (33 contract tests, unit tests, E2E tests)
- Jest + React Testing Library for frontend
- 80%+ code coverage target

### System Design

```
┌─────────────┐
│   Browser   │
│  (Next.js)  │
└──────┬──────┘
       │ HTTP/JSON
       ↓
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌─────────────────────────────┐   │
│  │  POST /api/{user_id}/chat   │   │
│  └────────────┬────────────────┘   │
│               │                     │
│  ┌────────────↓─────────────┐      │
│  │   OpenAI Agent API       │      │
│  │   - Natural language     │      │
│  │   - Function calling     │      │
│  └────────────┬─────────────┘      │
│               │                     │
│  ┌────────────↓─────────────┐      │
│  │      MCP Tools           │      │
│  │  • add_task              │      │
│  │  • list_tasks            │      │
│  │  • complete_task         │      │
│  │  • delete_task           │      │
│  │  • update_task           │      │
│  └────────────┬─────────────┘      │
└───────────────┼──────────────────────┘
                │
                ↓
        ┌───────────────┐
        │  PostgreSQL   │
        │    (Neon)     │
        │               │
        │  • tasks      │
        │  • messages   │
        │  • convos     │
        └───────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database (Neon recommended)
- OpenAI API key with GPT-4o access

### Backend Setup

1. **Clone and navigate**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create `backend/.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host/dbname
   OPENAI_API_KEY=sk-your-key-here
   FRONTEND_URL=http://localhost:3000
   ```

5. **Initialize database**
   ```bash
   python -c "
   from sqlmodel import SQLModel, create_engine
   from src.models.task import Task
   from src.models.conversation import Conversation
   from src.models.message import Message
   import os
   from dotenv import load_dotenv

   load_dotenv()
   engine = create_engine(os.getenv('DATABASE_URL'))
   SQLModel.metadata.create_all(engine)
   print('✅ Database initialized!')
   "
   ```

6. **Run backend**
   ```bash
   uvicorn src.api.main:app --reload --port 8001
   ```

   Backend will be available at `http://localhost:8001`
   - API Docs: `http://localhost:8001/docs`
   - Health Check: `http://localhost:8001/health`

**Note**: If you have other applications running on port 8000 (such as the original Todo API), use port 8001 or another available port to avoid conflicts.

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run frontend**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:3000`

### Verify Installation

1. Open `http://localhost:3000`
2. Try: "Add buy groceries to my list"
3. Then: "Show me my tasks"
4. Verify task appears

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/contract/    # Contract tests
pytest tests/unit/        # Unit tests
pytest tests/integration/ # Integration tests
pytest tests/e2e/         # End-to-end tests
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

## API Documentation

### Chat Endpoint

**POST** `/api/{user_id}/chat`

Send a message and get AI response with task operations.

**Request:**
```json
{
  "message": "Add buy groceries to my list",
  "conversation_id": "uuid-here-or-null"
}
```

**Response:**
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
        "task_id": "...",
        "status": "created",
        "title": "Buy groceries",
        "error": null
      }
    }
  ],
  "error": null
}
```

### List Conversations

**GET** `/api/{user_id}/conversations`

Get recent conversations for a user.

**Response:**
```json
{
  "conversations": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2025-12-21T10:00:00Z",
      "updated_at": "2025-12-21T10:30:00Z"
    }
  ],
  "count": 1
}
```

## MCP Tools

The system exposes 5 MCP tools that the AI agent can use:

### 1. add_task
Create a new todo task

**Parameters:**
- `user_id` (string, required)
- `title` (string, required, 1-500 chars)
- `description` (string, optional)

### 2. list_tasks
List tasks with filters

**Parameters:**
- `user_id` (string, required)
- `status` (all/pending/completed, default: all)

### 3. complete_task
Mark a task as complete (idempotent)

**Parameters:**
- `user_id` (string, required)
- `task_id` (integer, required)

### 4. delete_task
Permanently delete a task

**Parameters:**
- `user_id` (string, required)
- `task_id` (integer, required)

### 5. update_task
Update task properties (partial updates supported)

**Parameters:**
- `user_id` (string, required)
- `task_id` (integer, required)
- `title` (string, optional)
- `description` (string, optional)

## Project Structure

```
chatbot/
├── backend/
│   ├── src/
│   │   ├── agent/          # OpenAI agent logic
│   │   ├── api/            # FastAPI application
│   │   ├── database/       # Database connection
│   │   ├── mcp/            # MCP SDK server and tools
│   │   │   ├── server.py   # MCP server with official SDK
│   │   │   └── tools/      # Individual MCP tool implementations
│   │   └── models/         # SQLModel database models
│   ├── tests/
│   │   ├── contract/       # Tool interface tests
│   │   ├── unit/           # Unit tests
│   │   ├── integration/    # Integration tests
│   │   └── e2e/            # End-to-end tests
│   ├── migrations/         # Database migrations
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   └── ChatInterface.tsx  # OpenAI ChatKit-like interface
│   │   ├── pages/          # Next.js pages
│   │   └── services/       # API client
│   ├── __tests__/         # Frontend tests
│   ├── package.json
│   └── tsconfig.json
├── specs/                  # Feature specifications
│   └── 001-todo-ai-chatbot/
│       ├── spec.md         # Requirements
│       ├── plan.md         # Architecture
│       └── tasks.md        # Implementation tasks
├── README.md
└── DEPLOYMENT.md
```

## Configuration

### Environment Variables

**Backend (`.env`):**
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: Your OpenAI API key
- `FRONTEND_URL`: Frontend URL for CORS (default: http://localhost:3000)

**Frontend (`.env.local`):**
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

### Rate Limiting

Default: 60 requests per minute per user

Configure in `backend/src/api/middleware.py`:
```python
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
```

### Logging

Logs are written to stdout in production-ready format:
```
2025-12-21 10:30:45 - API - INFO - Request: POST /api/123/chat
2025-12-21 10:30:47 - API - INFO - Response: POST /api/123/chat Status: 200 Duration: 1.234s
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions covering:
- Railway/Render deployment
- Vercel frontend deployment
- Database setup and migrations
- Environment configuration
- Monitoring and scaling
- Cost estimates

## Development

### Adding New MCP Tools

1. Create tool in `backend/src/mcp/tools/your_tool.py`
2. Define Pydantic parameter schema
3. Implement tool function
4. Register in `backend/src/mcp/server.py`
5. Write contract and unit tests
6. Update agent instructions if needed

### Database Migrations

For schema changes:
1. Create migration file in `backend/migrations/`
2. Test locally
3. Apply to production database
4. Update SQLModel models

## Troubleshooting

### Common Issues

**"OpenAI API key not configured"**
- Ensure `OPENAI_API_KEY` is set in backend `.env`
- Restart backend server

**"Database connection failed"**
- Verify `DATABASE_URL` is correct
- Check database is running and accessible
- Ensure database schema is initialized

**"CORS error in browser"**
- Verify `FRONTEND_URL` matches your frontend exactly
- Check backend CORS middleware configuration

**"Rate limit exceeded"**
- Wait 1 minute and try again
- Or increase limit in `middleware.py`

### Getting Help

1. Check API documentation: `http://localhost:8000/docs`
2. View backend logs for errors
3. Check browser console for frontend errors
4. Verify environment variables are set correctly

## Contributing

1. Follow test-first development (Red-Green-Refactor)
2. Maintain 80%+ test coverage
3. Update documentation for new features
4. Follow existing code style

## License

Proprietary - All rights reserved

## Acknowledgments

- OpenAI for GPT-4 API
- FastAPI framework
- Next.js framework
- Neon for serverless PostgreSQL
