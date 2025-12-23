/**
 * Task detail page with editing capability
 */
'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { useAuthContext } from '@/components/auth/AuthProvider'
import { Task } from '@/types/task'
import { getTask, updateTask, toggleTaskCompletion, deleteTask } from '@/lib/api/tasks'
import Link from 'next/link'

export default function TaskDetailPage() {
  const params = useParams()
  const taskId = parseInt(params.id as string)
  const { user, isLoading: authLoading, isAuthenticated } = useAuthContext()
  const router = useRouter()

  const [task, setTask] = useState<Task | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [editedDescription, setEditedDescription] = useState('')
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/signin')
    } else if (!authLoading && isAuthenticated && user) {
      fetchTask()
    }
  }, [authLoading, isAuthenticated, user, taskId, router])

  const fetchTask = async () => {
    if (!user) return

    setIsLoading(true)
    setError(null)
    try {
      const data = await getTask(user.id, taskId)
      setTask(data)
      setEditedDescription(data.description)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('Task not found')
      } else if (err.response?.status === 403) {
        setError('You do not have permission to view this task')
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch task')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleCompletion = async () => {
    if (!user || !task) return

    try {
      const updatedTask = await toggleTaskCompletion(user.id, task.id)
      setTask(updatedTask)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to toggle task completion')
    }
  }

  const handleSaveEdit = async () => {
    if (!user || !task) return

    if (editedDescription.trim() === task.description) {
      setIsEditing(false)
      return
    }

    if (!editedDescription.trim()) {
      setError('Task description cannot be empty')
      return
    }

    setIsSaving(true)
    setError(null)
    try {
      const updatedTask = await updateTask(user.id, task.id, { description: editedDescription.trim() })
      setTask(updatedTask)
      setIsEditing(false)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update task')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancelEdit = () => {
    setEditedDescription(task?.description || '')
    setIsEditing(false)
    setError(null)
  }

  const handleDelete = async () => {
    if (!user || !task) return

    if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
      return
    }

    try {
      await deleteTask(user.id, task.id)
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete task')
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading task...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  if (error && !task) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
            <Link
              href="/dashboard"
              className="inline-flex items-center text-blue-600 hover:text-blue-700"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (!task) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-4">
          <Link
            href="/dashboard"
            className="inline-flex items-center text-blue-600 hover:text-blue-700"
          >
            ← Back to Dashboard
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-start justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">Task Details</h1>
            <div className="flex gap-2">
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                >
                  Edit
                </button>
              )}
              <button
                onClick={handleDelete}
                className="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-6">
            {/* Completion Status */}
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={task.completed}
                onChange={handleToggleCompletion}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
              />
              <label className="ml-3 text-sm font-medium text-gray-700">
                {task.completed ? 'Completed' : 'Mark as complete'}
              </label>
            </div>

            {/* Task Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              {isEditing ? (
                <div className="space-y-3">
                  <textarea
                    value={editedDescription}
                    onChange={(e) => setEditedDescription(e.target.value)}
                    maxLength={1000}
                    rows={4}
                    disabled={isSaving}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleSaveEdit}
                      disabled={isSaving || !editedDescription.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isSaving ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      disabled={isSaving}
                      className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <p className={`text-gray-900 whitespace-pre-wrap ${task.completed ? 'line-through text-gray-500' : ''}`}>
                  {task.description}
                </p>
              )}
            </div>

            {/* Metadata */}
            <div className="border-t pt-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Information</h3>
              <dl className="space-y-2">
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-600">Status:</dt>
                  <dd className="text-sm font-medium">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      task.completed
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {task.completed ? 'Completed' : 'In Progress'}
                    </span>
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-600">Created:</dt>
                  <dd className="text-sm text-gray-900">
                    {new Date(task.created_at).toLocaleString()}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-600">Last Updated:</dt>
                  <dd className="text-sm text-gray-900">
                    {new Date(task.updated_at).toLocaleString()}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-600">Task ID:</dt>
                  <dd className="text-sm text-gray-900">#{task.id}</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
