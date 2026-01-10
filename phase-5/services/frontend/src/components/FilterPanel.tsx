/**
 * FilterPanel component for filtering tasks by status, priority, tags, and date range.
 *
 * Provides a comprehensive filtering interface with:
 * - Status filter (Todo, In Progress, Completed)
 * - Priority filter (High, Medium, Low)
 * - Tag filter with multi-select
 * - Due date range filter
 * - Clear all filters button
 */

import React from 'react';
import type { TaskStatus, TaskPriority } from '../hooks/useTasks';
import { useTags } from '../hooks/useTags';
import { StatusFilter } from './StatusFilter';
import { DateRangeFilter } from './DateRangeFilter';

interface FilterPanelProps {
  /** Current status filter */
  statusFilter?: TaskStatus;
  /** Callback when status filter changes */
  onStatusChange: (status: TaskStatus | undefined) => void;

  /** Current priority filter */
  priorityFilter?: TaskPriority;
  /** Callback when priority filter changes */
  onPriorityChange: (priority: TaskPriority | undefined) => void;

  /** Current tag filters (AND logic) */
  tagFilters: string[];
  /** Callback when tag filters change */
  onTagFiltersChange: (tags: string[]) => void;

  /** Due date range start */
  dueDateStart?: string;
  /** Due date range end */
  dueDateEnd?: string;
  /** Callback when date range changes */
  onDateRangeChange: (startDate: string | undefined, endDate: string | undefined) => void;

  /** Additional CSS classes */
  className?: string;
}

export const FilterPanel: React.FC<FilterPanelProps> = ({
  statusFilter,
  onStatusChange,
  priorityFilter,
  onPriorityChange,
  tagFilters,
  onTagFiltersChange,
  dueDateStart,
  dueDateEnd,
  onDateRangeChange,
  className = '',
}) => {
  const { tags } = useTags({ limit: 50 });

  const handleClearAll = () => {
    onStatusChange(undefined);
    onPriorityChange(undefined);
    onTagFiltersChange([]);
    onDateRangeChange(undefined, undefined);
  };

  const handleTagToggle = (tagName: string) => {
    if (tagFilters.includes(tagName)) {
      onTagFiltersChange(tagFilters.filter((t) => t !== tagName));
    } else {
      onTagFiltersChange([...tagFilters, tagName]);
    }
  };

  const hasActiveFilters = statusFilter || priorityFilter || tagFilters.length > 0 || dueDateStart || dueDateEnd;

  return (
    <div className={`filter-panel bg-gray-50 rounded-lg p-4 space-y-4 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters && (
          <button
            onClick={handleClearAll}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Status Filter */}
      <StatusFilter value={statusFilter} onChange={onStatusChange} />

      {/* Priority Filter */}
      <div>
        <label htmlFor="priority-filter" className="block text-xs font-medium text-gray-700 mb-1">
          Priority
        </label>
        <select
          id="priority-filter"
          value={priorityFilter || ''}
          onChange={(e) => onPriorityChange((e.target.value as TaskPriority) || undefined)}
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Tag Filter */}
      <div>
        <label className="block text-xs font-medium text-gray-700 mb-2">
          Tags {tagFilters.length > 0 && `(${tagFilters.length} selected)`}
        </label>
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {tags.length === 0 ? (
            <p className="text-xs text-gray-500 italic">No tags available</p>
          ) : (
            tags.map((tag) => {
              const isSelected = tagFilters.includes(tag.name);
              return (
                <button
                  key={tag.id}
                  onClick={() => handleTagToggle(tag.name)}
                  className={`w-full flex items-center justify-between px-3 py-2 text-sm rounded-md border transition-colors ${
                    isSelected
                      ? 'bg-blue-100 border-blue-300 text-blue-900'
                      : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => {}} // Handled by button onClick
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      aria-label={`Filter by ${tag.name}`}
                    />
                    <span>{tag.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{tag.usage_count}</span>
                </button>
              );
            })
          )}
        </div>
        {tagFilters.length > 0 && (
          <p className="text-xs text-gray-500 mt-2">
            Tasks must have <strong>all</strong> selected tags
          </p>
        )}
      </div>

      {/* Due Date Range Filter */}
      <DateRangeFilter
        startDate={dueDateStart}
        endDate={dueDateEnd}
        onChange={onDateRangeChange}
      />
    </div>
  );
};

export default FilterPanel;
