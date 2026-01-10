/**
 * TaskDetail component for viewing and managing task details.
 *
 * Features:
 * - View complete task information
 * - Display reminders list
 * - Edit task details
 * - Manage reminders
 */

'use client';

import React, { useState, useEffect } from 'react';

export interface Reminder {
  id: number;
  task_id: number;
  user_id: string;
  remind_at: string;
  notification_channel: 'in_app' | 'email' | 'sms';
  delivery_status: 'pending' | 'sent' | 'failed' | 'cancelled';
  retry_count: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed';
  priority: 'low' | 'medium' | 'high';
  due_at?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  recurrence_pattern_id?: number;
  parent_task_id?: number;
}

interface TaskDetailProps {
  /** Task ID to display */
  taskId: number;
  /** Callback when task is updated */
  onUpdate?: () => void;
  /** Callback when task is deleted */
  onDelete?: () => void;
}

export const TaskDetail: React.FC<TaskDetailProps> = ({
  taskId,
  onUpdate,
  onDelete,
}) => {
  const [task, setTask] = useState<Task | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [isLoadingTask, setIsLoadingTask] = useState(true);
  const [isLoadingReminders, setIsLoadingReminders] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch task details
  useEffect(() => {
    const fetchTask = async () => {
      try {
        setIsLoadingTask(true);
        const response = await fetch(`/api/tasks/${taskId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch task');
        }
        const data = await response.json();
        setTask(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setIsLoadingTask(false);
      }
    };

    fetchTask();
  }, [taskId]);

  // Fetch task reminders
  useEffect(() => {
    const fetchReminders = async () => {
      try {
        setIsLoadingReminders(true);
        const response = await fetch(`/api/tasks/${taskId}/reminders`);
        if (!response.ok) {
          throw new Error('Failed to fetch reminders');
        }
        const data = await response.json();
        setReminders(data);
      } catch (err) {
        console.error('Failed to fetch reminders:', err);
        // Don't set error for reminders, just log it
      } finally {
        setIsLoadingReminders(false);
      }
    };

    fetchReminders();
  }, [taskId]);

  // Format date for display
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString();
  };

  // Get status badge color
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'sent':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Get priority badge color
  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoadingTask) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading task details...</div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-red-500">
          {error || 'Task not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* Task Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{task.title}</h1>
        <div className="flex gap-2">
          <span className={`px-2 py-1 text-xs rounded ${getStatusColor(task.status)}`}>
            {task.status.replace('_', ' ')}
          </span>
          <span className={`px-2 py-1 text-xs rounded ${getPriorityColor(task.priority)}`}>
            {task.priority}
          </span>
          {task.recurrence_pattern_id && (
            <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded">
              🔄 Recurring
            </span>
          )}
        </div>
      </div>

      {/* Task Description */}
      {task.description && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-1">Description</h3>
          <p className="text-gray-600">{task.description}</p>
        </div>
      )}

      {/* Task Dates */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <h3 className="font-semibold text-gray-700 mb-1">Created</h3>
          <p className="text-gray-600">{formatDate(task.created_at)}</p>
        </div>
        {task.due_at && (
          <div>
            <h3 className="font-semibold text-gray-700 mb-1">Due Date</h3>
            <p className="text-gray-600">{formatDate(task.due_at)}</p>
          </div>
        )}
        {task.completed_at && (
          <div>
            <h3 className="font-semibold text-gray-700 mb-1">Completed</h3>
            <p className="text-gray-600">{formatDate(task.completed_at)}</p>
          </div>
        )}
        <div>
          <h3 className="font-semibold text-gray-700 mb-1">Last Updated</h3>
          <p className="text-gray-600">{formatDate(task.updated_at)}</p>
        </div>
      </div>

      {/* Reminders Section */}
      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Reminders ({reminders.length})
        </h3>

        {isLoadingReminders ? (
          <div className="text-gray-500 text-sm">Loading reminders...</div>
        ) : reminders.length === 0 ? (
          <div className="text-gray-500 text-sm italic">
            No reminders scheduled for this task.
          </div>
        ) : (
          <div className="space-y-2">
            {reminders.map((reminder) => (
              <div
                key={reminder.id}
                className="p-3 border border-gray-200 rounded-lg bg-gray-50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-medium text-gray-900">
                        {formatDate(reminder.remind_at)}
                      </span>
                      <span className={`px-2 py-0.5 text-xs rounded ${getStatusColor(reminder.delivery_status)}`}>
                        {reminder.delivery_status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600">
                      Channel: <span className="font-medium">{reminder.notification_channel}</span>
                    </div>
                    {reminder.delivery_status === 'failed' && reminder.error_message && (
                      <div className="text-xs text-red-600 mt-1">
                        Error: {reminder.error_message}
                      </div>
                    )}
                    {reminder.retry_count > 0 && (
                      <div className="text-xs text-gray-500 mt-1">
                        Retry attempts: {reminder.retry_count}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-3 border-t pt-4">
        {onUpdate && (
          <button
            onClick={onUpdate}
            className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
          >
            Edit Task
          </button>
        )}
        {onDelete && (
          <button
            onClick={onDelete}
            className="px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700"
          >
            Delete Task
          </button>
        )}
      </div>
    </div>
  );
};

export default TaskDetail;
