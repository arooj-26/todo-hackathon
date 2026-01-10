/**
 * DateTimePicker component for selecting task due dates and times.
 *
 * Provides a user-friendly interface for selecting both date and time
 * for task due dates with validation.
 */

import React from 'react';

interface DateTimePickerProps {
  /** Current date-time value (ISO 8601 string) */
  value: string | null;
  /** Callback when date-time changes */
  onChange: (value: string | null) => void;
  /** Label for the input */
  label?: string;
  /** Whether the field is required */
  required?: boolean;
  /** Minimum allowed date-time (ISO 8601 string) */
  minDateTime?: string;
  /** Additional CSS classes */
  className?: string;
  /** Error message to display */
  error?: string;
}

export const DateTimePicker: React.FC<DateTimePickerProps> = ({
  value,
  onChange,
  label = 'Due Date & Time',
  required = false,
  minDateTime,
  className = '',
  error,
}) => {
  // Convert ISO string to datetime-local format (YYYY-MM-DDTHH:mm)
  const toLocalDateTime = (isoString: string | null): string => {
    if (!isoString) return '';

    try {
      const date = new Date(isoString);
      // Format: YYYY-MM-DDTHH:mm
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');

      return `${year}-${month}-${day}T${hours}:${minutes}`;
    } catch (e) {
      return '';
    }
  };

  // Convert datetime-local format to ISO string
  const toISOString = (localDateTime: string): string | null => {
    if (!localDateTime) return null;

    try {
      const date = new Date(localDateTime);
      return date.toISOString();
    } catch (e) {
      return null;
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const localValue = e.target.value;
    const isoValue = toISOString(localValue);
    onChange(isoValue);
  };

  const handleClear = () => {
    onChange(null);
  };

  const localValue = toLocalDateTime(value);
  const minLocal = minDateTime ? toLocalDateTime(minDateTime) : undefined;

  return (
    <div className={`date-time-picker ${className}`}>
      <label htmlFor="due-date-time" className="block text-sm font-medium text-gray-700 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>

      <div className="flex items-center gap-2">
        <input
          id="due-date-time"
          type="datetime-local"
          value={localValue}
          onChange={handleChange}
          min={minLocal}
          required={required}
          className={`
            flex-1 px-3 py-2 border rounded-md shadow-sm
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            ${error ? 'border-red-500' : 'border-gray-300'}
          `}
        />

        {value && (
          <button
            type="button"
            onClick={handleClear}
            className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
            title="Clear date"
          >
            Clear
          </button>
        )}
      </div>

      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}

      {value && (
        <p className="mt-1 text-xs text-gray-500">
          Selected: {new Date(value).toLocaleString()}
        </p>
      )}
    </div>
  );
};

export default DateTimePicker;
