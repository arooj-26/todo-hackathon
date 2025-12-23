# Todo Chatbot Frontend

Next.js-based conversational UI using OpenAI ChatKit for natural language task management.

## Prerequisites

- Node.js 18+ and npm installed
- Backend server running at `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local` and configure:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit domain key (only needed for production deployment)
# NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here

# Default user ID (placeholder - will be replaced with auth)
NEXT_PUBLIC_DEFAULT_USER_ID=00000000-0000-0000-0000-000000000000
```

### 3. Run Development Server

```bash
npm run dev
```

Application will be available at `http://localhost:3000`

## Testing

Run tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm run test:watch
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   │   └── ChatInterface.tsx
│   ├── pages/           # Next.js pages
│   │   └── index.tsx
│   └── services/        # API client
│       └── api.ts
├── public/              # Static assets
├── __tests__/           # Component and integration tests
└── package.json         # Dependencies and scripts
```

## Features

- **Conversational Interface**: Natural language task management
- **Conversation Persistence**: Resume conversations across sessions
- **ChatKit Integration**: Official OpenAI chat component
- **Real-time Updates**: Immediate feedback on task operations
- **Error Handling**: User-friendly error messages

## Development Workflow

1. Start backend server first (see backend/README.md)
2. Run frontend in development mode: `npm run dev`
3. Open browser to `http://localhost:3000`
4. Test conversation flows with natural language

## Deployment (Vercel)

### 1. Deploy Frontend

```bash
npm run build
vercel deploy
```

### 2. Configure OpenAI Domain Allowlist

Before production deployment:

1. Get your production URL from Vercel (e.g., `https://your-app.vercel.app`)
2. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Click "Add domain"
4. Enter your frontend URL (without trailing slash)
5. Copy the domain key provided

### 3. Set Environment Variables

In Vercel dashboard, add:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
```

## Deployment (GitHub Pages)

1. Update `next.config.js` for static export
2. Build: `npm run build && npm run export`
3. Deploy `out/` directory to GitHub Pages
4. Configure domain allowlist as above

## Troubleshooting

**Backend Connection Errors:**
- Verify backend is running at NEXT_PUBLIC_API_URL
- Check CORS configuration in backend
- Ensure network connectivity

**ChatKit Not Loading:**
- Verify domain is added to OpenAI allowlist (production only)
- Check NEXT_PUBLIC_OPENAI_DOMAIN_KEY is set (production only)
- Local development (`localhost`) works without domain key

**Conversation Not Persisting:**
- Check browser localStorage is enabled
- Verify conversation_id is being saved/retrieved
- Check backend /conversations endpoint

## API Integration

The frontend communicates with the backend through a single endpoint:

**POST /api/{user_id}/chat**

See `src/services/api.ts` for the API client implementation.
