/**
 * SortSelector component - dropdown for selecting sort options.
 *
 * Features:
 * - User-friendly sort option labels
 * - Support for primary and secondary sort criteria (compound sorting)
 * - Default sort based on search context (relevance when searching, newest when not)
 */

'use client';

import { useState } from 'react';

/**
 * Sort option configuration.
 */
export interface SortOption {
  value: string;
  label: string;
  description?: string;
}

/**
 * Available sort options with user-friendly labels.
 */
export const SORT_OPTIONS: SortOption[] = [
  // Priority sorting
  {
    value: 'priority_desc',
    label: 'Priority: High to Low',
    description: 'Show high priority tasks first',
  },
  {
    value: 'priority_asc',
    label: 'Priority: Low to High',
    description: 'Show low priority tasks first',
  },
  // Due date sorting
  {
    value: 'due_date_asc',
    label: 'Due Date: Earliest First',
    description: 'Show tasks due soonest first',
  },
  {
    value: 'due_date_desc',
    label: 'Due Date: Latest First',
    description: 'Show tasks due later first',
  },
  // Created date sorting
  {
    value: 'created_desc',
    label: 'Created: Newest First',
    description: 'Show recently created tasks first',
  },
  {
    value: 'created_asc',
    label: 'Created: Oldest First',
    description: 'Show oldest tasks first',
  },
  // Title sorting
  {
    value: 'title_asc',
    label: 'Title: A to Z',
    description: 'Sort alphabetically',
  },
  {
    value: 'title_desc',
    label: 'Title: Z to A',
    description: 'Sort reverse alphabetically',
  },
];

/**
 * Compound sort presets (primary + secondary).
 */
export const COMPOUND_SORT_PRESETS: SortOption[] = [
  {
    value: 'priority_desc,due_date_asc',
    label: 'Priority (High to Low), then Due Date (Earliest)',
    description: 'High priority tasks with earliest due dates first',
  },
  {
    value: 'priority_desc,created_desc',
    label: 'Priority (High to Low), then Newest',
    description: 'High priority tasks, most recent first',
  },
  {
    value: 'due_date_asc,priority_desc',
    label: 'Due Date (Earliest), then Priority (High to Low)',
    description: 'Tasks due soonest, high priority first',
  },
];

/**
 * Props for SortSelector component.
 */
interface SortSelectorProps {
  /**
   * Current sort value (can be compound: "priority_desc,due_date_asc").
   */
  value?: string;

  /**
   * Callback when sort changes.
   */
  onChange: (sort: string | undefined) => void;

  /**
   * Whether a search query is active (affects default sort display).
   */
  hasSearch?: boolean;

  /**
   * Show compound sort options.
   */
  showCompoundOptions?: boolean;
}

/**
 * SortSelector component.
 *
 * Provides a dropdown for selecting sort options with user-friendly labels.
 *
 * @param props - Component props
 * @returns SortSelector component
 */
export function SortSelector({
  value,
  onChange,
  hasSearch = false,
  showCompoundOptions = true,
}: SortSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Get current sort label
  const getCurrentLabel = () => {
    if (!value) {
      return hasSearch ? 'Sort: Relevance' : 'Sort: Newest First';
    }

    // Check simple options first
    const simpleOption = SORT_OPTIONS.find((opt) => opt.value === value);
    if (simpleOption) {
      return `Sort: ${simpleOption.label}`;
    }

    // Check compound options
    if (showCompoundOptions) {
      const compoundOption = COMPOUND_SORT_PRESETS.find((opt) => opt.value === value);
      if (compoundOption) {
        return `Sort: ${compoundOption.label}`;
      }
    }

    // Fallback for custom compound sorts
    return `Sort: ${value}`;
  };

  const handleSelect = (sortValue: string) => {
    onChange(sortValue === '' ? undefined : sortValue);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      {/* Dropdown button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 text-sm border border-gray-300 rounded-md bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <svg
          className="w-4 h-4 text-gray-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
          />
        </svg>
        <span className="font-medium">{getCurrentLabel()}</span>
        <svg
          className={`w-4 h-4 text-gray-500 transition-transform ${
            isOpen ? 'transform rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown menu */}
      {isOpen && (
        <div className="absolute z-10 mt-2 w-80 bg-white border border-gray-200 rounded-md shadow-lg max-h-96 overflow-y-auto">
          {/* Default option */}
          <button
            type="button"
            onClick={() => handleSelect('')}
            className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${
              !value ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
            }`}
          >
            <div className="font-medium">
              {hasSearch ? 'Relevance (Default)' : 'Newest First (Default)'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {hasSearch ? 'Sort by search relevance' : 'Most recently created tasks first'}
            </div>
          </button>

          <div className="border-t border-gray-200 my-1" />

          {/* Simple sort options */}
          <div className="px-2 py-1 text-xs font-semibold text-gray-500 uppercase">
            Simple Sort
          </div>
          {SORT_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleSelect(option.value)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${
                value === option.value ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
              }`}
            >
              <div className="font-medium">{option.label}</div>
              {option.description && (
                <div className="text-xs text-gray-500 mt-1">{option.description}</div>
              )}
            </button>
          ))}

          {/* Compound sort options */}
          {showCompoundOptions && (
            <>
              <div className="border-t border-gray-200 my-1" />
              <div className="px-2 py-1 text-xs font-semibold text-gray-500 uppercase">
                Compound Sort
              </div>
              {COMPOUND_SORT_PRESETS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleSelect(option.value)}
                  className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-50 ${
                    value === option.value ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                  }`}
                >
                  <div className="font-medium">{option.label}</div>
                  {option.description && (
                    <div className="text-xs text-gray-500 mt-1">{option.description}</div>
                  )}
                </button>
              ))}
            </>
          )}
        </div>
      )}

      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}
    </div>
  );
}
