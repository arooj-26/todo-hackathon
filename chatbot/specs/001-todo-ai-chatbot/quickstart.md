# Quickstart Guide: AI-Powered Todo Chatbot

**Date**: 2025-12-21
**Feature**: 001-todo-ai-chatbot
**Purpose**: Quick setup and development guide for the todo chatbot

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ and npm installed
- Git installed
- Neon PostgreSQL account (free tier sufficient)
- OpenAI API key with GPT-4 access

## Project Structure

```
chatbot/
├── backend/          # FastAPI server
├── frontend/         # Next.js + ChatKit UI
├── specs/            # Feature specifications
├── .specify/         # Project governance
└── history/          # PHRs and ADRs
```

## Backend Setup (FastAPI + MCP + Agent)

### 1. Navigate to Backend

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
openai==1.6.1
mcp-sdk==0.1.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
pydantic==2.5.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

### 4. Configure Environment

Create `.env` file in `backend/`:
```env
# Database
DATABASE_URL=postgresql://user:password@host.neon.tech/chatbot_db

# OpenAI
OPENAI_API_KEY=sk-...

# Server
HOST=0.0.0.0
PORT=8000

# Frontend (for CORS)
FRONTEND_URL=http://localhost:3000
```

**Get Neon Connection String**:
1. Go to https://neon.tech
2. Create new project: "todo-chatbot"
3. Copy connection string from dashboard
4. Paste into DATABASE_URL

### 5. Initialize Database

```bash
# Create tables
python -m src.database.init_db

# Verify connection
python -c "from src.database.connection import engine; print('Database connected!')"
```

### 6. Run Backend Server

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify**: Open http://localhost:8000/docs (FastAPI auto-generated docs)

### 7. Test MCP Tools (Optional)

```bash
# Run tool tests
pytest tests/contract/test_mcp_tools.py -v

# Run integration tests
pytest tests/integration/test_chat_endpoint.py -v
```

---

## Frontend Setup (Next.js + ChatKit)

### 1. Navigate to Frontend

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

**package.json** (key dependencies):
```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@openai/chatkit": "^1.0.0",
    "axios": "^1.6.2"
  }
}
```

### 3. Configure Environment

Create `.env.local` file in `frontend/`:
```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit (leave empty for localhost development)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=

# Hardcoded user ID for MVP (replace with auth later)
NEXT_PUBLIC_USER_ID=550e8400-e29b-41d4-a716-446655440000
```

### 4. Run Frontend

```bash
npm run dev
```

**Verify**: Open http://localhost:3000

---

## Using the Chatbot

### Start a Conversation

1. Open frontend at http://localhost:3000
2. Type natural language commands:
   - "Add buy groceries to my todo list"
   - "What do I need to do?"
   - "Mark task 1 as complete"
   - "Delete the meeting task"
   - "Change task 2 to 'call mom tonight'"

### Example Interaction

```
User: "I need to remember to buy milk and eggs"
Assistant: "I've added 'Buy milk and eggs' to your tasks!"

User: "What's on my list?"
Assistant: "You have 1 task:
1. Buy milk and eggs (pending, medium priority)"

User: "Mark it as done"
Assistant: "Great! I've marked 'Buy milk and eggs' as complete."
```

---

## Development Workflow

### Test-First Development (Required by Constitution)

1. **Write Tests First** (Red)
   ```bash
   # Example: Add test for new MCP tool
   cd backend
   pytest tests/contract/test_update_task.py -v
   # Should FAIL (not implemented yet)
   ```

2. **Implement Feature** (Green)
   ```bash
   # Implement the MCP tool
   # Edit: src/mcp/tools/update_task.py
   ```

3. **Run Tests** (Green)
   ```bash
   pytest tests/contract/test_update_task.py -v
   # Should PASS now
   ```

4. **Refactor** (Refactor)
   ```bash
   # Clean up code while tests still pass
   ```

