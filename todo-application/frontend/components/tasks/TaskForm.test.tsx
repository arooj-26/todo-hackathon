/**
 * TaskForm component tests
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import TaskForm from './TaskForm'

describe('TaskForm', () => {
  const mockOnSubmit = jest.fn(() => Promise.resolve())

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders task input field and submit button', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />)

    expect(screen.getByLabelText('New Task')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('What do you need to do?')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add task/i })).toBeInTheDocument()
  })

  it('updates input value when typing', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />)

    const input = screen.getByPlaceholderText('What do you need to do?') as HTMLInputElement
    fireEvent.change(input, { target: { value: 'New task' } })

    expect(input.value).toBe('New task')
  })

  it('calls onSubmit with trimmed description when form is submitted', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />)

    const input = screen.getByPlaceholderText('What do you need to do?')
    const button = screen.getByRole('button', { name: /add task/i })

    fireEvent.change(input, { target: { value: '  New task  ' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('New task')
    })
  })

  it('clears input after successful submission', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />)

    const input = screen.getByPlaceholderText('What do you need to do?') as HTMLInputElement
    const button = screen.getByRole('button', { name: /add task/i })

    fireEvent.change(input, { target: { value: 'New task' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(input.value).toBe('')
    })
  })

  it('shows error when submitting empty description', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />)

    const button = screen.getByRole('button', { name: /add task/i })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Please enter a task description')).toBeInTheDocument()
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  it('shows error when description exceeds 1000 characters', async () => {
    render(<TaskForm onSubmit={mockOnSubmit} />)

    const input = screen.getByPlaceholderText('What do you need to do?')
    const button = screen.getByRole('button', { name: /add task/i })

    const longDescription = 'a'.repeat(1001)
    fireEvent.change(input, { target: { value: longDescription } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Task description must be less than 1000 characters')).toBeInTheDocument()
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })



  it('disables form when isLoading is true', () => {
    render(<TaskForm onSubmit={mockOnSubmit} isLoading={true} />)

    const input = screen.getByPlaceholderText('What do you need to do?') as HTMLInputElement
    const button = screen.getByRole('button', { name: /adding/i }) as HTMLButtonElement

    expect(input).toBeDisabled()
    expect(button).toBeDisabled()
  })

  it('shows loading state text when submitting', () => {
    render(<TaskForm onSubmit={mockOnSubmit} isLoading={true} />)

    expect(screen.getByText('Adding...')).toBeInTheDocument()
  })

  it('handles submission error and displays error message', async () => {
    const mockErrorOnSubmit = jest.fn(() =>
      Promise.reject({
        response: {
          data: { detail: 'Server error' }
        }
      })
    )

    render(<TaskForm onSubmit={mockErrorOnSubmit} />)

    const input = screen.getByPlaceholderText('What do you need to do?')
    const button = screen.getByRole('button', { name: /add task/i })

    fireEvent.change(input, { target: { value: 'New task' } })
    fireEvent.click(button)

    await waitFor(() => {
      expect(screen.getByText('Server error')).toBeInTheDocument()
    })
  })

  it('enforces maxLength of 1000 characters on input', () => {
    render(<TaskForm onSubmit={mockOnSubmit} />)

    const input = screen.getByPlaceholderText('What do you need to do?') as HTMLInputElement
    expect(input).toHaveAttribute('maxLength', '1000')
  })
})
