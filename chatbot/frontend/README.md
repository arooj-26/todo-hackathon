# Todo AI Dashboard with OpenAI ChatKit

Next.js-based conversational dashboard powered **exclusively by OpenAI ChatKit** for intelligent natural language task management.

## ✨ Features

- **OpenAI ChatKit Powered**: Professional AI chat interface with modern UI
- **Enhanced Dashboard**: Statistics, quick actions, and conversation management
- **Smart Suggestions**: Quick action chips for common task operations
- **Theme Customization**: Customizable colors and styling
- **Thread Management**: Persistent conversations across sessions
- **Real-time Streaming**: Immediate feedback on task operations
- **Responsive Design**: Mobile-friendly interface
- **Markdown & Code**: Rich text rendering with syntax highlighting

## 📋 Prerequisites

- Node.js 18+ and npm installed
- Backend server running at `http://localhost:8001` (default)
- **Required**: OpenAI account with ChatKit access and domain key

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Then edit `.env.local` and add your configuration:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001

# OpenAI ChatKit Domain Key (get from https://platform.openai.com)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-actual-domain-key-here

# Default user ID
NEXT_PUBLIC_DEFAULT_USER_ID=00000000-0000-0000-0000-000000000000

```

**Important**: A valid ChatKit domain key is **REQUIRED** for this application to work. See [CHATKIT_QUICKSTART.md](./CHATKIT_QUICKSTART.md) for setup instructions.

### 3. Run Development Server

```bash
npm run dev
```

Application will be available at `http://localhost:3000`

## 🎨 ChatKit Integration

This project features **OpenAI ChatKit** integration for an enhanced chat experience. For detailed setup instructions:

👉 **[See CHATKIT_SETUP.md](./CHATKIT_SETUP.md)** for complete ChatKit configuration guide

### Quick ChatKit Setup

1. Get domain key from [OpenAI Platform](https://platform.openai.com/settings/organization/security/domain-allowlist)
2. Add domain (e.g., `localhost:3000` for development)
3. Copy the provided domain key
4. Add to `.env.local`: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key-here`
5. Restart dev server

### Without ChatKit Domain Key

If no domain key is configured, the application will show setup instructions to help you get started with ChatKit.

## 🧪 Testing

Run tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm run test:watch
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── ChatInterface.tsx # ChatKit-integrated chat component
│   │   ├── Dashboard.tsx     # Enhanced dashboard with sidebar
│   │   └── ConversationHistory.tsx
│   ├── pages/               # Next.js pages
│   │   └── index.tsx        # Main dashboard page
│   ├── services/            # API clients
│   │   └── api.ts          # Backend API client
│   └── lib/                # Utilities and config
│       └── chatkit-config.ts # ChatKit configuration
├── public/                 # Static assets
├── __tests__/             # Tests
├── next.config.js         # Next.js configuration
├── CHATKIT_SETUP.md       # ChatKit setup guide
└── package.json           # Dependencies
```

## 🚀 Key Features

### ChatKit-Powered Interface
- **Modern UI**: Professional chat interface using OpenAI ChatKit
- **Smart Suggestions**: Quick action chips for common tasks
- **Markdown Support**: Rich text rendering in messages
- **Code Highlighting**: Syntax highlighting for code blocks
- **Theme Customization**: Customizable colors and styling

### Enhanced Dashboard
- **Statistics Panel**: Real-time task counts and metrics
- **Quick Actions**: One-click buttons for common operations
- **Collapsible Sidebar**: Responsive design for all devices
- **View Toggle**: Switch between ChatKit and Classic interfaces
- **Help Section**: Inline help and example commands

### Core Functionality
- **Natural Language Processing**: Understand task commands naturally via ChatKit
- **Thread Management**: Persistent conversation threads
- **Real-time Streaming**: Server-sent events for live responses
- **Error Handling**: User-friendly error messages
- **Full ChatKit Features**: Leverage all ChatKit capabilities

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

### 2. (Optional) Configure OpenAI Domain Allowlist

This step is only required if using the official OpenAI ChatKit component:

1. Get your production URL from Vercel (e.g., `https://your-app.vercel.app`)
2. Navigate to: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Click "Add domain"
4. Enter your frontend URL (without trailing slash)
5. Copy the domain key provided

### 3. Set Environment Variables

In Vercel dashboard, add:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
# NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here  # Only needed if using official ChatKit
```

## Deployment (GitHub Pages)

1. Update `next.config.js` for static export
2. Build: `npm run build && npm run export`
3. Deploy `out/` directory to GitHub Pages
4. Configure domain allowlist as above

## Troubleshooting

**Backend Connection Errors:**
- Verify backend is running at NEXT_PUBLIC_API_URL (default: http://localhost:8001)
- Check CORS configuration in backend
- Ensure network connectivity
- Verify the backend server is running before starting the frontend

**Chat Interface Issues:**
- If using official ChatKit component, verify domain is added to OpenAI allowlist (production only)
- Check NEXT_PUBLIC_OPENAI_DOMAIN_KEY is set if using official ChatKit (production only)
- Local development (`localhost`) works without domain key for official ChatKit

**Conversation Not Persisting:**
- Check browser localStorage is enabled
- Verify conversation_id is being saved/retrieved
- Check backend /conversations endpoint

## API Integration

The frontend communicates with the backend through a single endpoint:

**POST /api/{user_id}/chat**

See `src/services/api.ts` for the API client implementation.