### Making Changes

**Backend Changes**:
```bash
cd backend
# Edit files in src/
uvicorn src.api.main:app --reload  # Auto-reloads on changes
```

**Frontend Changes**:
```bash
cd frontend
# Edit files in src/
npm run dev  # Auto-reloads on changes
```

**Database Changes**:
```bash
cd backend
# Create migration
alembic revision --autogenerate -m "Add new field"
# Apply migration
alembic upgrade head
```

---

## Project Commands

### Backend

```bash
# Start server
uvicorn src.api.main:app --reload

# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/

# Type checking
mypy src/

# Code formatting
black src/
isort src/

# Database migrations
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

### Frontend

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint
```

---

## Common Development Tasks

### Add a New MCP Tool

1. Create tool file: `backend/src/mcp/tools/new_tool.py`
2. Define Pydantic schemas for parameters and response
3. Implement tool function with database operations
4. Register tool in `backend/src/mcp/server.py`
5. Write contract tests in `tests/contract/`
6. Test with agent via chat endpoint

### Add a New Test

```bash
cd backend
# Create test file
touch tests/integration/test_new_feature.py

# Write test (see existing tests for examples)
# Run test
pytest tests/integration/test_new_feature.py -v
```

### Debug Agent Responses

**Enable Agent Logging**:
```python
# In backend/src/agent/chat_agent.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check Tool Calls**:
```bash
# Tool calls are returned in API response
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}' | jq '.tool_calls'
```

---

## Troubleshooting

### Database Connection Fails

```bash
# Check Neon status
curl https://neon.tech/api/health

# Verify connection string
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('DATABASE_URL'))"

# Test connection
python -c "from src.database.connection import engine; engine.connect()"
```

### OpenAI API Errors

```bash
# Verify API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10])"

# Check quota
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Agent Not Calling Tools

- Check tool descriptions are clear
- Verify tool parameters match spec
- Enable debug logging to see agent reasoning
- Test tools independently via contract tests

### Frontend Can't Connect to Backend

- Verify backend is running on port 8000
- Check CORS configuration in backend
- Verify NEXT_PUBLIC_API_URL is correct
- Check browser console for errors

---

## Production Deployment (Future)

### Backend Deployment (e.g., Railway, Render)

1. Set environment variables in platform
2. Update DATABASE_URL to production Neon connection
3. Set FRONTEND_URL to production frontend domain
4. Deploy via Git push or Docker
5. Run database migrations

### Frontend Deployment (e.g., Vercel)

1. Connect GitHub repository
2. Configure environment variables
3. Add domain to OpenAI allowlist
4. Get domain key from OpenAI
5. Set NEXT_PUBLIC_OPENAI_DOMAIN_KEY
6. Deploy

### Database (Neon Production)

- Upgrade to Neon Pro for production SLA
- Enable connection pooling
- Set up database backups
- Monitor connection usage

---

## Next Steps

1. ✅ Complete `/sp.plan` (this document is part of planning)
2. Run `/sp.tasks` to generate implementation task list
3. Run `/sp.implement` to execute tasks via Claude Code
4. Test each feature thoroughly
5. Document any architectural decisions with `/sp.adr`

---

## Support & Resources

- **Spec**: `specs/001-todo-ai-chatbot/spec.md`
- **Plan**: `specs/001-todo-ai-chatbot/plan.md`
- **Data Model**: `specs/001-todo-ai-chatbot/data-model.md`
- **Contracts**: `specs/001-todo-ai-chatbot/contracts/`
- **Constitution**: `.specify/memory/constitution.md`
- **OpenAI Agents SDK**: https://github.com/openai/agents-sdk
- **MCP Spec**: https://modelcontextprotocol.org
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Neon Docs**: https://neon.tech/docs

---

**Ready to build!** Follow the Agentic Dev Stack: Spec → Plan (you are here) → Tasks → Implement.
