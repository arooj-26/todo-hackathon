/**
 * TaskForm component for creating and editing tasks.
 *
 * Includes fields for:
 * - Title and description
 * - Priority and status
 * - Due date
 * - Recurrence pattern
 * - Reminders
 */

'use client';

import { useState } from 'react';
import { RecurrencePatternForm } from './RecurrencePatternForm';
import { DateTimePicker } from './DateTimePicker';
import { ReminderOffsetSelector } from './ReminderOffsetSelector';
import { PrioritySelector } from './PrioritySelector';
import { TagInput } from './TagInput';
import type { TaskCreate, TaskPriority, TaskStatus, RecurrencePattern } from '../hooks/useTasks';

interface TaskFormProps {
  onSubmit: (task: TaskCreate) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  initialData?: Partial<TaskCreate>;
}

export function TaskForm({
  onSubmit,
  onCancel,
  isLoading = false,
  initialData,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title ?? '');
  const [description, setDescription] = useState(initialData?.description ?? '');
  const [priority, setPriority] = useState<TaskPriority>(initialData?.priority ?? 'medium');
  const [status, setStatus] = useState<TaskStatus>(initialData?.status ?? 'todo');
  const [dueAt, setDueAt] = useState<string | null>(initialData?.due_at ?? null);
  const [recurrencePattern, setRecurrencePattern] = useState<RecurrencePattern | null>(
    initialData?.recurrence_pattern ?? null
  );
  const [reminderOffsetMinutes, setReminderOffsetMinutes] = useState<number | null>(
    initialData?.reminder_offset_minutes ?? null
  );
  const [tagNames, setTagNames] = useState<string[]>(initialData?.tag_names ?? []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      alert('Please enter a task title');
      return;
    }

    // Validate reminder requires due date
    if (reminderOffsetMinutes && !dueAt) {
      alert('Please set a due date to enable reminders');
      return;
    }

    const taskData: TaskCreate = {
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      status,
      due_at: dueAt || undefined,
      recurrence_pattern: recurrencePattern ?? undefined,
      reminder_offset_minutes: reminderOffsetMinutes ?? undefined,
      tag_names: tagNames.length > 0 ? tagNames : undefined,
    };

    onSubmit(taskData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
          Title *
        </label>
        <input
          type="text"
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter task title"
          required
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      {/* Description */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task description (optional)"
          rows={3}
          className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
        />
      </div>

      {/* Priority and Status */}
      <div className="grid grid-cols-2 gap-4">
        <PrioritySelector
          value={priority}
          onChange={setPriority}
        />

        <div>
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as TaskStatus)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
          >
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>

      {/* Tags */}
      <TagInput
        value={tagNames}
        onChange={setTagNames}
      />

      {/* Due Date and Reminder */}
      <div className="border-t pt-4 space-y-4">
        <h3 className="text-sm font-semibold text-gray-900">Due Date & Reminders</h3>

        <DateTimePicker
          value={dueAt}
          onChange={setDueAt}
          label="Due Date & Time"
          minDateTime={new Date().toISOString()}
        />

        <ReminderOffsetSelector
          value={reminderOffsetMinutes}
          onChange={setReminderOffsetMinutes}
          hasDueDate={!!dueAt}
        />
      </div>

      {/* Recurrence Pattern */}
      <div className="border-t pt-4">
        <RecurrencePatternForm
          value={recurrencePattern}
          onChange={setRecurrencePattern}
        />
      </div>

      {/* Form Actions */}
      <div className="flex justify-end gap-3 border-t pt-4">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Creating...' : 'Create Task'}
        </button>
      </div>
    </form>
  );
}
