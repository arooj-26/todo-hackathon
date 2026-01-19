/**
 * Authentication context provider for Phase-5 frontend.
 * Manages user authentication state and provides auth methods.
 */
'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { User } from '@/types/auth'
import * as authApi from '@/lib/api/auth'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  // Check authentication status on mount
  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      if (authApi.isAuthenticated()) {
        const currentUser = await authApi.getCurrentUser()
        setUser(currentUser)
      }
    } catch (error) {
      // Token is invalid or expired
      localStorage.removeItem('access_token')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const signIn = async (email: string, password: string) => {
    const response = await authApi.signIn(email, password)
    setUser(response.user)
    router.push('/')
  }

  const signUp = async (email: string, password: string) => {
    const response = await authApi.signUp(email, password)
    setUser(response.user)
    router.push('/')
  }

  const signOut = async () => {
    await authApi.signOut()
    setUser(null)
    router.push('/auth/signin')
  }

  const refreshUser = async () => {
    try {
      const currentUser = await authApi.getCurrentUser()
      setUser(currentUser)
    } catch (error) {
      setUser(null)
      localStorage.removeItem('access_token')
    }
  }

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    signIn,
    signUp,
    signOut,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuthContext() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }
  return context
}
