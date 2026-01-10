/**
 * Custom hook for managing search and filter state.
 *
 * Provides state management for:
 * - Search query
 * - Status filter
 * - Priority filter
 * - Tag filters
 * - Due date range filter
 * - Sort criteria
 * - Pagination (limit, offset)
 *
 * Integrates with useTasks to fetch filtered results.
 * Persists state in URL query parameters for shareable links.
 */

import { useState, useCallback, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useRouter, usePathname } from 'next/navigation';
import { useTasks, type TaskStatus, type TaskPriority } from './useTasks';

/**
 * Search and filter parameters.
 */
export interface SearchParams {
  search?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  tags?: string[];
  dueDateStart?: string;
  dueDateEnd?: string;
  sort?: string;
  limit?: number;
  offset?: number;
}

/**
 * Hook for search and filter state management with URL persistence.
 *
 * @param initialParams - Initial search parameters (overridden by URL params)
 * @returns Search state and setters
 */
export function useSearch(initialParams?: SearchParams) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Initialize state from URL parameters or initialParams
  const getInitialValue = <T,>(urlKey: string, defaultValue: T, parser?: (val: string) => T): T => {
    const urlValue = searchParams.get(urlKey);
    if (urlValue !== null) {
      return parser ? parser(urlValue) : (urlValue as unknown as T);
    }
    return defaultValue;
  };

  // Search and filter state (initialize from URL)
  const [search, setSearchState] = useState<string>(() =>
    getInitialValue('search', initialParams?.search || '')
  );
  const [status, setStatusState] = useState<TaskStatus | undefined>(() =>
    getInitialValue('status', initialParams?.status, (val) => val as TaskStatus)
  );
  const [priority, setPriorityState] = useState<TaskPriority | undefined>(() =>
    getInitialValue('priority', initialParams?.priority, (val) => val as TaskPriority)
  );
  const [tags, setTagsState] = useState<string[]>(() => {
    const urlTags = searchParams.getAll('tag');
    return urlTags.length > 0 ? urlTags : (initialParams?.tags || []);
  });
  const [dueDateStart, setDueDateStartState] = useState<string | undefined>(() =>
    getInitialValue('dueDateStart', initialParams?.dueDateStart)
  );
  const [dueDateEnd, setDueDateEndState] = useState<string | undefined>(() =>
    getInitialValue('dueDateEnd', initialParams?.dueDateEnd)
  );
  const [sort, setSortState] = useState<string | undefined>(() =>
    getInitialValue('sort', initialParams?.sort)
  );
  const [limit, setLimitState] = useState<number>(() =>
    getInitialValue('limit', initialParams?.limit || 50, parseInt)
  );
  const [offset, setOffsetState] = useState<number>(() =>
    getInitialValue('offset', initialParams?.offset || 0, parseInt)
  );

  // Update URL when state changes
  const updateURL = useCallback((params: Record<string, string | string[] | undefined>) => {
    const newParams = new URLSearchParams();

    // Add all non-empty parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        if (Array.isArray(value)) {
          // For arrays (like tags), add each item separately
          value.forEach((item) => newParams.append(key, item));
        } else {
          newParams.set(key, String(value));
        }
      }
    });

    // Update URL without navigation
    const newURL = `${pathname}?${newParams.toString()}`;
    router.replace(newURL, { scroll: false });
  }, [pathname, router]);

  // Sync state to URL on changes
  useEffect(() => {
    updateURL({
      search: search || undefined,
      status,
      priority,
      tag: tags.length > 0 ? tags : undefined,
      dueDateStart,
      dueDateEnd,
      sort,
      limit: limit !== 50 ? String(limit) : undefined, // Only include if not default
      offset: offset !== 0 ? String(offset) : undefined, // Only include if not default
    });
  }, [search, status, priority, tags, dueDateStart, dueDateEnd, sort, limit, offset, updateURL]);

  // Build query params for useTasks
  const queryParams = {
    search: search || undefined,
    status,
    priority,
    tags: tags.length > 0 ? tags : undefined,
    due_date_start: dueDateStart,
    due_date_end: dueDateEnd,
    sort,
    limit,
    offset,
  };

  // Fetch tasks with current filters
  const tasksQuery = useTasks(queryParams);

  // Clear all filters
  const clearFilters = useCallback(() => {
    setSearchState('');
    setStatusState(undefined);
    setPriorityState(undefined);
    setTagsState([]);
    setDueDateStartState(undefined);
    setDueDateEndState(undefined);
    setSortState(undefined);
    setOffsetState(0); // Reset to first page
  }, []);

  // Set date range
  const setDateRange = useCallback((start: string | undefined, end: string | undefined) => {
    setDueDateStartState(start);
    setDueDateEndState(end);
    setOffsetState(0); // Reset to first page when filter changes
  }, []);

  // Update search (resets to first page)
  const updateSearch = useCallback((value: string) => {
    setSearchState(value);
    setOffsetState(0);
  }, []);

  // Update status filter (resets to first page)
  const updateStatus = useCallback((value: TaskStatus | undefined) => {
    setStatusState(value);
    setOffsetState(0);
  }, []);

  // Update priority filter (resets to first page)
  const updatePriority = useCallback((value: TaskPriority | undefined) => {
    setPriorityState(value);
    setOffsetState(0);
  }, []);

  // Update tag filters (resets to first page)
  const updateTags = useCallback((value: string[]) => {
    setTagsState(value);
    setOffsetState(0);
  }, []);

  // Update sort (resets to first page)
  const updateSort = useCallback((value: string | undefined) => {
    setSortState(value);
    setOffsetState(0);
  }, []);

  // Pagination helpers
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil((tasksQuery.total || 0) / limit);
  const hasNextPage = currentPage < totalPages;
  const hasPreviousPage = currentPage > 1;

  const goToPage = useCallback((page: number) => {
    const newOffset = (page - 1) * limit;
    setOffsetState(Math.max(0, newOffset));
  }, [limit]);

  const nextPage = useCallback(() => {
    if (hasNextPage) {
      setOffsetState(offset + limit);
    }
  }, [hasNextPage, offset, limit]);

  const previousPage = useCallback(() => {
    if (hasPreviousPage) {
      setOffsetState(Math.max(0, offset - limit));
    }
  }, [hasPreviousPage, offset, limit]);

  // Check if any filters are active
  const hasActiveFilters = !!(
    search ||
    status ||
    priority ||
    tags.length > 0 ||
    dueDateStart ||
    dueDateEnd
  );

  // Check if sort is active (not default)
  const hasActiveSort = !!sort;

  return {
    // State
    search,
    status,
    priority,
    tags,
    dueDateStart,
    dueDateEnd,
    sort,
    limit,
    offset,

    // Setters
    setSearch: updateSearch,
    setStatus: updateStatus,
    setPriority: updatePriority,
    setTags: updateTags,
    setDateRange,
    setSort: updateSort,
    setLimit: setLimitState,
    setOffset: setOffsetState,

    // Clear all
    clearFilters,
    hasActiveFilters,
    hasActiveSort,

    // Task query results
    tasks: tasksQuery.tasks,
    total: tasksQuery.total,
    isLoading: tasksQuery.isLoading,
    isError: tasksQuery.isError,
    error: tasksQuery.error,

    // Pagination
    currentPage,
    totalPages,
    hasNextPage,
    hasPreviousPage,
    goToPage,
    nextPage,
    previousPage,

    // Mutations (from useTasks)
    createTask: tasksQuery.createTask,
    createTaskAsync: tasksQuery.createTaskAsync,
    isCreating: tasksQuery.isCreating,
    completeTask: tasksQuery.completeTask,
    completeTaskAsync: tasksQuery.completeTaskAsync,
    isCompleting: tasksQuery.isCompleting,
    updateTask: tasksQuery.updateTask,
    updateTaskAsync: tasksQuery.updateTaskAsync,
    isUpdating: tasksQuery.isUpdating,
    stopRecurrence: tasksQuery.stopRecurrence,
    stopRecurrenceAsync: tasksQuery.stopRecurrenceAsync,
    isStoppingRecurrence: tasksQuery.isStoppingRecurrence,
  };
}

export default useSearch;
