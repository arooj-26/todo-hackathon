/**
 * Custom hook for task management with TanStack Query.
 *
 * Provides queries and mutations for:
 * - Creating tasks with recurrence patterns
 * - Completing tasks
 * - Listing tasks with filters
 * - Updating tasks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';

/**
 * Task status enumeration.
 */
export type TaskStatus = 'todo' | 'in_progress' | 'completed';

/**
 * Task priority enumeration.
 */
export type TaskPriority = 'high' | 'medium' | 'low';

/**
 * Recurrence pattern type.
 */
export type PatternType = 'daily' | 'weekly' | 'monthly';

/**
 * Recurrence end condition.
 */
export type EndCondition = 'never' | 'after_occurrences' | 'by_date';

/**
 * Recurrence pattern configuration.
 */
export interface RecurrencePattern {
  pattern_type: PatternType;
  interval: number;
  days_of_week?: number[];
  day_of_month?: number;
  end_condition: EndCondition;
  occurrence_count?: number;
  end_date?: string;
}

/**
 * Task interface.
 */
export interface Task {
  id: number;
  user_id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  due_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  recurrence_pattern_id?: number;
  parent_task_id?: number;
  tags: string[];
}

/**
 * Task creation data.
 */
export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_at?: string;
  recurrence_pattern?: RecurrencePattern;
  tag_names?: string[];
  reminder_offset_minutes?: number;
}

/**
 * Task update data.
 */
export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_at?: string;
  tag_names?: string[];
}

/**
 * Task list response.
 */
export interface TaskListResponse {
  tasks: Task[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Task list query parameters.
 */
export interface TaskListParams {
  search?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  tags?: string[];
  due_date_start?: string;
  due_date_end?: string;
  sort?: string;
  limit?: number;
  offset?: number;
}

/**
 * Hook for task management operations.
 *
 * @param params - Optional query parameters for task list
 * @returns Task queries and mutations
 */
export function useTasks(params?: TaskListParams) {
  const queryClient = useQueryClient();

  // Query for task list
  const tasksQuery = useQuery<TaskListResponse>({
    queryKey: ['tasks', params],
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      if (params?.search) queryParams.set('search', params.search);
      if (params?.status) queryParams.set('status', params.status);
      if (params?.priority) queryParams.set('priority', params.priority);
      if (params?.tags) {
        params.tags.forEach((tag) => queryParams.append('tags', tag));
      }
      if (params?.due_date_start) queryParams.set('due_date_start', params.due_date_start);
      if (params?.due_date_end) queryParams.set('due_date_end', params.due_date_end);
      if (params?.sort) queryParams.set('sort', params.sort);
      if (params?.limit) queryParams.set('limit', params.limit.toString());
      if (params?.offset) queryParams.set('offset', params.offset.toString());

      const endpoint = `/tasks${queryParams.toString() ? `?${queryParams}` : ''}`;
      return api.get<TaskListResponse>(endpoint);
    },
  });

  // Mutation for creating a task
  const createTaskMutation = useMutation({
    mutationFn: async (taskData: TaskCreate) => {
      return api.post<Task>('/tasks', taskData);
    },
    onSuccess: () => {
      // Invalidate and refetch tasks list
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  // Mutation for completing a task
  const completeTaskMutation = useMutation({
    mutationFn: async (taskId: number) => {
      return api.post<Task>(`/tasks/${taskId}/complete`, {});
    },
    onSuccess: () => {
      // Invalidate and refetch tasks list
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  // Mutation for updating a task
  const updateTaskMutation = useMutation({
    mutationFn: async ({ taskId, data }: { taskId: number; data: TaskUpdate }) => {
      return api.patch<Task>(`/tasks/${taskId}`, data);
    },
    onSuccess: () => {
      // Invalidate and refetch tasks list
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  // Mutation for stopping recurrence
  const stopRecurrenceMutation = useMutation({
    mutationFn: async (taskId: number) => {
      return api.post<Task>(`/tasks/${taskId}/stop-recurrence`, {});
    },
    onSuccess: () => {
      // Invalidate and refetch tasks list
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  return {
    // Queries
    tasks: tasksQuery.data?.tasks ?? [],
    total: tasksQuery.data?.total ?? 0,
    isLoading: tasksQuery.isLoading,
    isError: tasksQuery.isError,
    error: tasksQuery.error,

    // Mutations
    createTask: createTaskMutation.mutate,
    createTaskAsync: createTaskMutation.mutateAsync,
    isCreating: createTaskMutation.isPending,

    completeTask: completeTaskMutation.mutate,
    completeTaskAsync: completeTaskMutation.mutateAsync,
    isCompleting: completeTaskMutation.isPending,

    updateTask: updateTaskMutation.mutate,
    updateTaskAsync: updateTaskMutation.mutateAsync,
    isUpdating: updateTaskMutation.isPending,

    stopRecurrence: stopRecurrenceMutation.mutate,
    stopRecurrenceAsync: stopRecurrenceMutation.mutateAsync,
    isStoppingRecurrence: stopRecurrenceMutation.isPending,

    // Refetch
    refetch: tasksQuery.refetch,
  };
}

/**
 * Hook for a single task by ID.
 *
 * @param taskId - Task ID to fetch
 * @returns Task query
 */
export function useTask(taskId: number | null) {
  return useQuery<Task>({
    queryKey: ['tasks', taskId],
    queryFn: async () => {
      if (!taskId) throw new Error('Task ID is required');
      return api.get<Task>(`/tasks/${taskId}`);
    },
    enabled: taskId !== null,
  });
}
