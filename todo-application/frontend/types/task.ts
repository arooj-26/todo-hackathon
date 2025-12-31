/**
 * Task-related TypeScript types
 */

export type Priority = 'low' | 'medium' | 'high'
export type Recurrence = 'daily' | 'weekly' | 'monthly' | null

export interface Task {
  id: number
  user_id: number
  description: string
  completed: boolean
  priority: Priority
  due_date?: string | null
  recurrence: Recurrence
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  description: string
  priority?: Priority
  due_date?: string | null
  recurrence?: Recurrence
}

export interface TaskUpdate {
  description?: string
  completed?: boolean
  priority?: Priority
  due_date?: string | null
  recurrence?: Recurrence
}
