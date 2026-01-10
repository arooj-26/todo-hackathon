/**
 * ReminderOffsetSelector component for selecting when to send reminders.
 *
 * Provides preset options (1 day, 1 hour, 15 min) and custom offset input
 * for scheduling task reminders before the due date.
 */

import React, { useState } from 'react';

interface ReminderOffsetSelectorProps {
  /** Current offset in minutes */
  value: number | null;
  /** Callback when offset changes */
  onChange: (minutes: number | null) => void;
  /** Label for the selector */
  label?: string;
  /** Additional CSS classes */
  className?: string;
  /** Whether due date is set (required for reminders) */
  hasDueDate?: boolean;
}

// Preset reminder offsets in minutes
const PRESET_OFFSETS = [
  { label: '15 minutes before', value: 15 },
  { label: '1 hour before', value: 60 },
  { label: '1 day before', value: 1440 }, // 24 * 60
  { label: 'Custom', value: 'custom' as const },
  { label: 'No reminder', value: null },
];

export const ReminderOffsetSelector: React.FC<ReminderOffsetSelectorProps> = ({
  value,
  onChange,
  label = 'Reminder',
  className = '',
  hasDueDate = true,
}) => {
  const [showCustomInput, setShowCustomInput] = useState(false);
  const [customValue, setCustomValue] = useState<string>('');
  const [customUnit, setCustomUnit] = useState<'minutes' | 'hours' | 'days'>('hours');

  // Determine which preset is selected
  const getSelectedPreset = (): string | number | null => {
    if (value === null) return null;

    const preset = PRESET_OFFSETS.find((p) => p.value === value);
    if (preset) return preset.value;

    return 'custom';
  };

  const selectedPreset = getSelectedPreset();

  const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedValue = e.target.value;

    if (selectedValue === 'null') {
      onChange(null);
      setShowCustomInput(false);
    } else if (selectedValue === 'custom') {
      setShowCustomInput(true);
      // Don't change the value yet, wait for custom input
    } else {
      const minutes = parseInt(selectedValue, 10);
      onChange(minutes);
      setShowCustomInput(false);
    }
  };

  const handleCustomValueChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setCustomValue(newValue);

    // Convert to minutes based on unit
    const numValue = parseInt(newValue, 10);
    if (!isNaN(numValue) && numValue > 0) {
      let minutes = numValue;
      if (customUnit === 'hours') {
        minutes = numValue * 60;
      } else if (customUnit === 'days') {
        minutes = numValue * 1440;
      }
      onChange(minutes);
    }
  };

  const handleCustomUnitChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newUnit = e.target.value as 'minutes' | 'hours' | 'days';
    setCustomUnit(newUnit);

    // Recalculate minutes with new unit
    const numValue = parseInt(customValue, 10);
    if (!isNaN(numValue) && numValue > 0) {
      let minutes = numValue;
      if (newUnit === 'hours') {
        minutes = numValue * 60;
      } else if (newUnit === 'days') {
        minutes = numValue * 1440;
      }
      onChange(minutes);
    }
  };

  // Format current value for display
  const formatCurrentValue = (): string => {
    if (value === null) return 'No reminder';
    if (value < 60) return `${value} minutes before`;
    if (value < 1440) return `${Math.floor(value / 60)} hours before`;
    return `${Math.floor(value / 1440)} days before`;
  };

  if (!hasDueDate) {
    return (
      <div className={`reminder-offset-selector ${className}`}>
        <label className="block text-sm font-medium text-gray-400 mb-1">
          {label}
        </label>
        <p className="text-sm text-gray-500 italic">
          Set a due date to enable reminders
        </p>
      </div>
    );
  }

  return (
    <div className={`reminder-offset-selector ${className}`}>
      <label htmlFor="reminder-offset" className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>

      <div className="space-y-2">
        <select
          id="reminder-offset"
          value={selectedPreset === null ? 'null' : selectedPreset}
          onChange={handlePresetChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {PRESET_OFFSETS.map((preset) => (
            <option
              key={preset.label}
              value={preset.value === null ? 'null' : preset.value}
            >
              {preset.label}
            </option>
          ))}
        </select>

        {showCustomInput && (
          <div className="flex items-center gap-2 p-3 bg-gray-50 border border-gray-200 rounded-md">
            <input
              type="number"
              min="1"
              max="10080" // 7 days in minutes
              value={customValue}
              onChange={handleCustomValueChange}
              placeholder="Enter value"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <select
              value={customUnit}
              onChange={handleCustomUnitChange}
              className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="minutes">minutes</option>
              <option value="hours">hours</option>
              <option value="days">days</option>
            </select>
            <span className="text-sm text-gray-600">before</span>
          </div>
        )}

        {value !== null && (
          <p className="text-xs text-gray-500">
            Reminder will be sent: {formatCurrentValue()}
          </p>
        )}
      </div>
    </div>
  );
};

export default ReminderOffsetSelector;
