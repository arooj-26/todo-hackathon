/**
 * TaskList component - displays and manages user tasks.
 *
 * Features:
 * - Displays tasks with status, priority, and due dates
 * - Filtering by status, priority, and search
 * - Sorting by various fields
 * - Task completion toggling with next instance notification
 * - Stop recurrence for recurring tasks
 * - Task editing and deletion
 */

'use client';

import { useState } from 'react';
import { type Task } from '../hooks/useTasks';
import { useSearch } from '../hooks/useSearch';
import { TaskHistory } from './TaskHistory';
import { useNotifications } from '../lib/store';
import { getPriorityBadgeClasses, getPriorityLabel } from './PrioritySelector';
import { SearchBar } from './SearchBar';
import { FilterPanel } from './FilterPanel';
import { SortSelector } from './SortSelector';

/**
 * Props for TaskList component.
 */
interface TaskListProps {
  /**
   * Initial filter by status.
   */
  initialStatus?: 'todo' | 'in_progress' | 'completed';

  /**
   * Initial filter by priority.
   */
  initialPriority?: 'low' | 'medium' | 'high';
}

/**
 * Calculate time until task is due and format as human-readable string.
 *
 * @param dueAt - ISO date string of when task is due
 * @returns Formatted string like "Due in 2 hours" or "Overdue by 1 day"
 */
function formatDueTime(dueAt: string): { text: string; isOverdue: boolean } {
  const now = new Date();
  const due = new Date(dueAt);
  const diffMs = due.getTime() - now.getTime();
  const isOverdue = diffMs < 0;
  const absDiffMs = Math.abs(diffMs);

  const minutes = Math.floor(absDiffMs / (1000 * 60));
  const hours = Math.floor(absDiffMs / (1000 * 60 * 60));
  const days = Math.floor(absDiffMs / (1000 * 60 * 60 * 24));

  let timeStr: string;
  if (minutes < 60) {
    timeStr = `${minutes} minute${minutes !== 1 ? 's' : ''}`;
  } else if (hours < 24) {
    timeStr = `${hours} hour${hours !== 1 ? 's' : ''}`;
  } else {
    timeStr = `${days} day${days !== 1 ? 's' : ''}`;
  }

  return {
    text: isOverdue ? `Overdue by ${timeStr}` : `Due in ${timeStr}`,
    isOverdue,
  };
}

/**
 * TaskList component.
 *
 * Displays a list of tasks with filtering, sorting, and actions.
 * Uses TanStack Query for server state management.
 *
 * @param props - Component props
 * @returns TaskList component
 */
