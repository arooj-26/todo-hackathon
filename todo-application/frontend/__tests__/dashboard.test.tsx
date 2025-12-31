/**
 * Tests for TodoFlowDashboard component with new features
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import TodoFlowDashboard from '@/components/dashboard/TodoFlowDashboard';
import { Task, Priority, Recurrence } from '@/types/task';

// Mock the API functions
vi.mock('@/lib/api/tasks', () => ({
  getTasks: vi.fn(),
  createTask: vi.fn(),
  toggleTaskCompletion: vi.fn(),
  deleteTask: vi.fn(),
  updateTask: vi.fn(),
}));

// Mock other dependencies
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
  })),
}));

vi.mock('@/components/auth/AuthProvider', () => ({
  useAuthContext: vi.fn(() => ({
    user: { id: 1, email: 'test@example.com' },
    isLoading: false,
    isAuthenticated: true,
    signOut: vi.fn(),
  })),
}));

vi.mock('framer-motion', async () => {
  const actual = await vi.importActual('framer-motion');
  return {
    ...actual,
    motion: ({ children }: { children: React.ReactNode }) => children,
    AnimatePresence: ({ children }: { children: React.ReactNode }) => children,
  };
});

// Mock shadcn/ui components
vi.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props}>
      {children}
    </button>
  ),
}));

vi.mock('@/components/ui/input', () => ({
  Input: ({ value, onChange, ...props }: any) => (
    <input value={value} onChange={onChange} {...props} />
  ),
}));

vi.mock('@/components/ui/select', () => ({
  Select: ({ children, value, onValueChange }: any) => (
    <select value={value} onChange={(e) => onValueChange(e.target.value)}>
      {children}
    </select>
  ),
  SelectContent: ({ children }: any) => <div>{children}</div>,
  SelectItem: ({ children, value }: any) => <option value={value}>{children}</option>,
  SelectTrigger: ({ children }: any) => <div>{children}</div>,
  SelectValue: () => <div>Select Value</div>,
}));

vi.mock('@/components/ui/checkbox', () => ({
  Checkbox: ({ checked, onCheckedChange, ...props }: any) => (
    <input
      type="checkbox"
      checked={checked}
      onChange={(e) => onCheckedChange(e.target.checked)}
      {...props}
    />
  ),
}));

vi.mock('@/components/ui/dialog', () => ({
  Dialog: ({ children, open, onOpenChange }: any) => (
    <div data-testid="dialog" style={{ display: open ? 'block' : 'none' }}>
      {children}
    </div>
  ),
  DialogContent: ({ children }: any) => <div>{children}</div>,
  DialogHeader: ({ children }: any) => <div>{children}</div>,
  DialogTitle: ({ children }: any) => <div>{children}</div>,
  DialogFooter: ({ children }: any) => <div>{children}</div>,
}));

vi.mock('@/components/ui/badge', () => ({
  Badge: ({ children, className }: any) => <span className={className}>{children}</span>,
}));

vi.mock('@/components/ui/card', () => ({
  Card: ({ children }: any) => <div>{children}</div>,
  CardContent: ({ children }: any) => <div>{children}</div>,
  CardHeader: ({ children }: any) => <div>{children}</div>,
  CardTitle: ({ children }: any) => <div>{children}</div>,
}));

vi.mock('@/components/chatbot/FloatingChatWidget', () => ({
  default: () => <div>Chat Widget</div>,
}));

vi.mock('sonner', () => ({
  toast: { success: vi.fn(), error: vi.fn() },
  Toaster: () => <div />,
}));

describe('TodoFlowDashboard', () => {
  const mockUser = { id: 1, email: 'test@example.com' };
  const mockSignOut = vi.fn();

  const mockTasks: Task[] = [
    {
      id: 1,
      user_id: 1,
      description: 'Test task 1',
      completed: false,
      priority: 'medium',
      due_date: '2025-01-01T12:00:00Z',
      recurrence: 'weekly',
      created_at: '2024-12-26T10:00:00Z',
      updated_at: '2024-12-26T10:00:00Z',
    },
    {
      id: 2,
      user_id: 1,
      description: 'Test task 2',
      completed: true,
      priority: 'high',
      due_date: null,
      recurrence: null,
      created_at: '2024-12-26T11:00:00Z',
      updated_at: '2024-12-26T11:00:00Z',
    },
    {
      id: 3,
      user_id: 1,
      description: 'Another task',
      completed: false,
      priority: 'low',
      due_date: '2024-12-30T12:00:00Z',
      recurrence: 'daily',
      created_at: '2024-12-26T12:00:00Z',
      updated_at: '2024-12-26T12:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard with new features', async () => {
    const { getTasks } = await import('@/lib/api/tasks');
    (getTasks as vi.MockedFunction<any>).mockResolvedValue(mockTasks);

    render(
      <TodoFlowDashboard user={mockUser} onSignOut={mockSignOut} />
    );

    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument();
    });

    // Check that new features are present
    expect(screen.getByPlaceholderText('Search tasks...')).toBeInTheDocument();
    expect(screen.getByText('Filter:')).toBeInTheDocument();
    expect(screen.getByText('Sort by:')).toBeInTheDocument();
    expect(screen.getByText('Order:')).toBeInTheDocument();

    // Check that tasks with due dates and recurrence are displayed
    expect(screen.getByText('1/1/2025')).toBeInTheDocument(); // due date
    expect(screen.getByText('weekly')).toBeInTheDocument(); // recurrence
    expect(screen.getByText('daily')).toBeInTheDocument(); // recurrence
  });

  it('filters tasks by status', async () => {
    const { getTasks } = await import('@/lib/api/tasks');
    (getTasks as vi.MockedFunction<any>).mockResolvedValue(mockTasks);

    render(
      <TodoFlowDashboard user={mockUser} onSignOut={mockSignOut} />
    );

    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument();
    });

    // Filter by completed
    const filterSelect = screen.getByText('Filter:').closest('select') as HTMLSelectElement;
    fireEvent.change(filterSelect, { target: { value: 'completed' } });

    // Should only show completed task
    expect(screen.getByText('Test task 2')).toBeInTheDocument();
    expect(screen.queryByText('Test task 1')).not.toBeInTheDocument();
    expect(screen.queryByText('Another task')).not.toBeInTheDocument();

    // Filter by pending
    fireEvent.change(filterSelect, { target: { value: 'pending' } });

    // Should show pending tasks
    expect(screen.getByText('Test task 1')).toBeInTheDocument();
    expect(screen.getByText('Another task')).toBeInTheDocument();
    expect(screen.queryByText('Test task 2')).not.toBeInTheDocument();

    // Filter by overdue
    fireEvent.change(filterSelect, { target: { value: 'overdue' } });

    // Should show overdue task (task 3 with due date in past)
    expect(screen.getByText('Another task')).toBeInTheDocument();
    expect(screen.queryByText('Test task 1')).not.toBeInTheDocument();
    expect(screen.queryByText('Test task 2')).not.toBeInTheDocument();
  });

  it('sorts tasks by date', async () => {
    const { getTasks } = await import('@/lib/api/tasks');
    (getTasks as vi.MockedFunction<any>).mockResolvedValue(mockTasks);

    render(
      <TodoFlowDashboard user={mockUser} onSignOut={mockSignOut} />
    );

    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument();
    });

    // Sort by due date
    const sortSelect = screen.getByText('Sort by:').closest('select') as HTMLSelectElement;
    fireEvent.change(sortSelect, { target: { value: 'date' } });

    // Order should be by due date (task 3 first, then task 1)
    const taskElements = screen.getAllByText(/Test task|Another task/);
    expect(taskElements[0]).toHaveTextContent('Another task'); // due date: 2024-12-30
    expect(taskElements[1]).toHaveTextContent('Test task 1'); // due date: 2025-01-01
  });

  it('searches tasks', async () => {
    const { getTasks } = await import('@/lib/api/tasks');
    (getTasks as vi.MockedFunction<any>).mockResolvedValue(mockTasks);

    render(
      <TodoFlowDashboard user={mockUser} onSignOut={mockSignOut} />
    );

    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument();
    });

    // Search for "Another"
    const searchInput = screen.getByPlaceholderText('Search tasks...');
    fireEvent.change(searchInput, { target: { value: 'Another' } });

    // Should only show "Another task"
    expect(screen.getByText('Another task')).toBeInTheDocument();
    expect(screen.queryByText('Test task 1')).not.toBeInTheDocument();
    expect(screen.queryByText('Test task 2')).not.toBeInTheDocument();
  });

  it('adds a task with due date and recurrence', async () => {
    const { getTasks, createTask } = await import('@/lib/api/tasks');
    (getTasks as vi.MockedFunction<any>).mockResolvedValue(mockTasks);
    (createTask as vi.MockedFunction<any>).mockResolvedValue({
      id: 4,
      user_id: 1,
      description: 'New task',
      completed: false,
      priority: 'medium',
      due_date: '2025-01-10T12:00:00Z',
      recurrence: 'monthly',
      created_at: '2024-12-26T13:00:00Z',
      updated_at: '2024-12-26T13:00:00Z',
    });

    render(
      <TodoFlowDashboard user={mockUser} onSignOut={mockSignOut} />
    );

    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument();
    });

    // Open add task dialog
    const addTaskButton = screen.getByText('Add Task');
    fireEvent.click(addTaskButton);

    // Fill in the form
    const descriptionInput = screen.getByPlaceholderText('What needs to be done?');
    fireEvent.change(descriptionInput, { target: { value: 'New task' } });

    const dueDateInput = screen.getByLabelText('Due Date (Optional)');
    fireEvent.change(dueDateInput, { target: { value: '2025-01-10' } });

    const recurrenceSelect = screen.getByLabelText('Recurrence (Optional)').closest('select') as HTMLSelectElement;
    fireEvent.change(recurrenceSelect, { target: { value: 'monthly' } });

    // Submit the form
    const createButton = screen.getByText('Create');
    fireEvent.click(createButton);

    // Check that createTask was called with the correct parameters
    await waitFor(() => {
      expect(createTask).toHaveBeenCalledWith(1, {
        description: 'New task',
        priority: 'medium',
        due_date: '2025-01-10T00:00:00.000Z',
        recurrence: 'monthly',
      });
    });
  });

  it('updates a task with due date and recurrence', async () => {
    const { getTasks, updateTask } = await import('@/lib/api/tasks');
    (getTasks as vi.MockedFunction<any>).mockResolvedValue(mockTasks);
    (updateTask as vi.MockedFunction<any>).mockResolvedValue({
      id: 1,
      user_id: 1,
      description: 'Updated task',
      completed: false,
      priority: 'high',
      due_date: '2025-01-15T12:00:00Z',
      recurrence: 'daily',
      created_at: '2024-12-26T10:00:00Z',
      updated_at: '2024-12-26T14:00:00Z',
    });

    render(
      <TodoFlowDashboard user={mockUser} onSignOut={mockSignOut} />
    );

    await waitFor(() => {
      expect(screen.getByText('Test task 1')).toBeInTheDocument();
    });

    // Click edit button for first task
    const editButton = screen.getAllByLabelText('Pencil')[0];
    fireEvent.click(editButton);

    // Update the form
    const descriptionInput = screen.getByPlaceholderText('What needs to be done?');
    fireEvent.change(descriptionInput, { target: { value: 'Updated task' } });

    const prioritySelect = screen.getByRole('combobox');
    fireEvent.change(prioritySelect, { target: { value: 'high' } });

    const dueDateInput = screen.getByLabelText('Due Date (Optional)');
    fireEvent.change(dueDateInput, { target: { value: '2025-01-15' } });

    const recurrenceSelect = screen.getByLabelText('Recurrence (Optional)').closest('select') as HTMLSelectElement;
    fireEvent.change(recurrenceSelect, { target: { value: 'daily' } });

    // Submit the form
    const updateButton = screen.getByText('Update');
    fireEvent.click(updateButton);

    // Check that updateTask was called with the correct parameters
    await waitFor(() => {
      expect(updateTask).toHaveBeenCalledWith(1, 1, {
        description: 'Updated task',
        priority: 'high',
        due_date: '2025-01-15T00:00:00.000Z',
        recurrence: 'daily',
      });
    });
  });
});