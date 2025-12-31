# Todo Chatbot Backend

AI-powered conversational interface for managing todos through natural language using FastAPI, OpenAI API with function calling, and MCP (Model Context Protocol) SDK server architecture.

## Prerequisites

- Python 3.11+ installed
- Neon PostgreSQL account (free tier sufficient)
- OpenAI API key with GPT-4 access

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```env
# Database - Get from https://neon.tech dashboard
DATABASE_URL=postgresql://user:password@host.neon.tech/chatbot_db

# OpenAI API key
OPENAI_API_KEY=sk-your-api-key-here

# Application settings
ENVIRONMENT=development
LOG_LEVEL=INFO
FRONTEND_URL=http://localhost:3000
```

### 4. Initialize Database

Run the database migration:

```bash
# Apply migrations
python -c "from sqlmodel import SQLModel; from src.database.connection import engine; SQLModel.metadata.create_all(engine)"
```

Or use the migration script:

```bash
psql $DATABASE_URL < migrations/001_initial_schema.sql
```

### 5. Run Development Server

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8001
```


Server will be available at `http://localhost:8001`

API documentation: `http://localhost:8001/docs`

**Note**: If you have other applications running on port 8000 (such as the original Todo API), use port 8001 or another available port to avoid conflicts.

## Testing

Run all tests with coverage:

```bash
pytest
```

Run specific test categories:

```bash
# Unit tests only
pytest -m unit

# Integration tests
pytest -m integration

# Contract tests
pytest -m contract

# End-to-end tests
pytest -m e2e
```

## Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel database models (with integer IDs)
│   ├── mcp/             # MCP SDK server and tools
│   │   ├── server.py    # MCP server using official SDK
│   │   └── tools/       # Individual MCP tool implementations
│   ├── api/             # FastAPI application
│   ├── agent/           # OpenAI API agent with function calling
│   └── database/        # Database configuration
├── tests/
│   ├── contract/        # MCP tool contract tests
│   ├── integration/     # FastAPI + database + agent tests
│   ├── unit/            # Individual function tests
│   └── e2e/             # End-to-end conversational flows
├── migrations/          # Database migration scripts
├── requirements.txt     # Python dependencies
└── pytest.ini           # Pytest configuration
```

## Architecture

- **Stateless**: All conversation context retrieved from database on each request
- **MCP Tools**: Task operations (add, list, complete, delete, update) as standardized tools using official MCP SDK
- **OpenAI Agent**: Interprets natural language and orchestrates tool calls via function calling
- **FastAPI**: Single POST /api/{user_id}/chat endpoint
- **SQLModel + PostgreSQL**: Type-safe ORM with integer primary keys and Neon serverless database

## Development Workflow

This project follows Test-First Quality (Red-Green-Refactor):

1. **RED**: Write test first (should FAIL)
2. **GREEN**: Implement code to make test PASS
3. **REFACTOR**: Improve code while keeping tests green

All implementation must have corresponding tests before being considered complete.

## API Endpoint

**POST /api/{user_id}/chat**

Request:
```json
{
  "conversation_id": "uuid-or-null",
  "message": "add buy groceries to my tasks"
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "response": "I've added 'Buy groceries' to your tasks!",
  "tool_calls": [...],
  "error": null
}
```

## Troubleshooting

**Database Connection Issues:**
- Verify DATABASE_URL is correct
- Check Neon project is active
- Ensure connection string includes password

**OpenAI API Errors:**
- Verify OPENAI_API_KEY is valid
- Check API quota/billing
- Ensure GPT-4 access

**Import Errors:**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

## Contributing

Follow the Test-First Quality principle:
1. Write failing tests first
2. Implement minimum code to pass
3. Refactor while keeping tests green
4. Ensure 80%+ code coverage
