/**
 * Dashboard Component with ChatKit Integration
 *
 * Enhanced dashboard providing task management with ChatKit interface,
 * statistics, quick actions, and conversation management.
 */
'use client';

import React, { useState, useEffect } from 'react';
import ChatInterface from './ChatInterface';

interface DashboardProps {
  userId: string;
}

interface DashboardStats {
  totalTasks: number;
  completedTasks: number;
  pendingTasks: number;
  conversations: number;
}

export default function Dashboard({ userId }: DashboardProps) {
  const [showSidebar, setShowSidebar] = useState(true);
  const [stats, setStats] = useState<DashboardStats>({
    totalTasks: 0,
    completedTasks: 0,
    pendingTasks: 0,
    conversations: 0,
  });

  // Load stats from localStorage (in production, fetch from API)
  useEffect(() => {
    const savedStats = localStorage.getItem('dashboard_stats');
    if (savedStats) {
      try {
        setStats(JSON.parse(savedStats));
      } catch (e) {
        console.error('Failed to load stats:', e);
      }
    }
  }, []);

  const quickActions = [
    { label: 'Add Task', command: 'Add a new task' },
    { label: 'List Tasks', command: 'Show all my tasks' },
    { label: 'Mark Complete', command: 'Mark the first task as done' },
    { label: 'Delete Task', command: 'Delete the last task' },
  ];

  return (
    <div className="dashboard">
      {showSidebar && (
        <aside className="dashboard-sidebar">
          <div className="sidebar-header">
            <h2>Dashboard</h2>
            <button
              onClick={() => setShowSidebar(false)}
              className="close-sidebar-btn"
              title="Hide Sidebar"
            >
              ×
            </button>
          </div>

          {/* Statistics Panel */}
          <div className="stats-panel">
            <h3>Statistics</h3>
            <div className="stat-card">
              <div className="stat-value">{stats.totalTasks}</div>
              <div className="stat-label">Total Tasks</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.completedTasks}</div>
              <div className="stat-label">Completed</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.pendingTasks}</div>
              <div className="stat-label">Pending</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{stats.conversations}</div>
              <div className="stat-label">Conversations</div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="quick-actions">
            <h3>Quick Actions</h3>
            <div className="action-buttons">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  className="action-btn"
                  onClick={() => {
                    // Simulate clicking the chat input with the command
                    const event = new CustomEvent('chatCommand', {
                      detail: { command: action.command }
                    });
                    window.dispatchEvent(event);
                  }}
                >
                  {action.label}
                </button>
              ))}
            </div>
          </div>

          {/* Help Section */}
          <div className="help-section">
            <h3>Need Help?</h3>
            <p>Try asking me:</p>
            <ul>
              <li>"Add buy groceries"</li>
              <li>"Show my tasks"</li>
              <li>"Mark first task done"</li>
              <li>"Delete last task"</li>
            </ul>
          </div>
        </aside>
      )}

      <main className="dashboard-main">
        {!showSidebar && (
          <button
            onClick={() => setShowSidebar(true)}
            className="show-sidebar-btn"
            title="Show Sidebar"
          >
            ☰
          </button>
        )}

        <ChatInterface userId={userId} />
      </main>

      <style jsx>{`
        .dashboard {
          display: flex;
          height: 100vh;
          background: #f5f5f5;
        }

        .dashboard-sidebar {
          width: 300px;
          background: white;
          border-right: 1px solid #e0e0e0;
          padding: 1.5rem;
          overflow-y: auto;
          box-shadow: 2px 0 8px rgba(0,0,0,0.05);
        }

        .sidebar-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid #667eea;
        }

        .sidebar-header h2 {
          margin: 0;
          color: #333;
          font-size: 1.5rem;
        }

        .close-sidebar-btn {
          background: none;
          border: none;
          font-size: 2rem;
          color: #666;
          cursor: pointer;
          padding: 0;
          line-height: 1;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 4px;
          transition: all 0.2s;
        }

        .close-sidebar-btn:hover {
          background: #f0f0f0;
          color: #333;
        }

        .stats-panel {
          margin-bottom: 2rem;
        }

        .stats-panel h3 {
          margin: 0 0 1rem 0;
          color: #666;
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .stat-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 0.75rem;
          text-align: center;
        }

        .stat-value {
          font-size: 2rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
        }

        .stat-label {
          font-size: 0.875rem;
          opacity: 0.9;
        }

        .quick-actions {
          margin-bottom: 2rem;
        }

        .quick-actions h3 {
          margin: 0 0 1rem 0;
          color: #666;
          font-size: 0.875rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .action-buttons {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 0.75rem;
        }

        .action-btn {
          background: white;
          border: 2px solid #667eea;
          color: #667eea;
          padding: 0.75rem;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
          font-size: 0.875rem;
          transition: all 0.2s;
        }

        .action-btn:hover {
          background: #667eea;
          color: white;
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
        }

        .help-section {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
        }

        .help-section h3 {
          margin: 0 0 0.5rem 0;
          color: #333;
          font-size: 1rem;
        }

        .help-section p {
          margin: 0 0 0.5rem 0;
          color: #666;
          font-size: 0.875rem;
        }

        .help-section ul {
          margin: 0;
          padding-left: 1.25rem;
          color: #667eea;
          font-size: 0.875rem;
        }

        .help-section li {
          margin: 0.25rem 0;
        }

        .dashboard-main {
          flex: 1;
          position: relative;
          overflow: hidden;
        }

        .show-sidebar-btn {
          position: absolute;
          top: 1rem;
          left: 1rem;
          z-index: 100;
          background: white;
          border: 1px solid #ddd;
          padding: 0.5rem 0.75rem;
          border-radius: 6px;
          cursor: pointer;
          font-size: 1.25rem;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: all 0.2s;
        }

        .show-sidebar-btn:hover {
          background: #f8f9fa;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        @media (max-width: 768px) {
          .dashboard-sidebar {
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            z-index: 1000;
          }
        }
      `}</style>
    </div>
  );
}
