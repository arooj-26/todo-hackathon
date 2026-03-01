/**
 * Task API calls
 */
import api from './client'
import { Task, TaskCreate, TaskUpdate } from '@/types/task'

/**
 * Get all tasks for a user
 */
export async function getTasks(userId: number): Promise<Task[]> {
  // Add timestamp to prevent caching
  const timestamp = new Date().getTime()
  const response = await api.get<Task[]>(`/api/${userId}/tasks?_t=${timestamp}`)
  console.log('🌐 getTasks API response:', response.data)
  return response.data
}

/**
 * Create a new task
 */
export async function createTask(userId: number, data: TaskCreate): Promise<Task> {
  const response = await api.post<Task>(`/api/${userId}/tasks`, data)
  return response.data
}

/**
 * Get a specific task by ID
 */
export async function getTask(userId: number, taskId: number): Promise<Task> {
  const response = await api.get<Task>(`/api/${userId}/tasks/${taskId}`)
  return response.data
}

/**
 * Update a task
 */
export async function updateTask(userId: number, taskId: number, data: TaskUpdate): Promise<Task> {
  const response = await api.put<Task>(`/api/${userId}/tasks/${taskId}`, data)
  return response.data
}

/**
 * Toggle task completion status
 */
export async function toggleTaskCompletion(userId: number, taskId: number): Promise<Task> {
  const response = await api.patch<Task>(`/api/${userId}/tasks/${taskId}/toggle`)
  return response.data
}

/**
 * Delete a task
 */
export async function deleteTask(userId: number, taskId: number): Promise<void> {
  await api.delete(`/api/${userId}/tasks/${taskId}`)
}
