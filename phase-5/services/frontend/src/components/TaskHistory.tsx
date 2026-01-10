/**
 * TaskHistory component for showing completed recurring task instances.
 *
 * Displays a list of completed instances of a recurring task,
 * showing when they were completed and their details.
 */

'use client';

import { useTasks, type Task } from '../hooks/useTasks';

interface TaskHistoryProps {
  parentTaskId: number;
  className?: string;
}

export function TaskHistory({ parentTaskId, className = '' }: TaskHistoryProps) {
  // Query for completed tasks with this parent_task_id
  const { tasks, isLoading, isError } = useTasks({
    status: 'completed',
  });

  // Filter for tasks that have this task as parent
  const historyTasks = tasks.filter((task) => task.parent_task_id === parentTaskId);

  if (isLoading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="space-y-2">
          <div className="h-12 bg-gray-200 rounded"></div>
          <div className="h-12 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className={`text-red-600 text-sm ${className}`}>
        Failed to load task history
      </div>
    );
  }

  if (historyTasks.length === 0) {
    return (
      <div className={`text-gray-500 text-sm ${className}`}>
        No completed instances yet
      </div>
    );
  }

  return (
    <div className={className}>
      <h3 className="text-sm font-medium text-gray-700 mb-3">
        Completed Instances ({historyTasks.length})
      </h3>

      <div className="space-y-2">
        {historyTasks.map((task) => (
          <TaskHistoryItem key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
}

interface TaskHistoryItemProps {
  task: Task;
}

function TaskHistoryItem({ task }: TaskHistoryItemProps) {
  const completedDate = task.completed_at
    ? new Date(task.completed_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : 'Unknown';

  const dueDate = task.due_at
    ? new Date(task.due_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : 'No due date';

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-md border border-gray-200">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-green-600"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
          <span className="text-sm font-medium text-gray-900">{task.title}</span>
        </div>
        <div className="mt-1 text-xs text-gray-500">
          Due: {dueDate} • Completed: {completedDate}
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* Priority badge */}
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${
            task.priority === 'high'
              ? 'bg-red-100 text-red-700'
              : task.priority === 'medium'
              ? 'bg-yellow-100 text-yellow-700'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {task.priority}
        </span>
      </div>
    </div>
  );
}
