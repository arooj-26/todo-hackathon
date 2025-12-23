# Better Auth Setup Guide

This project now uses [Better Auth](https://better-auth.com) for authentication instead of a custom backend API.

## What is Better Auth?

Better Auth is a modern, type-safe authentication library for Next.js that handles:
- Email/password authentication
- Session management
- Secure cookie handling
- Built-in database support
- Type-safe API

## Configuration

### 1. Environment Variables

Copy `.env.example` to `.env.local` and configure:

```bash
# App Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Better Auth Configuration
# Generate a secure secret with: openssl rand -base64 32
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars-change-this-in-production
```

**Important:**
- The `BETTER_AUTH_SECRET` must be at least 32 characters
- Generate a secure secret for production using: `openssl rand -base64 32`
- Never commit `.env.local` to version control

### 2. Database

Better Auth uses SQLite by default (stored in `db.sqlite`). The database is automatically created when you first run the app.

For production, you can configure a different database in `lib/auth/server.ts`:

```typescript
export const auth = betterAuth({
  database: {
    provider: "postgres", // or "mysql", "sqlite"
    url: process.env.DATABASE_URL,
  },
  // ... other config
})
```

### 3. File Structure

```
frontend/
├── lib/
│   └── auth/
│       ├── server.ts       # Server-side auth config
│       └── client.ts       # Client-side auth hooks
├── app/
│   └── api/
│       └── auth/
│           └── [...all]/
│               └── route.ts # Auth API endpoints
├── hooks/
│   └── useAuth.ts          # Auth hook wrapper
└── components/
    └── auth/
        └── AuthProvider.tsx # Auth context provider
```

## Usage

### Sign Up

```typescript
import { useAuth } from '@/hooks/useAuth'

function SignUpForm() {
  const { signUp } = useAuth()

  const handleSubmit = async (email: string, password: string) => {
    try {
      await signUp(email, password)
      // User is automatically redirected to dashboard
    } catch (error) {
      console.error('Sign up failed:', error.message)
    }
  }
}
```

### Sign In

```typescript
import { useAuth } from '@/hooks/useAuth'

function SignInForm() {
  const { signIn } = useAuth()

  const handleSubmit = async (email: string, password: string) => {
    try {
      await signIn(email, password)
      // User is automatically redirected to dashboard
    } catch (error) {
      console.error('Sign in failed:', error.message)
    }
  }
}
```

### Sign Out

```typescript
import { useAuth } from '@/hooks/useAuth'

function Header() {
  const { signOut, user } = useAuth()

  return (
    <div>
      <p>Welcome, {user?.name}</p>
      <button onClick={signOut}>Sign Out</button>
    </div>
  )
}
```

### Check Authentication Status

```typescript
import { useAuth } from '@/hooks/useAuth'

function ProtectedPage() {
  const { user, isLoading, isAuthenticated } = useAuth()

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    return <div>Please sign in</div>
  }

  return <div>Hello, {user?.name}</div>
}
```

## Password Requirements

By default, passwords must be at least 8 characters long. The sign-up page enforces additional client-side validation:
- At least one uppercase letter
- At least one lowercase letter
- At least one number

You can customize these requirements in `lib/auth/server.ts`:

```typescript
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 12, // Increase minimum length
    requireEmailVerification: true, // Require email verification
  },
})
```

## Session Management

Better Auth automatically handles session management with:
- Secure HTTP-only cookies
- Automatic session refresh
- Session caching (5 minutes by default)

You can customize session settings in `lib/auth/server.ts`:

```typescript
export const auth = betterAuth({
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 5 * 60, // 5 minutes
    },
  },
})
```

## Security Best Practices

1. **Secret Management**
   - Use a strong, random secret for `BETTER_AUTH_SECRET`
   - Never commit secrets to version control
   - Rotate secrets periodically

2. **HTTPS**
   - Always use HTTPS in production
   - Better Auth cookies are marked as `secure` in production

3. **Email Verification**
   - Enable `requireEmailVerification` in production
   - Configure an email provider (e.g., SendGrid, Resend)

4. **Rate Limiting**
   - Implement rate limiting for auth endpoints in production
   - Use middleware or a service like Vercel Edge Config

## Migration from Backend API

If you were previously using the FastAPI backend for authentication:

1. User data is now stored in Better Auth's local database
2. Existing users will need to sign up again
3. You can migrate users by importing them into the Better Auth database
4. The old auth endpoints (`/auth/signin`, `/auth/signup`) are no longer used

## Troubleshooting

### "Database not found" error
- Make sure `better-sqlite3` is installed: `npm install better-sqlite3`
- Check that the app has write permissions in the project directory

### "Invalid session" error
- Clear your browser cookies
- Make sure `BETTER_AUTH_SECRET` is set in `.env.local`
- Restart the development server

### Sign up/sign in not working
- Check browser console for errors
- Verify API route is working: `http://localhost:3000/api/auth/session`
- Make sure `NEXT_PUBLIC_APP_URL` matches your actual URL

## Additional Features

Better Auth supports many additional features:

- **OAuth Providers** (Google, GitHub, etc.)
- **Two-Factor Authentication**
- **Magic Links**
- **Account Linking**
- **Session Management**

See the [Better Auth documentation](https://better-auth.com/docs) for more details.

## Resources

- [Better Auth Documentation](https://better-auth.com/docs)
- [Better Auth GitHub](https://github.com/better-auth/better-auth)
- [Next.js Documentation](https://nextjs.org/docs)
