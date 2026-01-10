/**
 * PrioritySelector component for selecting task priority.
 *
 * Provides High, Medium, and Low priority options with color coding.
 */

import React from 'react';
import { TaskPriority } from '../hooks/useTasks';

interface PrioritySelectorProps {
  /** Current priority value */
  value: TaskPriority;
  /** Callback when priority changes */
  onChange: (priority: TaskPriority) => void;
  /** Label for the selector */
  label?: string;
  /** Additional CSS classes */
  className?: string;
}

// Priority options with colors
const PRIORITY_OPTIONS: Array<{
  value: TaskPriority;
  label: string;
  colorClass: string;
}> = [
  { value: 'high', label: 'High', colorClass: 'text-red-600 bg-red-50 border-red-300' },
  { value: 'medium', label: 'Medium', colorClass: 'text-yellow-600 bg-yellow-50 border-yellow-300' },
  { value: 'low', label: 'Low', colorClass: 'text-green-600 bg-green-50 border-green-300' },
];

export const PrioritySelector: React.FC<PrioritySelectorProps> = ({
  value,
  onChange,
  label = 'Priority',
  className = '',
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onChange(e.target.value as TaskPriority);
  };

  // Get color class for selected priority
  const selectedOption = PRIORITY_OPTIONS.find((opt) => opt.value === value);
  const colorClass = selectedOption?.colorClass || '';

  return (
    <div className={`priority-selector ${className}`}>
      <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>

      <select
        id="priority"
        value={value}
        onChange={handleChange}
        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${colorClass}`}
      >
        {PRIORITY_OPTIONS.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
};

/**
 * Get badge color classes for a priority.
 *
 * @param priority - Task priority
 * @returns CSS classes for priority badge
 */
export function getPriorityBadgeClasses(priority: TaskPriority): string {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'low':
      return 'bg-green-100 text-green-800 border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

/**
 * Get priority label with capitalization.
 *
 * @param priority - Task priority
 * @returns Formatted priority label
 */
export function getPriorityLabel(priority: TaskPriority): string {
  return priority.charAt(0).toUpperCase() + priority.slice(1);
}

export default PrioritySelector;
