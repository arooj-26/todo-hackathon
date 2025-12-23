/**
 * Task creation form - VIBRANT DESIGN
 */
'use client'

import { useState, FormEvent } from 'react'
import { Priority } from '@/types/task'

interface TaskFormProps {
  onSubmit: (description: string, priority: Priority) => Promise<void>
  isLoading?: boolean
}

export default function TaskForm({ onSubmit, isLoading = false }: TaskFormProps) {
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<Priority>('medium')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!description.trim()) {
      setError('Task description is required')
      return
    }

    if (description.length > 1000) {
      setError('Task description is too long')
      return
    }

    try {
      await onSubmit(description.trim(), priority)
      setDescription('')
      setPriority('medium')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create task')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-[#252942]/80 rounded-xl p-6 border border-gray-700/50">
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <input
            id="task-input"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What needs to be done?"
            maxLength={1000}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-[#1a1d2e] border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          />
        </div>
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value as Priority)}
          disabled={isLoading}
          className={`px-6 py-3 rounded-xl font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm ${
            priority === 'high' ? 'bg-pink-600 text-white' :
            priority === 'medium' ? 'bg-purple-600 text-white' :
            'bg-green-600 text-white'
          }`}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <button
          type="submit"
          disabled={isLoading || !description.trim()}
          className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-purple-500/30"
        >
          {isLoading ? 'Adding...' : 'Add Task'}
        </button>
      </div>
      {error && (
        <div className="mt-3 bg-red-500/10 border border-red-500/50 rounded-xl px-4 py-2">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}
    </form>
  )
}
