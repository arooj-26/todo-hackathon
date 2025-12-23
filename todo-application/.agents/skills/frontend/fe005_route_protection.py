"""
Skill FE-005: Implement Route Protection

Creates protected route wrappers and authentication guards.
"""

from pathlib import Path
from typing import List
from ...lib.skill_base import (
    Skill,
    SkillMetadata,
    SkillInput,
    SkillOutput,
    SkillStatus,
    register_skill
)


@register_skill
class ImplementRouteProtectionSkill(Skill):
    """Implement route protection with authentication guards."""

    @property
    def metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        return SkillMetadata(
            skill_id="FE-005",
            name="Implement Route Protection",
            description="Create protected route wrappers and authentication guards",
            category="frontend",
            version="1.0.0",
            dependencies=["FE-001", "FE-003", "FE-004"],
            inputs_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            outputs_schema={
                "type": "object",
                "properties": {
                    "guard_path": {"type": "string"},
                    "provider_path": {"type": "string"}
                }
            }
        )

    def validate_inputs(self, inputs: SkillInput) -> tuple[bool, str | None]:
        """Validate input parameters."""
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            return False, "Frontend directory does not exist. Run FE-001 first."

        return True, None

    def execute(self, inputs: SkillInput) -> SkillOutput:
        """Execute the skill."""
        try:
            frontend_path = Path("frontend")
            components_path = frontend_path / "components"
            components_path.mkdir(parents=True, exist_ok=True)

            # Create auth provider
            provider_path = components_path / "AuthProvider.tsx"
            provider_code = """"use client"

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient } from '@/lib/api-client'
import { User } from '@/lib/types'

interface AuthContextType {
  user: User | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated on mount
    const token = localStorage.getItem('access_token')
    if (token) {
      refreshUser()
    } else {
      setLoading(false)
    }
  }, [])

  const refreshUser = async () => {
    try {
      const userData = await apiClient.getMe()
      setUser(userData)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const signIn = async (email: string, password: string) => {
    try {
      const response = await apiClient.signIn({ email, password })
      setUser(response.user)
      router.push('/dashboard')
    } catch (error) {
      throw error
    }
  }

  const signUp = async (email: string, password: string) => {
    try {
      const response = await apiClient.signUp({ email, password })
      setUser(response.user)
      router.push('/dashboard')
    } catch (error) {
      throw error
    }
  }

  const signOut = async () => {
    await apiClient.signOut()
    setUser(null)
    router.push('/signin')
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
"""

            provider_path.write_text(provider_code, encoding="utf-8")
            self.logger.info(f"Created auth provider: {provider_path}")

            # Create protected route guard
            guard_path = components_path / "ProtectedRoute.tsx"
            guard_code = """"use client"

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from './AuthProvider'

interface ProtectedRouteProps {
  children: React.ReactNode
  redirectTo?: string
}

export function ProtectedRoute({ children, redirectTo = '/signin' }: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push(redirectTo)
    }
  }, [user, loading, router, redirectTo])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return <>{children}</>
}
"""

            guard_path.write_text(guard_code, encoding="utf-8")
            self.logger.info(f"Created route guard: {guard_path}")

            # Create loading component
            loading_path = components_path / "Loading.tsx"
            loading_code = """export function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
    </div>
  )
}
"""

            loading_path.write_text(loading_code, encoding="utf-8")
            self.logger.info(f"Created loading component: {loading_path}")

            artifacts = [str(provider_path), str(guard_path), str(loading_path)]

            return SkillOutput(
                status=SkillStatus.SUCCESS,
                result={
                    "guard_path": str(guard_path),
                    "provider_path": str(provider_path)
                },
                artifacts=artifacts,
                logs=[f"Created {len(artifacts)} route protection files"]
            )

        except Exception as e:
            self.logger.exception("Failed to implement route protection")
            return SkillOutput(
                status=SkillStatus.FAILED,
                error=str(e)
            )

    def get_success_criteria(self) -> List[str]:
        """Get success criteria checklist."""
        return [
            "AuthProvider created with context",
            "useAuth hook exposed for consuming components",
            "ProtectedRoute component guards routes",
            "Loading state shown during authentication check",
            "Automatic redirect to signin for unauthenticated users",
            "User state managed globally",
            "Sign in/up/out methods available"
        ]
