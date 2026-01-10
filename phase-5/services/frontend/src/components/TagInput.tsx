/**
 * TagInput component with autocomplete for task tagging.
 *
 * Provides autocomplete suggestions ranked by usage count and allows
 * adding multiple tags to a task.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useTags } from '../hooks/useTags';

interface TagInputProps {
  /** Current tag names */
  value: string[];
  /** Callback when tags change */
  onChange: (tags: string[]) => void;
  /** Label for the input */
  label?: string;
  /** Placeholder text */
  placeholder?: string;
  /** Additional CSS classes */
  className?: string;
  /** Maximum number of tags allowed */
  maxTags?: number;
}

export const TagInput: React.FC<TagInputProps> = ({
  value,
  onChange,
  label = 'Tags',
  placeholder = 'Type to search tags...',
  className = '',
  maxTags = 10,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Fetch tags with autocomplete search
  const { tags, isLoading } = useTags({
    search: inputValue.trim(),
    limit: 20,
  });

  // Filter out already selected tags
  const availableTags = tags.filter(
    (tag) => !value.includes(tag.name) && tag.name.toLowerCase().includes(inputValue.toLowerCase())
  );

  useEffect(() => {
    // Reset selected index when suggestions change
    setSelectedIndex(-1);
  }, [availableTags.length]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setShowSuggestions(newValue.trim().length > 0);
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();

      if (selectedIndex >= 0 && selectedIndex < availableTags.length) {
        // Add selected suggestion
        addTag(availableTags[selectedIndex].name);
      } else if (inputValue.trim()) {
        // Add new tag from input
        addTag(inputValue.trim());
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, availableTags.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, -1));
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    } else if (e.key === 'Backspace' && inputValue === '' && value.length > 0) {
      // Remove last tag if input is empty
      removeTag(value[value.length - 1]);
    }
  };

  const addTag = (tagName: string) => {
    // Validate tag name (lowercase, alphanumeric, hyphens only)
    const normalizedTag = tagName.toLowerCase().replace(/[^a-z0-9-]/g, '-');

    if (!normalizedTag) {
      return;
    }

    if (value.includes(normalizedTag)) {
      // Tag already added
      setInputValue('');
      setShowSuggestions(false);
      return;
    }

    if (value.length >= maxTags) {
      // Max tags reached
      alert(`Maximum ${maxTags} tags allowed`);
      return;
    }

    onChange([...value, normalizedTag]);
    setInputValue('');
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const removeTag = (tagToRemove: string) => {
    onChange(value.filter((tag) => tag !== tagToRemove));
  };

  const handleSuggestionClick = (tagName: string) => {
    addTag(tagName);
    inputRef.current?.focus();
  };

  const handleInputBlur = () => {
    // Delay to allow click on suggestions
    setTimeout(() => {
      setShowSuggestions(false);
    }, 200);
  };

  const handleInputFocus = () => {
    if (inputValue.trim().length > 0) {
      setShowSuggestions(true);
    }
  };

  return (
    <div className={`tag-input ${className}`}>
      <label htmlFor="tag-input" className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>

      <div className="relative">
        {/* Tag pills and input */}
        <div className="flex flex-wrap items-center gap-2 p-2 border border-gray-300 rounded-md bg-white min-h-[42px] focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
          {value.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded-md border border-blue-200"
            >
              {tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="hover:text-blue-600 focus:outline-none"
                aria-label={`Remove tag ${tag}`}
              >
                <svg
                  className="w-3 h-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </span>
          ))}

          <input
            ref={inputRef}
            id="tag-input"
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleInputKeyDown}
            onBlur={handleInputBlur}
            onFocus={handleInputFocus}
            placeholder={value.length === 0 ? placeholder : ''}
            className="flex-1 min-w-[120px] outline-none border-none focus:ring-0 text-sm"
            disabled={value.length >= maxTags}
          />
        </div>

        {/* Autocomplete suggestions */}
        {showSuggestions && availableTags.length > 0 && (
          <div
            ref={suggestionsRef}
            className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto"
          >
            {availableTags.map((tag, index) => (
              <div
                key={tag.id}
                onClick={() => handleSuggestionClick(tag.name)}
                className={`px-3 py-2 cursor-pointer hover:bg-blue-50 flex items-center justify-between ${
                  index === selectedIndex ? 'bg-blue-100' : ''
                }`}
              >
                <span className="text-sm">{tag.name}</span>
                <span className="text-xs text-gray-500">{tag.usage_count} uses</span>
              </div>
            ))}
          </div>
        )}

        {/* Loading indicator */}
        {isLoading && inputValue.trim().length > 0 && (
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Help text */}
      <p className="mt-1 text-xs text-gray-500">
        {value.length}/{maxTags} tags. Press Enter to add, Backspace to remove.
      </p>
    </div>
  );
};

export default TagInput;
