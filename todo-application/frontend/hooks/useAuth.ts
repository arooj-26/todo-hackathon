/**
 * Authentication hook that integrates Better Auth UI with FastAPI backend
 * All authentication operations delegate to FastAPI endpoints
 */
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { customSignIn, customSignUp, customSignOut, syncSession } from '@/lib/auth/handlers'
import { sessionSync } from '@/lib/auth/session-sync'
import { User } from '@/types/auth'

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Check authentication state on mount
  useEffect(() => {
    checkAuth()
  }, [])

  /**
   * Check current authentication state
   * Validates session with FastAPI /auth/me endpoint
   */
  const checkAuth = async () => {
    setIsLoading(true)
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
      if (!token) {
        setUser(null)
        setIsLoading(false)
        return
      }

      // Validate session with FastAPI and cache result
      const currentUser = await sessionSync.validate()
      setUser(currentUser)
    } catch {
      // Token invalid or expired
      setUser(null)
      sessionSync.clear()
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Sign up new user via FastAPI
   */
  const signUp = async (email: string, password: string) => {
    const response = await customSignUp(email, password)
    setUser(response.user)
    sessionSync.setUser(response.user)
    router.push('/dashboard')
  }

  /**
   * Sign in existing user via FastAPI
   */
  const signIn = async (email: string, password: string) => {
    const response = await customSignIn(email, password)
    setUser(response.user)
    sessionSync.setUser(response.user)
    router.push('/dashboard')
  }

  /**
   * Sign out current user via FastAPI
   */
  const signOut = async () => {
    await customSignOut()
    setUser(null)
    sessionSync.clear()
    router.push('/auth/signin')
  }

  /**
   * Refresh current session state
   */
  const refresh = async () => {
    await checkAuth()
  }

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    signUp,
    signIn,
    signOut,
    refresh,
  }
}
