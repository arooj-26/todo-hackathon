/**
 * Better Auth client configuration
 * This file sets up the Better Auth client for client-side operations
 */
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
})

export const {
  signIn,
  signUp,
  signOut,
  useSession,
} = authClient
