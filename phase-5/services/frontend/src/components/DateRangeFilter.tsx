/**
 * DateRangeFilter component for filtering tasks by due date range.
 *
 * Provides:
 * - Start date picker
 * - End date picker
 * - Clear button to reset range
 * - Validation (end date >= start date)
 */

import React from 'react';

interface DateRangeFilterProps {
  /** Start date (ISO string or undefined) */
  startDate?: string;
  /** End date (ISO string or undefined) */
  endDate?: string;
  /** Callback when date range changes */
  onChange: (startDate: string | undefined, endDate: string | undefined) => void;
  /** Additional CSS classes */
  className?: string;
}

export const DateRangeFilter: React.FC<DateRangeFilterProps> = ({
  startDate,
  endDate,
  onChange,
  className = '',
}) => {
  const handleStartChange = (value: string) => {
    const newStart = value || undefined;
    onChange(newStart, endDate);
  };

  const handleEndChange = (value: string) => {
    const newEnd = value || undefined;
    onChange(startDate, newEnd);
  };

  const handleClear = () => {
    onChange(undefined, undefined);
  };

  // Convert ISO strings to date input format (YYYY-MM-DD)
  const startDateValue = startDate ? startDate.split('T')[0] : '';
  const endDateValue = endDate ? endDate.split('T')[0] : '';

  const hasDateRange = startDate || endDate;

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-1">
        <label className="block text-sm font-medium text-gray-700">
          Due Date Range
        </label>
        {hasDateRange && (
          <button
            type="button"
            onClick={handleClear}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
          >
            Clear
          </button>
        )}
      </div>

      <div className="space-y-2">
        {/* Start date */}
        <div>
          <label htmlFor="due-date-start" className="block text-xs text-gray-600 mb-1">
            From
          </label>
          <input
            type="date"
            id="due-date-start"
            value={startDateValue}
            onChange={(e) => {
              const value = e.target.value;
              // Convert to ISO string with time
              const isoValue = value ? `${value}T00:00:00.000Z` : '';
              handleStartChange(isoValue);
            }}
            max={endDateValue || undefined}
            className="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* End date */}
        <div>
          <label htmlFor="due-date-end" className="block text-xs text-gray-600 mb-1">
            To
          </label>
          <input
            type="date"
            id="due-date-end"
            value={endDateValue}
            onChange={(e) => {
              const value = e.target.value;
              // Convert to ISO string with time (end of day)
              const isoValue = value ? `${value}T23:59:59.999Z` : '';
              handleEndChange(isoValue);
            }}
            min={startDateValue || undefined}
            className="block w-full px-3 py-2 text-sm border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {hasDateRange && (
        <p className="text-xs text-gray-500 mt-2">
          {startDate && endDate
            ? 'Showing tasks due between selected dates'
            : startDate
            ? 'Showing tasks due after selected date'
            : 'Showing tasks due before selected date'}
        </p>
      )}
    </div>
  );
};

export default DateRangeFilter;
