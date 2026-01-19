/**
 * Authentication-related types for Phase-5 frontend.
 */

export interface User {
  id: number
  email: string
  timezone?: string
  notification_preferences?: {
    email?: boolean
    push?: boolean
    in_app?: boolean
  }
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface SignUpRequest {
  email: string
  password: string
  timezone?: string
}

export interface SignInRequest {
  email: string
  password: string
}
