/**
 * NotificationBanner component for displaying in-app notifications.
 *
 * Shows task reminders, system notifications, and user alerts.
 * Supports auto-dismiss and manual dismissal.
 */

'use client';

import React, { useEffect, useState } from 'react';

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'reminder';
  title: string;
  message: string;
  taskId?: number;
  autoDismiss?: boolean;
  duration?: number; // milliseconds
  createdAt: Date;
}

interface NotificationBannerProps {
  /** Array of notifications to display */
  notifications: Notification[];
  /** Callback when notification is dismissed */
  onDismiss: (id: string) => void;
  /** Maximum number of notifications to show at once */
  maxVisible?: number;
  /** Position of the banner */
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export const NotificationBanner: React.FC<NotificationBannerProps> = ({
  notifications,
  onDismiss,
  maxVisible = 5,
  position = 'top-right',
}) => {
  const [visibleNotifications, setVisibleNotifications] = useState<Notification[]>([]);

  // Update visible notifications when prop changes
  useEffect(() => {
    setVisibleNotifications(notifications.slice(0, maxVisible));
  }, [notifications, maxVisible]);

  // Auto-dismiss notifications
  useEffect(() => {
    const timers: NodeJS.Timeout[] = [];

    visibleNotifications.forEach((notification) => {
      if (notification.autoDismiss !== false) {
        const duration = notification.duration || 5000; // Default 5 seconds
        const timer = setTimeout(() => {
          onDismiss(notification.id);
        }, duration);
        timers.push(timer);
      }
    });

    return () => {
      timers.forEach((timer) => clearTimeout(timer));
    };
  }, [visibleNotifications, onDismiss]);

  // Get icon for notification type
  const getIcon = (type: Notification['type']): string => {
    switch (type) {
      case 'info':
        return 'ℹ️';
      case 'success':
        return '✅';
      case 'warning':
        return '⚠️';
      case 'error':
        return '❌';
      case 'reminder':
        return '🔔';
      default:
        return 'ℹ️';
    }
  };

  // Get color classes for notification type
  const getColorClasses = (type: Notification['type']): string => {
    switch (type) {
      case 'info':
        return 'bg-blue-50 border-blue-500 text-blue-900';
      case 'success':
        return 'bg-green-50 border-green-500 text-green-900';
      case 'warning':
        return 'bg-yellow-50 border-yellow-500 text-yellow-900';
      case 'error':
        return 'bg-red-50 border-red-500 text-red-900';
      case 'reminder':
        return 'bg-purple-50 border-purple-500 text-purple-900';
      default:
        return 'bg-gray-50 border-gray-500 text-gray-900';
    }
  };

  // Get position classes
  const getPositionClasses = (): string => {
    switch (position) {
      case 'top-right':
        return 'top-4 right-4';
      case 'top-left':
        return 'top-4 left-4';
      case 'bottom-right':
        return 'bottom-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      default:
        return 'top-4 right-4';
    }
  };

  if (visibleNotifications.length === 0) {
    return null;
  }

  return (
    <div className={`fixed ${getPositionClasses()} z-50 space-y-2 w-96 max-w-full`}>
      {visibleNotifications.map((notification) => (
        <div
          key={notification.id}
          className={`
            border-l-4 rounded-lg shadow-lg p-4
            ${getColorClasses(notification.type)}
            animate-slide-in-right
          `}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 flex-1">
              <span className="text-2xl flex-shrink-0">{getIcon(notification.type)}</span>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm mb-1">{notification.title}</p>
                <p className="text-sm opacity-90 break-words">{notification.message}</p>
                {notification.taskId && (
                  <a
                    href={`/tasks/${notification.taskId}`}
                    className="text-xs underline mt-1 inline-block hover:opacity-75"
                  >
                    View Task →
                  </a>
                )}
              </div>
            </div>
            <button
              onClick={() => onDismiss(notification.id)}
              className="text-gray-500 hover:text-gray-700 flex-shrink-0"
              aria-label="Dismiss notification"
            >
              <svg
                className="w-5 h-5"
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
          </div>
        </div>
      ))}
    </div>
  );
};

export default NotificationBanner;
