# Chatbot Setup Guide

## How Authentication Works

The chatbot now uses **JWT (JSON Web Token) authentication** to automatically identify users. Here's how it works:

### 1. **User Login Flow**
```
User → Login with email/password → Backend verifies → Returns JWT token
```

The JWT token contains:
- Your **user ID** (automatically embedded)
- Token expiration time
- Security signature

### 2. **Where Your User ID Comes From**

You **don't need to know your user ID**! Here's what happens:

1. When you **sign up or log in** to the todo app:
   - Backend creates your user account in the database
   - Your user ID is automatically assigned (e.g., 1, 2, 3...)
   - Backend generates a JWT token with your ID embedded
   - Frontend stores this token in localStorage

2. When you **use the chatbot**:
   - Frontend automatically sends your JWT token to the chatbot
   - Chatbot extracts your user ID from the token
   - Tasks are created/listed for YOUR account only

### 3. **Security Benefits**

- **No manual ID entry**: You never see or enter your user ID
- **Automatic authentication**: Token is sent with every request
- **Secure**: Token is signed and verified by the backend
- **Data isolation**: You can only access YOUR tasks, not other users'

## Setup Instructions

### Step 1: Configure Environment Variables

Both the **todo app backend** and **chatbot backend** must use the **SAME SECRET_KEY** for JWT to work.

#### Todo App Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=your-secret-key-min-32-characters-long-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
```

#### Chatbot Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/database  # SAME database
SECRET_KEY=your-secret-key-min-32-characters-long-change-in-production  # SAME secret key!
ALGORITHM=HS256
OPENAI_API_KEY=sk-your-openai-key-here
```

**CRITICAL**: The `SECRET_KEY` must be **identical** in both backends!

### Step 2: Install Dependencies

```bash
cd chatbot/backend
pip install -r requirements.txt
```

This will install `python-jose[cryptography]` for JWT verification.

### Step 3: Restart the Chatbot Backend

```bash
cd chatbot/backend
uvicorn src.api.main:app --reload --port 8000
```

### Step 4: Test the Flow

1. **Login to the dashboard** (http://localhost:3000)
   - Use your email and password
   - You're now authenticated!

2. **Open the chatbot** (floating button on bottom-right)

3. **Send a message**: "Add buy groceries to my list"

4. **Check the dashboard**: The task appears instantly!

## How to Find Your User ID (Optional)

If you're curious about your user ID:

1. **Open Browser DevTools** (F12)
2. Go to **Application** → **Local Storage**
3. Find `access_token`
4. Copy the token and paste it into [jwt.io](https://jwt.io)
5. Look at the payload section → `"sub": "1"` ← This is your user ID!

But remember: **You don't need to know this!** The chatbot handles it automatically.

## API Endpoints

### Chat Endpoint (NEW)
```
POST /api/chat
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "message": "Add buy groceries to my list",
  "conversation_id": null
}
```

The `user_id` is automatically extracted from the JWT token!

### Old Endpoint (Deprecated)
```
❌ POST /api/{user_id}/chat  # Don't use this anymore
```

## Troubleshooting

### Error: "Not authenticated. Please log in."

**Cause**: No JWT token found in localStorage

**Solution**:
1. Log out of the dashboard
2. Log back in
3. Try the chatbot again

### Error: "Invalid or expired token"

**Cause**: Token has expired (default: 24 hours) or SECRET_KEY mismatch

**Solution**:
1. Check that both backends have the **same SECRET_KEY** in `.env`
2. Log out and log back in to get a fresh token
3. Restart both backends

### Error: "Server configuration error: SECRET_KEY not set"

**Cause**: Chatbot backend `.env` file is missing SECRET_KEY

**Solution**:
1. Copy `.env.example` to `.env` in `chatbot/backend/`
2. Set `SECRET_KEY` to match the todo app backend
3. Restart the chatbot backend

### Tasks created by chatbot don't appear in dashboard

**Cause**: Different DATABASE_URL in chatbot and todo app

**Solution**:
1. Both backends must use the **same database**
2. Check `DATABASE_URL` in both `.env` files
3. Restart both backends

## Architecture Diagram

```
┌─────────────┐
│   Browser   │
│  (Frontend) │
└──────┬──────┘
       │ 1. Login with email/password
       ↓
┌─────────────────────┐
│ Todo App Backend    │
│ (Port 8001)         │
│                     │
│ Generates JWT:      │
│ {                   │
│   "sub": "1",       │ ← User ID embedded
│   "exp": 1234567890 │
│ }                   │
└──────┬──────────────┘
       │ 2. Returns JWT token
       ↓
┌─────────────┐
│   Browser   │
│ localStorage│
│ access_token│ ← Token stored
└──────┬──────┘
       │ 3. Sends message + token
       ↓
┌─────────────────────┐
│ Chatbot Backend     │
│ (Port 8000)         │
│                     │
│ Extracts user_id:   │
│ verify_token(token) │ → user_id = 1
│                     │
│ Creates task with   │
│ user_id = 1         │
└──────┬──────────────┘
       │ 4. Saves to database
       ↓
┌─────────────────────┐
│    Database         │
│                     │
│ tasks table:        │
│ id | user_id | desc │
│ 1  |    1    | buy  │ ← Task created!
└─────────────────────┘
```

## Security Notes

- **Never commit `.env` files** to git
- **Use strong SECRET_KEY** in production (min 32 characters)
- **Use HTTPS** in production
- **Rotate SECRET_KEY** periodically for security
- Tokens expire after 24 hours by default

## Questions?

If you have issues:
1. Check both `.env` files have matching `SECRET_KEY` and `DATABASE_URL`
2. Check browser console for error messages (F12 → Console tab)
3. Check backend logs for authentication errors
4. Ensure you're logged in to the dashboard

That's it! The chatbot now automatically knows who you are. No need to manually enter your user ID! 🎉
