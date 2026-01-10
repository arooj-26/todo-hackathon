/**
 * StatusFilter component for filtering tasks by status.
 *
 * Provides a dropdown to filter tasks by:
 * - All statuses (no filter)
 * - To Do (todo)
 * - In Progress (in_progress)
 * - Completed (completed)
 */

import React from 'react';
import type { TaskStatus } from '../hooks/useTasks';

interface StatusFilterProps {
  /** Current status filter value */
  value?: TaskStatus;
  /** Callback when status filter changes */
  onChange: (status: TaskStatus | undefined) => void;
  /** Additional CSS classes */
  className?: string;
}

export const StatusFilter: React.FC<StatusFilterProps> = ({
  value,
  onChange,
  className = '',
}) => {
  return (
    <div className={className}>
      <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
        Status
      </label>
      <select
        id="status-filter"
        value={value || ''}
        onChange={(e) => onChange((e.target.value as TaskStatus) || undefined)}
        className="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">All statuses</option>
        <option value="todo">To Do</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
      </select>
    </div>
  );
};

export default StatusFilter;
