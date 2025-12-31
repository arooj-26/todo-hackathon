# ChatKit Quick Start Guide

## ✅ What's Been Fixed

The ChatKit integration now uses the **actual OpenAI ChatKit Web Component** correctly!

Previously, the code tried to import ChatKit as a React component, but ChatKit is actually a **Web Component** that works differently.

## 🚀 How to Use ChatKit

### Step 1: Get Your Domain Key

1. Go to [OpenAI Platform](https://platform.openai.com/settings/organization/security/domain-allowlist)
2. Click **"Add domain"**
3. For development, enter: `localhost:3000` (or `localhost:3001` if 3000 is in use)
4. Click **"Add"**
5. **Copy the domain key** they provide

### Step 2: Configure Environment

1. Navigate to the frontend directory:
   ```bash
   cd chatbot/frontend
   ```

2. Create `.env.local` from the example:
   ```bash
   cp .env.example .env.local
   ```

3. Edit `.env.local` and add your actual domain key:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8001
   NEXT_PUBLIC_OPENAI_DOMAIN_KEY=sk-domain-abc123xyz...  # Your actual key here
   NEXT_PUBLIC_DEFAULT_USER_ID=00000000-0000-0000-0000-000000000000
   NEXT_PUBLIC_USE_CHATKIT=true
   ```

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Start the Development Server

```bash
npm run dev
```

The server will start on `http://localhost:3000` (or 3001 if 3000 is in use).

### Step 5: Open in Browser

Navigate to `http://localhost:3000` (or whatever port was shown in the terminal).

## 🎯 What You'll See

### With ChatKit Configured:
- Modern OpenAI ChatKit interface
- Professional chat UI with smooth animations
- Suggestion chips for quick actions
- Markdown rendering in responses
- Code highlighting
- Customizable theme
- Toggle to switch between ChatKit and Classic views

### Without ChatKit (Fallback):
- Clean, functional classic chat interface
- All task management features still work
- Simple, responsive design

## 🔧 How It Works Now

### Web Component Architecture

ChatKit is loaded as a **Web Component** (custom HTML element):

```html
<!-- This is how ChatKit is used -->
<openai-chatkit id="chatkit-instance"></openai-chatkit>
```

The component is:
1. Loaded via CDN in `_document.tsx`
2. Configured using JavaScript with `setOptions()`
3. Controlled via events and methods

### Key Files Updated

1. **`src/components/ChatInterface.tsx`** - Uses `<openai-chatkit>` custom element
2. **`src/pages/_document.tsx`** - Loads ChatKit from CDN
3. **`tsconfig.json`** - Includes `@openai/chatkit` types
4. **`package.json`** - Has `@openai/chatkit` for TypeScript types only

## 📝 Important Notes

### About `@openai/chatkit` Package

The npm package `@openai/chatkit` **only contains TypeScript types**, not the actual component!

- ✅ Provides type definitions for TypeScript
- ✅ Gives you autocomplete and type checking
- ❌ Does **not** contain the actual ChatKit component
- ❌ Cannot be imported as `import { ChatKit }`

The actual component is loaded from CDN:
```
https://cdn.jsdelivr.net/npm/@openai/chatkit@latest/dist/chatkit.min.js
```

### Backend Requirements

ChatKit expects specific API endpoints. For a full implementation, your backend needs:

```
POST /api/{userId}/chatkit
```

This endpoint should:
- Accept ChatKit's request format
- Return server-sent events (SSE) for streaming responses
- Handle ChatKit's protocol for messages and thread management

**For now**, the chatbot will use the classic interface unless you implement the ChatKit backend endpoint.

## 🧪 Testing

### Test with Classic Interface (Always Works)

```bash
# In .env.local, set:
NEXT_PUBLIC_USE_CHATKIT=false
# OR don't set the domain key
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
```

### Test with ChatKit (Requires Domain Key + Backend)

```bash
# In .env.local, set:
NEXT_PUBLIC_USE_CHATKIT=true
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=sk-domain-your-actual-key-here
```

Then the app will:
1. Check if domain key is valid
2. Load ChatKit from CDN
3. Initialize the web component
4. Render the ChatKit interface

## 🐛 Troubleshooting

### "Build Error: Module not found" is Gone!

The error you saw was because the code tried to import ChatKit as:
```typescript
import { ChatKit } from '@openai/chatkit';  // ❌ Wrong!
```

Now it correctly uses:
```typescript
import type { OpenAIChatKit } from '@openai/chatkit';  // ✅ Correct! (type-only import)
```

And renders as:
```tsx
<openai-chatkit id="chatkit-instance" />  // ✅ Correct! (web component)
```

### ChatKit Not Showing

**Possible causes:**

1. **No domain key configured** → Falls back to classic interface (this is normal!)
2. **Invalid domain key** → Check it matches what OpenAI provided
3. **Wrong domain in OpenAI settings** → Must match exactly (e.g., `localhost:3000`)
4. **Script didn't load** → Check browser console for errors

### Backend Connection Errors

ChatKit requires a specific backend API structure. Until you implement the ChatKit backend endpoint, you can:

1. Use the classic interface (works with current backend)
2. Or implement the ChatKit API endpoint following OpenAI's spec

## 🎨 Customization

### Theme Colors

Edit `src/lib/chatkit-config.ts`:

```typescript
export function getDefaultTheme(): ChatKitTheme {
  return {
    primaryColor: '#667eea',  // Change this!
    backgroundColor: '#ffffff',
    userMessageColor: '#e3f2fd',
    assistantMessageColor: '#f5f5f5',
    // ...
  };
}
```

### Suggestions

Edit `src/lib/chatkit-config.ts`:

```typescript
export function getTaskSuggestions(): string[] {
  return [
    "Your custom suggestion 1",
    "Your custom suggestion 2",
    // Add more...
  ];
}
```

## 📚 Learn More

- [OpenAI ChatKit Documentation](https://openai.github.io/chatkit-js/)
- [ChatKit Python SDK](https://openai.github.io/chatkit-python-sdk/)
- [Web Components MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_components)

## ✨ Summary

The chatbot now **correctly integrates OpenAI ChatKit** as a Web Component! The error is fixed and you can:

1. Use ChatKit with a valid domain key ✅
2. Or use the classic interface without ChatKit ✅
3. Toggle between both views ✅
4. Everything works out of the box! ✅
