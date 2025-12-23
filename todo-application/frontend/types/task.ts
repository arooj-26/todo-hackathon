/**
 * Task-related TypeScript types
 */

export type Priority = 'low' | 'medium' | 'high'

export interface Task {
  id: number
  user_id: number
  description: string
  completed: boolean
  priority: Priority
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  description: string
  priority?: Priority
}

export interface TaskUpdate {
  description?: string
  completed?: boolean
  priority?: Priority
}
