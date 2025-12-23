# AI Chatbot Integration Guide

## Overview

The todo-application now includes an **AI-powered chatbot** that allows users to manage tasks using natural language. The chatbot appears as a floating widget in the bottom-right corner of the dashboard.

## Features

- **Natural Language Task Management**: Add, complete, delete, and list tasks using conversational language
- **Smart Task Understanding**: The AI understands context and intent
- **Real-time Task Updates**: When the chatbot creates or modifies tasks, the dashboard automatically refreshes
- **Persistent Conversations**: Chat history is maintained across sessions
- **Modern UI**: Beautiful floating chat widget that matches the TodoFlow design

## Architecture

### Components

1. **Frontend Integration** (`todo-application/frontend`)
   - `components/chatbot/FloatingChatWidget.tsx` - Main chat UI component
   - `lib/api/chatbot/api.ts` - API client for chatbot backend

2. **Backend Services**
   - **Main API**: `todo-application/backend` (Port 8000) - Handles task CRUD operations
   - **Chatbot API**: `chatbot/backend` (Port 8001) - Handles AI conversations and task commands

## Setup Instructions

### 1. Start the Main Todo Backend

```bash
cd D:\web-todo\todo-application\backend
uvicorn app.main:app --reload --port 8000
```

### 2. Start the Chatbot Backend

```bash
cd D:\web-todo\chatbot\backend
uvicorn app.main:app --reload --port 8001
```

**Important**: The chatbot backend MUST run on port 8001 (or update `NEXT_PUBLIC_CHATBOT_API_URL` in `.env.local`)

### 3. Start the Frontend

```bash
cd D:\web-todo\todo-application\frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## Environment Configuration

### Frontend (`.env.local`)

```env
# Main Todo API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Chatbot API (separate backend)
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:8001

# Other configurations...
```

### Chatbot Backend (`.env`)

Make sure the chatbot backend has:
- `DATABASE_URL` configured (PostgreSQL connection)
- `OPENAI_API_KEY` configured (for AI functionality)
- `FRONTEND_URL=http://localhost:3000` (for CORS)

## Usage

### Opening the Chatbot

1. Log in to the todo application
2. Navigate to the dashboard
3. Click the purple chat icon (💬) in the bottom-right corner

### Example Commands

- **Add Task**: "Add buy groceries to my list"
- **List Tasks**: "Show me all my tasks"
- **Complete Task**: "Mark the first task as done"
- **Delete Task**: "Delete the meeting task"
- **High Priority**: "Add urgent: fix the bug with high priority"

### How It Works

1. User types a message in the chat widget
2. Message is sent to the chatbot backend API (`/api/{userId}/chat`)
3. AI processes the message and executes tool calls (create_task, list_tasks, etc.)
4. Response is displayed in the chat
5. If tasks were modified, the dashboard automatically refreshes

## Troubleshooting

### Chatbot Not Responding

1. **Check Chatbot Backend**: Ensure it's running on port 8001
   ```bash
   # Should show the chatbot backend
   curl http://localhost:8001/docs
   ```

2. **Check Environment Variables**: Verify `NEXT_PUBLIC_CHATBOT_API_URL` is set correctly

3. **Check Browser Console**: Look for CORS or network errors

### CORS Issues

If you see CORS errors, ensure the chatbot backend's `FRONTEND_URL` environment variable matches your frontend URL.

### Database Connection

The chatbot backend needs database access to create/modify tasks. Ensure:
- Database is running
- `DATABASE_URL` is configured correctly
- Database migrations are applied: `alembic upgrade head`

## API Endpoints

### Chatbot Backend

- `POST /api/{userId}/chat` - Send a message to the chatbot
  ```json
  {
    "message": "Add buy groceries",
    "conversation_id": null
  }
  ```

- `GET /api/{userId}/conversations` - Get conversation history

### Main Backend

- Standard task CRUD endpoints (used by both UI and chatbot)
- `GET /api/{userId}/tasks`
- `POST /api/{userId}/tasks`
- `PUT /api/{userId}/tasks/{taskId}`
- `DELETE /api/{userId}/tasks/{taskId}`

## Development Notes

- The chatbot automatically refreshes the task list after performing task operations
- Conversation state is persisted in `localStorage`
- The widget uses Framer Motion for smooth animations
- All chatbot API calls include the user ID for authentication/authorization

## Future Enhancements

- Voice input support
- Task scheduling via natural language ("remind me tomorrow")
- Task search and filtering via chat
- Multi-language support
- Custom AI personalities
