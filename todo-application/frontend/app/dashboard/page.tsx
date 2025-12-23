/**
 * Dashboard - TodoFlow Modern Design
 * Production-ready dashboard with shadcn/ui components
 */
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthContext } from '@/components/auth/AuthProvider'
import TodoFlowDashboard from '@/components/dashboard/TodoFlowDashboard'

export default function DashboardPage() {
  const { user, isLoading: authLoading, isAuthenticated, signOut } = useAuthContext()
  const router = useRouter()

  useEffect(() => {
    const hasToken = typeof window !== 'undefined' && localStorage.getItem('access_token')
    if (!authLoading && !isAuthenticated && !hasToken) {
      router.push('/auth/signin')
    }
  }, [authLoading, isAuthenticated, router])

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 border-4 border-t-purple-600 border-r-purple-600 border-b-gray-200 border-l-gray-200 rounded-full animate-spin"></div>
          <p className="text-gray-600 font-medium">Loading your workspace...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) return null

  return <TodoFlowDashboard user={user} onSignOut={signOut} />
}
