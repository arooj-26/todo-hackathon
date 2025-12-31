# ChatKit Integration Setup Guide

This guide walks you through setting up OpenAI ChatKit integration for the Todo AI Dashboard.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Getting Your Domain Key](#getting-your-domain-key)
3. [Configuration](#configuration)
4. [Features](#features)
5. [Customization](#customization)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

- Node.js 18+ installed
- Backend server running (default: `http://localhost:8001`)
- OpenAI account with access to ChatKit

## Getting Your Domain Key

### For Development (localhost)

1. Go to [OpenAI Platform Settings](https://platform.openai.com/settings/organization/security/domain-allowlist)
2. Click "Add domain"
3. Enter `localhost:3000` (or your dev port)
4. Click "Add"
5. Copy the domain key provided
6. Save it for the configuration step

### For Production (Vercel/Other Hosting)

1. Deploy your application first to get the production URL
2. Go to [OpenAI Platform Settings](https://platform.openai.com/settings/organization/security/domain-allowlist)
3. Click "Add domain"
4. Enter your production URL (e.g., `your-app.vercel.app`)
   - **Important:** Do NOT include `https://` or trailing slashes
5. Click "Add"
6. Copy the domain key provided
7. Add it to your production environment variables

## Configuration

### Step 1: Create .env.local

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

### Step 2: Add Your Domain Key

Edit `.env.local` and add your domain key:

```env
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8001

# OpenAI ChatKit Configuration
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-actual-domain-key-here

# User Configuration
NEXT_PUBLIC_DEFAULT_USER_ID=00000000-0000-0000-0000-000000000000

# Feature Flags
NEXT_PUBLIC_USE_CHATKIT=true
```

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Start the Application

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Features

### ChatKit Dashboard

When ChatKit is enabled, you get:

1. **Modern UI**: Professional ChatKit interface with OpenAI styling
2. **Enhanced Chat**: Better message rendering with markdown and code highlighting
3. **Suggestions**: Quick action buttons for common tasks
4. **Theme Customization**: Customizable colors and styling
5. **View Toggle**: Switch between ChatKit and Classic views

### Dashboard Components

The enhanced dashboard includes:

- **Statistics Panel**: Task counts and conversation tracking
- **Quick Actions**: One-click buttons for common operations
- **Help Section**: Inline help and examples
- **Responsive Sidebar**: Collapsible on mobile devices

### Available Suggestions

- "Add buy groceries to my list"
- "Show me all my tasks"
- "Mark the first task as done"
- "Delete the meeting task"
- "What tasks are due today?"
- "Add a task: Call dentist tomorrow at 2pm"
- "Show me completed tasks"
- "Clear all completed tasks"

## Customization

### Theme Configuration

Edit `src/lib/chatkit-config.ts` to customize the theme:

```typescript
export function getDefaultTheme(): ChatKitTheme {
  return {
    primaryColor: '#667eea',        // Main brand color
    backgroundColor: '#ffffff',      // Background
    userMessageColor: '#e3f2fd',    // User message bubble
    assistantMessageColor: '#f5f5f5', // AI message bubble
    fontSize: '16px',
    fontFamily: 'Your preferred font',
    borderRadius: '8px',
  };
}
```

### Feature Toggles

Enable/disable ChatKit features in `src/lib/chatkit-config.ts`:

```typescript
export function getDefaultFeatures(): ChatKitFeatures {
  return {
    suggestions: true,           // Show suggestion chips
    voiceInput: false,          // Voice input (future)
    fileUpload: false,          // File upload (future)
    codeHighlighting: true,     // Syntax highlighting
    markdown: true,             // Markdown rendering
  };
}
```

### Custom Suggestions

Modify suggestions in `src/lib/chatkit-config.ts`:

```typescript
export function getTaskSuggestions(): string[] {
  return [
    "Your custom suggestion 1",
    "Your custom suggestion 2",
    // Add more...
  ];
}
```

## Troubleshooting

### ChatKit Not Loading

**Problem**: Interface falls back to classic view

**Solutions**:
1. Check that `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is set correctly in `.env.local`
2. Verify the domain key is not the placeholder value
3. Ensure the domain is correctly added to OpenAI allowlist
4. Check browser console for errors

### Domain Key Invalid

**Problem**: "Invalid domain key" error

**Solutions**:
1. Verify you added the correct domain (no `https://`, no trailing slash)
2. Make sure you copied the full domain key
3. Check for extra spaces in the `.env.local` file
4. Try regenerating the domain key from OpenAI platform

### Backend Connection Issues

**Problem**: "Failed to connect to backend" error

**Solutions**:
1. Verify backend is running at the URL specified in `NEXT_PUBLIC_API_URL`
2. Check CORS settings on the backend
3. Ensure network connectivity
4. Verify the backend port (default: 8001)

### Styling Issues

**Problem**: ChatKit interface looks broken

**Solutions**:
1. Clear browser cache
2. Run `npm install` again
3. Delete `.next` folder and restart dev server
4. Check browser developer tools for CSS errors

### Messages Not Sending

**Problem**: Messages don't send or responses don't appear

**Solutions**:
1. Check browser network tab for failed requests
2. Verify backend API is responding correctly
3. Check conversation ID is being saved properly
4. Look for errors in browser console

### Delete/Update Commands Not Working

**Problem**: Delete, complete, or update commands appear to do nothing

**Root Cause**: ChatKit was configured to call `/api/{userId}/chatkit` endpoint, but the backend only had `/api/chat` endpoint

**Fix Applied (2025-12-29)**:
- Added new ChatKit-specific endpoint at `/api/{user_id}/chatkit` in `chatbot/backend/src/api/main.py`
- This endpoint accepts ChatKit's request format (`messages` array) and returns ChatKit-compatible responses (`choices` array)
- The endpoint extracts the last user message from the messages array
- Creates/retrieves conversation for the user automatically
- Stores message history and forwards to the AI agent
- Returns responses in the format ChatKit expects

**Technical Details**:
```python
# ChatKit sends requests to:
POST /api/{user_id}/chatkit

# Request format:
{
  "messages": [
    {"role": "user", "content": "delete the meeting task"},
    ...
  ]
}

# Response format:
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "I've deleted the 'meeting' task."
    }
  }],
  "conversation_id": 123,
  "tool_calls": [...]
}
```

**Verification**:
1. Backend server auto-reloads when `main.py` is updated
2. Check backend logs for reload confirmation
3. Test with: `curl http://127.0.0.1:8001/openapi.json | grep chatkit`
4. Should see the new endpoint in the API documentation

**If Still Not Working**:
1. Restart the backend server manually:
   ```bash
   cd chatbot/backend
   uvicorn src.api.main:app --reload --port 8001
   ```
2. Clear browser cache and reload frontend
3. Check browser Network tab - requests should now go to `/api/{userId}/chatkit` instead of `/api/chat`
4. Verify OpenAI API key is set in backend `.env` file

## Development vs Production

### Development Setup

- Domain: `localhost:3000`
- Domain key obtained from OpenAI for localhost
- Set in `.env.local`
- Hot reload enabled

### Production Setup

1. Build the application:
   ```bash
   npm run build
   ```

2. Deploy to hosting (e.g., Vercel)

3. Add production domain to OpenAI allowlist

4. Set environment variable in hosting platform:
   ```
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-production-domain-key
   ```

5. Redeploy if necessary

## Best Practices

1. **Never commit** `.env.local` to version control
2. **Use different domain keys** for development and production
3. **Test thoroughly** in development before deploying
4. **Monitor** ChatKit API usage and rate limits
5. **Implement error handling** for production deployments

## Support

For issues with:
- **ChatKit API**: Contact OpenAI support
- **This Integration**: Check GitHub issues or create a new one
- **Backend**: Refer to backend documentation

## Additional Resources

- [OpenAI ChatKit Documentation](https://platform.openai.com/docs/chatkit)
- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [Backend API Documentation](../backend/README.md)
