/**
 * TaskItem component tests
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import TaskItem from './TaskItem'
import { Task } from '@/types/task'

describe('TaskItem', () => {
  const mockTask: Task = {
    id: 1,
    user_id: 1,
    description: 'Test task',
    completed: false,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  }

  const mockOnToggle = jest.fn(() => Promise.resolve())
  const mockOnDelete = jest.fn(() => Promise.resolve())
  const mockOnEdit = jest.fn(() => Promise.resolve())

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders task description', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    expect(screen.getByText('Test task')).toBeInTheDocument()
  })

  it('renders completion checkbox with correct state', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const checkbox = screen.getByRole('checkbox') as HTMLInputElement
    expect(checkbox.checked).toBe(false)
  })

  it('calls onToggle when checkbox is clicked', async () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)

    await waitFor(() => {
      expect(mockOnToggle).toHaveBeenCalledWith(1)
    })

    await waitFor(() => {
      expect(checkbox).not.toBeDisabled()
    })
  })

  it('calls onDelete when delete button is clicked and confirmed', async () => {
    // Mock window.confirm
    global.confirm = jest.fn(() => true)

    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(global.confirm).toHaveBeenCalled()
      expect(mockOnDelete).toHaveBeenCalledWith(1)
    })
  })

  it('does not call onDelete when delete is cancelled', async () => {
    // Mock window.confirm to return false
    global.confirm = jest.fn(() => false)

    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(global.confirm).toHaveBeenCalled()
      expect(mockOnDelete).not.toHaveBeenCalled()
    })
  })

  it('enters edit mode when edit button is clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const editButton = screen.getByText('Edit')
    fireEvent.click(editButton)

    expect(screen.getByDisplayValue('Test task')).toBeInTheDocument()
    expect(screen.getByText('Save')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  it('calls onEdit when saving edited task', async () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    // Enter edit mode
    const editButton = screen.getByText('Edit')
    fireEvent.click(editButton)

    // Edit the description
    const input = screen.getByDisplayValue('Test task') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'Updated task' } })

    // Save
    const saveButton = screen.getByText('Save')
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(mockOnEdit).toHaveBeenCalledWith(1, 'Updated task')
    })
  })

  it('cancels edit mode when cancel button is clicked', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    // Enter edit mode
    const editButton = screen.getByText('Edit')
    fireEvent.click(editButton)

    // Edit the description
    const input = screen.getByDisplayValue('Test task') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'Updated task' } })

    // Cancel
    const cancelButton = screen.getByText('Cancel')
    fireEvent.click(cancelButton)

    // Should exit edit mode and not save changes
    expect(screen.queryByDisplayValue('Updated task')).not.toBeInTheDocument()
    expect(screen.getByText('Test task')).toBeInTheDocument()
    expect(mockOnEdit).not.toHaveBeenCalled()
  })

  it('applies line-through style to completed tasks', () => {
    const completedTask = { ...mockTask, completed: true }

    render(
      <TaskItem
        task={completedTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const taskText = screen.getByText('Test task')
    expect(taskText).toHaveClass('line-through')
    expect(taskText).toHaveClass('text-gray-500')
  })

  it('renders view link with correct href', () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const viewLink = screen.getByText('View')
    expect(viewLink).toHaveAttribute('href', '/tasks/1')
  })

  it('disables actions when loading', async () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={mockOnToggle}
        onDelete={mockOnDelete}
        onEdit={mockOnEdit}
      />
    )

    const checkbox = screen.getByRole('checkbox')
    fireEvent.click(checkbox)

    // Buttons should be disabled during loading
    await waitFor(() => {
      const editButton = screen.getByText('Edit')
      const deleteButton = screen.getByText('Delete')
      expect(checkbox).toBeDisabled()
      expect(editButton).toBeDisabled()
      expect(deleteButton).toBeDisabled()
    })

    await waitFor(() => {
      expect(checkbox).not.toBeDisabled()
    })
  })
})
