/**
 * Custom authentication handlers that bridge Better Auth to FastAPI backend
 * These handlers delegate all authentication logic to FastAPI endpoints
 */
import { signIn as fastAPISignIn, signUp as fastAPISignUp, signOut as fastAPISignOut, getCurrentUser } from '@/lib/api/auth'
import { AuthResponse, User } from '@/types/auth'

/**
 * Custom sign-in handler that calls FastAPI /auth/signin
 * Stores FastAPI JWT token in localStorage for API calls
 *
 * @param email - User email address
 * @param password - User password
 * @returns AuthResponse with access token and user data
 */
export async function customSignIn(email: string, password: string): Promise<AuthResponse> {
  // Call FastAPI /auth/signin endpoint
  const response = await fastAPISignIn(email, password)

  // Token is already stored in localStorage by lib/api/auth.ts
  // Better Auth session will be synced separately

  return response
}

/**
 * Custom sign-up handler that calls FastAPI /auth/signup
 * Stores FastAPI JWT token in localStorage for API calls
 *
 * @param email - User email address
 * @param password - User password
 * @returns AuthResponse with access token and user data
 */
export async function customSignUp(email: string, password: string): Promise<AuthResponse> {
  // Call FastAPI /auth/signup endpoint
  const response = await fastAPISignUp(email, password)

  // Token is already stored in localStorage by lib/api/auth.ts
  // Better Auth session will be synced separately

  return response
}

/**
 * Custom sign-out handler that calls FastAPI /auth/signout
 * Clears FastAPI JWT token from localStorage
 */
export async function customSignOut(): Promise<void> {
  // Call FastAPI /auth/signout endpoint
  await fastAPISignOut()

  // Token is already removed from localStorage by lib/api/auth.ts
}

/**
 * Sync Better Auth session with FastAPI authentication state
 * This fetches current user from FastAPI and updates session
 *
 * @returns Current user if authenticated, null otherwise
 */
export async function syncSession(): Promise<User | null> {
  try {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (!token) return null

    // Fetch current user from FastAPI /auth/me endpoint
    const user = await getCurrentUser()
    return user
  } catch (error) {
    // Token invalid or expired
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
    return null
  }
}

/**
 * Check if user is currently authenticated
 *
 * @returns true if access token exists in localStorage
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  const token = localStorage.getItem('access_token')
  return !!token
}
