/**
 * Individual task item component
 */
'use client'

import { Task, Priority } from '@/types/task'
import { useState } from 'react'

interface TaskItemProps {
  task: Task
  onToggle: (taskId: number) => Promise<void>
  onDelete: (taskId: number) => Promise<void>
  onEdit?: (taskId: number, description: string, priority: Priority) => Promise<void>
}

export default function TaskItem({ task, onToggle, onDelete, onEdit }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedDescription, setEditedDescription] = useState(task.description)
  const [editedPriority, setEditedPriority] = useState<Priority>(task.priority)
  const [isLoading, setIsLoading] = useState(false)

  const handleToggle = async () => {
    setIsLoading(true)
    try {
      await onToggle(task.id)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this task?')) {
      setIsLoading(true)
      try {
        await onDelete(task.id)
      } finally {
        setIsLoading(false)
      }
    }
  }

  const handleEdit = async () => {
    if (!onEdit) return

    if (editedDescription.trim() === task.description && editedPriority === task.priority) {
      setIsEditing(false)
      return
    }

    if (!editedDescription.trim()) {
      setEditedDescription(task.description)
      setEditedPriority(task.priority)
      setIsEditing(false)
      return
    }

    setIsLoading(true)
    try {
      await onEdit(task.id, editedDescription.trim(), editedPriority)
      setIsEditing(false)
    } catch (err) {
      setEditedDescription(task.description)
      setEditedPriority(task.priority)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancelEdit = () => {
    setEditedDescription(task.description)
    setEditedPriority(task.priority)
    setIsEditing(false)
  }

  const getPriorityColor = (priority: Priority) => {
    switch (priority) {
      case 'high':
        return {
          border: 'border-l-pink-500',
          badge: 'bg-pink-600 text-white',
          progress: 'bg-pink-500'
        }
      case 'medium':
        return {
          border: 'border-l-purple-500',
          badge: 'bg-purple-600 text-white',
          progress: 'bg-purple-500'
        }
      case 'low':
        return {
          border: 'border-l-green-500',
          badge: 'bg-green-600 text-white',
          progress: 'bg-green-500'
        }
    }
  }

  const colors = getPriorityColor(task.priority)

  return (
    <div className={`group bg-[#252942]/80 border border-gray-700/50 rounded-2xl overflow-hidden hover:border-gray-600 transition-all ${isLoading ? 'opacity-50' : ''} ${colors.border} border-l-4`}>
      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* CHECKBOX */}
          <button
            onClick={handleToggle}
            disabled={isLoading}
            className="flex-shrink-0 mt-1"
          >
            <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
              task.completed ? `bg-${task.priority === 'high' ? 'pink' : task.priority === 'medium' ? 'purple' : 'green'}-500 border-${task.priority === 'high' ? 'pink' : task.priority === 'medium' ? 'purple' : 'green'}-500` : 'border-gray-600 hover:border-gray-500'
            }`}>
              {task.completed && (
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </button>

      {isEditing ? (
        <div className="flex-1 flex gap-3">
          <input
            type="text"
            value={editedDescription}
            onChange={(e) => setEditedDescription(e.target.value)}
            maxLength={1000}
            disabled={isLoading}
            className="flex-1 px-4 py-2.5 bg-[#1a1d2e] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 text-sm"
            autoFocus
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleEdit()
              if (e.key === 'Escape') handleCancelEdit()
            }}
          />
          <select
            value={editedPriority}
            onChange={(e) => setEditedPriority(e.target.value as Priority)}
            disabled={isLoading}
            className={`px-4 py-2.5 rounded-xl text-white font-medium text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 ${
              editedPriority === 'high' ? 'bg-pink-600' :
              editedPriority === 'medium' ? 'bg-purple-600' :
              'bg-green-600'
            }`}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <button
            onClick={handleEdit}
            disabled={isLoading}
            className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 transition-all text-sm shadow-lg shadow-purple-500/20"
          >
            Save
          </button>
          <button
            onClick={handleCancelEdit}
            disabled={isLoading}
            className="px-6 py-2.5 bg-[#1a1d2e] border border-gray-700 text-white rounded-xl font-semibold hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 transition-all text-sm"
          >
            Cancel
          </button>
        </div>
      ) : (
        <>
          <span className={`flex-1 text-sm transition-all duration-200 ${task.completed ? 'line-through text-gray-500' : 'text-white'}`}>
            {task.description}
          </span>

          <span className={`px-3 py-1.5 rounded-xl text-xs font-medium ${colors.badge}`}>
            {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
          </span>

          <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {onEdit && (
              <button
                onClick={() => setIsEditing(true)}
                disabled={isLoading}
                className="p-2 text-gray-500 hover:text-purple-400 rounded-xl hover:bg-purple-500/10 disabled:opacity-50 transition-all duration-200"
                title="Edit"
              >
                <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            )}
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="p-2 text-gray-500 hover:text-red-400 rounded-xl hover:bg-red-500/10 disabled:opacity-50 transition-all duration-200"
              title="Delete"
            >
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </>
      )}
        </div>
      </div>
    </div>
  )
}