export function TaskList({ initialStatus, initialPriority }: TaskListProps) {
  // Use the new useSearch hook which handles search, filters, and pagination
  const [showHistoryFor, setShowHistoryFor] = useState<number | null>(null);

  // Notifications
  const { addNotification } = useNotifications();

  // Initialize search with filters and pagination
  const {
    search,
    setSearch,
    status: statusFilter,
    setStatus: setStatusFilter,
    priority: priorityFilter,
    setPriority: setPriorityFilter,
    tags: tagFilters,
    setTags: setTagFilters,
    dueDateStart,
    dueDateEnd,
    setDateRange,
    sort,
    setSort,
    tasks,
    total,
    isLoading,
    error,
    currentPage,
    totalPages,
    hasNextPage,
    hasPreviousPage,
    nextPage,
    previousPage,
    goToPage,
    completeTask,
    isCompleting,
    stopRecurrence,
    isStoppingRecurrence,
    clearFilters,
    hasActiveFilters,
    hasActiveSort,
  } = useSearch({
    status: initialStatus,
    priority: initialPriority,
  });

  const handleCompleteTask = (task: Task) => {
    completeTask(task.id, {
      onSuccess: () => {
        if (task.recurrence_pattern_id) {
          addNotification({
            type: 'success',
            message: `Task completed! Next instance will be created automatically.`,
          });
        } else {
          addNotification({
            type: 'success',
            message: 'Task completed successfully!',
          });
        }
      },
      onError: () => {
        addNotification({
          type: 'error',
          message: 'Failed to complete task',
        });
      },
    });
  };

  const handleStopRecurrence = (taskId: number) => {
    if (confirm('Are you sure you want to stop the recurrence for this task?')) {
      stopRecurrence(taskId, {
        onSuccess: () => {
          addNotification({
            type: 'success',
            message: 'Recurrence stopped successfully!',
          });
        },
        onError: () => {
          addNotification({
            type: 'error',
            message: 'Failed to stop recurrence',
          });
        },
      });
    }
  };

  const handleTagClick = (tagName: string) => {
    // Toggle tag filter
    if (tagFilters.includes(tagName)) {
      setTagFilters(tagFilters.filter((t) => t !== tagName));
    } else {
      setTagFilters([...tagFilters, tagName]);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading tasks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-red-500">
          Error loading tasks: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search and Filters Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Bar and Sort Controls */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search Bar */}
          <SearchBar value={search} onChange={setSearch} placeholder="Search tasks by title or description..." />

          {/* Sort Controls */}
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Showing {tasks.length} of {total} tasks
              {(hasActiveFilters || hasActiveSort) && (
                <button
                  onClick={clearFilters}
                  className="ml-2 text-blue-600 hover:text-blue-800 font-medium"
                >
                  Clear all filters
                </button>
              )}
            </div>
            <SortSelector
              value={sort}
              onChange={setSort}
              hasSearch={!!search}
              showCompoundOptions={true}
            />
          </div>
        </div>

        {/* Filter Panel */}
        <div className="lg:col-span-1">
          <FilterPanel
            statusFilter={statusFilter}
            onStatusChange={setStatusFilter}
            priorityFilter={priorityFilter}
            onPriorityChange={setPriorityFilter}
            tagFilters={tagFilters}
            onTagFiltersChange={setTagFilters}
            dueDateStart={dueDateStart}
            dueDateEnd={dueDateEnd}
            onDateRangeChange={setDateRange}
          />
        </div>
      </div>

      {/* Legacy inline filters - keeping for backwards compatibility, can be removed */}
      <div className="hidden gap-4 items-center">
        {/* Status filter */}
        <select
          value={statusFilter || ''}
          onChange={(e) => setStatusFilter(e.target.value as any || undefined)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All statuses</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>

        {/* Priority filter */}
        <select
          value={priorityFilter || ''}
          onChange={(e) => setPriorityFilter(e.target.value as any || undefined)}
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Task list */}
      <div className="space-y-2">
        {tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No tasks found. Create your first task to get started!
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="font-medium text-lg">{task.title}</h3>
                    {task.recurrence_pattern_id && (
                      <span className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded">
                        🔄 Recurring
                      </span>
                    )}
                  </div>
                  {task.description && (
                    <p className="text-gray-600 text-sm mt-1">
                      {task.description}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-2 mt-2">
                    <span
                      className={`px-2 py-1 text-xs rounded ${
                        task.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : task.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {task.status.replace('_', ' ')}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs rounded border ${getPriorityBadgeClasses(task.priority)}`}
                    >
                      {getPriorityLabel(task.priority)}
                    </span>
                    {task.due_at && (() => {
                      const { text, isOverdue } = formatDueTime(task.due_at);
                      return (
                        <span
                          className={`px-2 py-1 text-xs rounded ${
                            isOverdue
                              ? 'bg-red-100 text-red-800'
                              : 'bg-purple-100 text-purple-800'
                          }`}
                          title={`Due: ${new Date(task.due_at).toLocaleString()}`}
                        >
                          📅 {text}
                        </span>
                      );
                    })()}
                    {/* Tag pills */}
                    {task.tags && task.tags.map((tag) => (
                      <button
                        key={tag}
                        onClick={() => handleTagClick(tag)}
                        className={`px-2 py-1 text-xs rounded border cursor-pointer transition-colors ${
                          tagFilters.includes(tag)
                            ? 'bg-blue-600 text-white border-blue-700'
                            : 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
                        }`}
                        title={`Click to ${tagFilters.includes(tag) ? 'remove' : 'add'} filter`}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>

                  {/* Task History */}
                  {task.recurrence_pattern_id && showHistoryFor === task.id && (
                    <div className="mt-4 border-t pt-4">
                      <TaskHistory parentTaskId={task.id} />
                    </div>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  {/* Complete button */}
                  {task.status !== 'completed' && (
                    <button
                      onClick={() => handleCompleteTask(task)}
                      disabled={isCompleting}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                    >
                      {isCompleting ? 'Completing...' : 'Complete'}
                    </button>
                  )}

                  {/* Stop recurrence button */}
                  {task.recurrence_pattern_id && (
                    <button
                      onClick={() => handleStopRecurrence(task.id)}
                      disabled={isStoppingRecurrence}
                      className="px-3 py-1 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50"
                    >
                      Stop Recurrence
                    </button>
                  )}

                  {/* Show/Hide history */}
                  {task.recurrence_pattern_id && (
                    <button
                      onClick={() =>
                        setShowHistoryFor(showHistoryFor === task.id ? null : task.id)
                      }
                      className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
                    >
                      {showHistoryFor === task.id ? 'Hide History' : 'Show History'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-lg">
          <div className="flex flex-1 justify-between sm:hidden">
            {/* Mobile pagination */}
            <button
              onClick={previousPage}
              disabled={!hasPreviousPage}
              className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              onClick={nextPage}
              disabled={!hasNextPage}
              className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Page <span className="font-medium">{currentPage}</span> of{' '}
                <span className="font-medium">{totalPages}</span>
              </p>
            </div>
            <div>
              <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                {/* Previous button */}
                <button
                  onClick={previousPage}
                  disabled={!hasPreviousPage}
                  className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="sr-only">Previous</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path
                      fillRule="evenodd"
                      d="M12.79 5.23a.75.75 0 01-.02 1.06L8.832 10l3.938 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.08l4.5-4.25a.75.75 0 011.06.02z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>

                {/* Page numbers */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  // Show first 2, current, and last 2 pages
                  let pageNum: number;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }

                  return (
                    <button
                      key={pageNum}
                      onClick={() => goToPage(pageNum)}
                      className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                        currentPage === pageNum
                          ? 'z-10 bg-blue-600 text-white focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
                          : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}

                {/* Next button */}
                <button
                  onClick={nextPage}
                  disabled={!hasNextPage}
                  className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="sr-only">Next</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path
                      fillRule="evenodd"
                      d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
