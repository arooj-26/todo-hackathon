/**
 * RecurrencePatternForm component for configuring task recurrence patterns.
 *
 * Allows users to specify:
 * - Pattern type (daily, weekly, monthly)
 * - Interval (every N days/weeks/months)
 * - Days of week (for weekly pattern)
 * - Day of month (for monthly pattern)
 * - End condition (never, after N occurrences, by date)
 */

'use client';

import { useState } from 'react';
import type { RecurrencePattern, PatternType, EndCondition } from '../hooks/useTasks';

interface RecurrencePatternFormProps {
  value?: RecurrencePattern | null;
  onChange: (pattern: RecurrencePattern | null) => void;
  className?: string;
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Mon' },
  { value: 1, label: 'Tue' },
  { value: 2, label: 'Wed' },
  { value: 3, label: 'Thu' },
  { value: 4, label: 'Fri' },
  { value: 5, label: 'Sat' },
  { value: 6, label: 'Sun' },
];

export function RecurrencePatternForm({
  value,
  onChange,
  className = '',
}: RecurrencePatternFormProps) {
  const [enabled, setEnabled] = useState(!!value);
  const [patternType, setPatternType] = useState<PatternType>(value?.pattern_type ?? 'daily');
  const [interval, setInterval] = useState(value?.interval ?? 1);
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>(value?.days_of_week ?? []);
  const [dayOfMonth, setDayOfMonth] = useState(value?.day_of_month ?? 1);
  const [endCondition, setEndCondition] = useState<EndCondition>(value?.end_condition ?? 'never');
  const [occurrenceCount, setOccurrenceCount] = useState(value?.occurrence_count ?? 10);
  const [endDate, setEndDate] = useState(value?.end_date ?? '');

  const handleToggle = (checked: boolean) => {
    setEnabled(checked);
    if (!checked) {
      onChange(null);
    } else {
      updatePattern();
    }
  };

  const updatePattern = () => {
    if (!enabled) return;

    const pattern: RecurrencePattern = {
      pattern_type: patternType,
      interval,
      end_condition: endCondition,
    };

    // Add pattern-specific fields
    if (patternType === 'weekly') {
      pattern.days_of_week = daysOfWeek.length > 0 ? daysOfWeek : [new Date().getDay()];
    }

    if (patternType === 'monthly') {
      pattern.day_of_month = dayOfMonth;
    }

    // Add end condition fields
    if (endCondition === 'after_occurrences') {
      pattern.occurrence_count = occurrenceCount;
    } else if (endCondition === 'by_date') {
      pattern.end_date = endDate;
    }

    onChange(pattern);
  };

  const handlePatternTypeChange = (type: PatternType) => {
    setPatternType(type);
    setTimeout(updatePattern, 0);
  };

  const handleIntervalChange = (value: number) => {
    setInterval(value);
    setTimeout(updatePattern, 0);
  };

  const toggleDayOfWeek = (day: number) => {
    const newDays = daysOfWeek.includes(day)
      ? daysOfWeek.filter((d) => d !== day)
      : [...daysOfWeek, day].sort();
    setDaysOfWeek(newDays);
    setTimeout(updatePattern, 0);
  };

  const handleDayOfMonthChange = (value: number) => {
    setDayOfMonth(value);
    setTimeout(updatePattern, 0);
  };

  const handleEndConditionChange = (condition: EndCondition) => {
    setEndCondition(condition);
    setTimeout(updatePattern, 0);
  };

  const handleOccurrenceCountChange = (value: number) => {
    setOccurrenceCount(value);
    setTimeout(updatePattern, 0);
  };

  const handleEndDateChange = (value: string) => {
    setEndDate(value);
    setTimeout(updatePattern, 0);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Enable/Disable Toggle */}
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="recurrence-enabled"
          checked={enabled}
          onChange={(e) => handleToggle(e.target.checked)}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="recurrence-enabled" className="text-sm font-medium text-gray-700">
          Recurring Task
        </label>
      </div>

      {enabled && (
        <>
          {/* Pattern Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repeat Pattern
            </label>
            <select
              value={patternType}
              onChange={(e) => handlePatternTypeChange(e.target.value as PatternType)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          {/* Interval */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repeat Every
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="365"
                value={interval}
                onChange={(e) => handleIntervalChange(parseInt(e.target.value) || 1)}
                className="w-20 rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-600">
                {patternType === 'daily' && 'day(s)'}
                {patternType === 'weekly' && 'week(s)'}
                {patternType === 'monthly' && 'month(s)'}
              </span>
            </div>
          </div>

          {/* Days of Week (for weekly pattern) */}
          {patternType === 'weekly' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Repeat On
              </label>
              <div className="flex gap-2">
                {DAYS_OF_WEEK.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => toggleDayOfWeek(value)}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      daysOfWeek.includes(value)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Day of Month (for monthly pattern) */}
          {patternType === 'monthly' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Day of Month
              </label>
              <input
                type="number"
                min="1"
                max="31"
                value={dayOfMonth}
                onChange={(e) => handleDayOfMonthChange(parseInt(e.target.value) || 1)}
                className="w-24 rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          )}

          {/* End Condition */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Condition
            </label>
            <select
              value={endCondition}
              onChange={(e) => handleEndConditionChange(e.target.value as EndCondition)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="never">Never</option>
              <option value="after_occurrences">After N occurrences</option>
              <option value="by_date">By date</option>
            </select>
          </div>

          {/* Occurrence Count */}
          {endCondition === 'after_occurrences' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Number of Occurrences
              </label>
              <input
                type="number"
                min="1"
                max="365"
                value={occurrenceCount}
                onChange={(e) => handleOccurrenceCountChange(parseInt(e.target.value) || 1)}
                className="w-32 rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          )}

          {/* End Date */}
          {endCondition === 'by_date' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => handleEndDateChange(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}
