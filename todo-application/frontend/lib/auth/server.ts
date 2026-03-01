/**
 * Better Auth server configuration
 * This file sets up Better Auth as a thin UI/session layer
 * All authentication logic is delegated to the FastAPI backend
 *
 * IMPORTANT: Better Auth no longer uses a database
 * All user data is stored in PostgreSQL via FastAPI
 */
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  // NO database configuration - Better Auth delegates to FastAPI
  // Database removed: All user data stored in PostgreSQL via FastAPI backend

  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    requireEmailVerification: false, // Set to true in production
    // Password validation is handled by FastAPI backend
  },

  session: {
    // Stateless sessions - no server-side storage
    // All session validation happens via FastAPI /auth/me endpoint
    cookieCache: {
      enabled: false, // Disabled - always validate with FastAPI
    },
  },

  trustedOrigins: [
    process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  ],

  // Secret still needed for Better Auth internal operations
  secret: process.env.BETTER_AUTH_SECRET,
})

export type Session = typeof auth.$Infer.Session
export type User = typeof auth.$Infer.Session.user
