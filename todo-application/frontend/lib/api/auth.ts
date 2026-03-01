/**
 * Authentication API calls
 */
import api from './client'
import { User, AuthResponse, SignUpRequest, SignInRequest } from '@/types/auth'

/**
 * Sign up a new user
 */
export async function signUp(email: string, password: string): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/signup', {
    email,
    password,
  } as SignUpRequest)

  // Store token in localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', response.data.access_token)
  }

  return response.data
}

/**
 * Sign in with email and password
 */
export async function signIn(email: string, password: string): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/signin', {
    email,
    password,
  } as SignInRequest)

  // Store token in localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', response.data.access_token)
  }

  return response.data
}

/**
 * Sign out current user
 */
export async function signOut(): Promise<void> {
  try {
    await api.post('/auth/signout')
  } finally {
    // Always remove all auth-related data from localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      // Clear all chatbot conversation IDs for all users
      Object.keys(localStorage).forEach(key => {
        if (key.startsWith('chatbot_conversation_id')) {
          localStorage.removeItem(key)
        }
      })
    }
  }
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<User> {
  const response = await api.get<User>('/auth/me')
  return response.data
}

/**
 * Check if user is authenticated (has valid token)
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false
  const token = localStorage.getItem('access_token')
  return !!token
}
