# Frontend Development Guide

This file contains frontend-specific guidance for the Todo Application built with Next.js and React.

## Technology Stack

- **Framework**: Next.js 15+ (App Router)
- **Language**: TypeScript
- **UI Library**: React 19+
- **Authentication**: Better Auth (JWT-based)
- **Styling**: TailwindCSS 3.4+
- **HTTP Client**: Axios
- **Testing**: Jest + React Testing Library
- **Form Validation**: Better Auth built-in validation

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Home page (landing or redirect)
│   ├── auth/
│   │   ├── signin/
│   │   │   └── page.tsx    # Sign-in page
│   │   └── signup/
│   │       └── page.tsx    # Sign-up page
│   ├── dashboard/
│   │   └── page.tsx        # Main dashboard with task list
│   └── api/
│       └── auth/
│           └── [...better-auth]/route.ts  # Better Auth API route
├── components/
│   ├── auth/
│   │   ├── SignInForm.tsx   # Sign-in form component
│   │   ├── SignUpForm.tsx   # Sign-up form component
│   │   └── AuthGuard.tsx    # Protected route wrapper
│   ├── tasks/
│   │   ├── TaskList.tsx     # Task list display
│   │   ├── TaskItem.tsx     # Individual task item
│   │   ├── TaskForm.tsx     # Task creation form
│   │   └── TaskEditForm.tsx # Task edit form
│   ├── layout/
│   │   ├── Header.tsx       # App header with user info
│   │   └── Navbar.tsx       # Navigation bar
│   └── ui/
│       ├── Button.tsx       # Reusable button component
│       ├── Input.tsx        # Reusable input component
│       └── Modal.tsx        # Reusable modal component
├── lib/
│   ├── api/
│   │   ├── client.ts        # Axios instance with interceptors
│   │   ├── auth.ts          # Auth API calls
│   │   └── tasks.ts         # Task API calls
│   ├── auth/
│   │   ├── better-auth.ts   # Better Auth configuration
│   │   └── session.ts       # Session management utilities
│   └── utils/
│       ├── validators.ts    # Input validation functions
│       └── formatters.ts    # Date/text formatting
├── types/
│   ├── auth.ts              # Auth-related types
│   ├── task.ts              # Task-related types
│   └── api.ts               # API response types
├── hooks/
│   ├── useAuth.ts           # Authentication hook
│   ├── useTasks.ts          # Task management hook
│   └── useDebounce.ts       # Debounce utility hook
├── middleware.ts            # Next.js middleware for auth
├── tailwind.config.ts       # TailwindCSS configuration
├── next.config.js           # Next.js configuration
├── jest.config.js           # Jest configuration
├── package.json
├── tsconfig.json
├── .env.example
├── .gitignore
└── CLAUDE.md               # This file
```

## Next.js App Router Patterns

### Root Layout (app/layout.tsx)

```tsx
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Todo App',
  description: 'Full-stack todo application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
```

### Server Component (app/dashboard/page.tsx)

```tsx
import { redirect } from 'next/navigation'
import { auth } from '@/lib/auth/better-auth'
import TaskList from '@/components/tasks/TaskList'

export default async function DashboardPage() {
  const session = await auth()

  if (!session) {
    redirect('/auth/signin')
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Tasks</h1>
      <TaskList userId={session.user.id} />
    </main>
  )
}
```

### Client Component (components/tasks/TaskForm.tsx)

```tsx
'use client'

import { useState } from 'react'
import { createTask } from '@/lib/api/tasks'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

interface TaskFormProps {
  userId: number
  onTaskCreated: () => void
}

export default function TaskForm({ userId, onTaskCreated }: TaskFormProps) {
  const [description, setDescription] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      await createTask(userId, { description })
      setDescription('')
      onTaskCreated()
    } catch (err) {
      setError('Failed to create task')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Enter task description"
        required
        minLength={1}
        maxLength={1000}
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <Button type="submit" disabled={isLoading || !description.trim()}>
        {isLoading ? 'Creating...' : 'Create Task'}
      </Button>
    </form>
  )
}
```

## Better Auth Integration

### Configuration (lib/auth/better-auth.ts)

```typescript
import { betterAuth } from "better-auth"

export const auth = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_APP_URL,
  secret: process.env.BETTER_AUTH_SECRET,
  database: {
    // Better Auth uses its own storage
    provider: "memory", // Or use database adapter
  },
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
  },
  session: {
    expiresIn: 60 * 60 * 24, // 24 hours
    updateAge: 60 * 60 * 24, // 24 hours
  },
})

export type Session = typeof auth.$Infer.Session
```

### API Route (app/api/auth/[...better-auth]/route.ts)

```typescript
import { auth } from "@/lib/auth/better-auth"

export const { GET, POST } = auth.handler
```

### Authentication Hook (hooks/useAuth.ts)

```typescript
'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { signIn, signUp, signOut, getSession } from '@/lib/api/auth'

export interface User {
  id: number
  email: string
}

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const session = await getSession()
      setUser(session.user)
    } catch {
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await signIn(email, password)
    setUser(response.user)
    router.push('/dashboard')
  }

  const register = async (email: string, password: string) => {
    const response = await signUp(email, password)
    setUser(response.user)
    router.push('/dashboard')
  }

  const logout = async () => {
    await signOut()
    setUser(null)
    router.push('/auth/signin')
  }

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  }
}
```

### Auth Guard Component (components/auth/AuthGuard.tsx)

```tsx
'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/auth/signin')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
```

## API Client Patterns

### Axios Configuration (lib/api/client.ts)

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token')
      window.location.href = '/auth/signin'
    }
    return Promise.reject(error)
  }
)

export default api
```

### API Calls (lib/api/tasks.ts)

```typescript
import api from './client'
import { Task, TaskCreate, TaskUpdate } from '@/types/task'

export async function getTasks(userId: number): Promise<Task[]> {
  const response = await api.get(`/api/${userId}/tasks`)
  return response.data
}

export async function createTask(userId: number, data: TaskCreate): Promise<Task> {
  const response = await api.post(`/api/${userId}/tasks`, data)
  return response.data
}

export async function updateTask(userId: number, taskId: number, data: TaskUpdate): Promise<Task> {
  const response = await api.put(`/api/${userId}/tasks/${taskId}`, data)
  return response.data
}

export async function toggleTaskCompletion(userId: number, taskId: number): Promise<Task> {
  const response = await api.patch(`/api/${userId}/tasks/${taskId}/toggle`)
  return response.data
}

export async function deleteTask(userId: number, taskId: number): Promise<void> {
  await api.delete(`/api/${userId}/tasks/${taskId}`)
}
```

## Custom Hooks

### Task Management Hook (hooks/useTasks.ts)

```typescript
'use client'

import { useState, useEffect } from 'react'
import { getTasks, createTask, updateTask, toggleTaskCompletion, deleteTask } from '@/lib/api/tasks'
import { Task, TaskCreate, TaskUpdate } from '@/types/task'

export function useTasks(userId: number) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTasks()
  }, [userId])

  const fetchTasks = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getTasks(userId)
      setTasks(data)
    } catch (err) {
      setError('Failed to fetch tasks')
    } finally {
      setIsLoading(false)
    }
  }

  const addTask = async (data: TaskCreate) => {
    const newTask = await createTask(userId, data)
    setTasks((prev) => [newTask, ...prev])
  }

  const editTask = async (taskId: number, data: TaskUpdate) => {
    const updatedTask = await updateTask(userId, taskId, data)
    setTasks((prev) => prev.map((task) => (task.id === taskId ? updatedTask : task)))
  }

  const toggleTask = async (taskId: number) => {
    const updatedTask = await toggleTaskCompletion(userId, taskId)
    setTasks((prev) => prev.map((task) => (task.id === taskId ? updatedTask : task)))
  }

  const removeTask = async (taskId: number) => {
    await deleteTask(userId, taskId)
    setTasks((prev) => prev.filter((task) => task.id !== taskId))
  }

  return {
    tasks,
    isLoading,
    error,
    refresh: fetchTasks,
    addTask,
    editTask,
    toggleTask,
    removeTask,
  }
}
```

## TypeScript Types

### Task Types (types/task.ts)

```typescript
export interface Task {
  id: number
  user_id: number
  description: string
  completed: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  description: string
}

export interface TaskUpdate {
  description?: string
  completed?: boolean
}
```

### Auth Types (types/auth.ts)

```typescript
export interface User {
  id: number
  email: string
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface SignUpRequest {
  email: string
  password: string
}

export interface SignInRequest {
  email: string
  password: string
}
```

## Middleware for Auth Protection

### middleware.ts

```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value
  const isAuthPage = request.nextUrl.pathname.startsWith('/auth')
  const isDashboard = request.nextUrl.pathname.startsWith('/dashboard')

  // Redirect to signin if accessing protected route without token
  if (isDashboard && !token) {
    return NextResponse.redirect(new URL('/auth/signin', request.url))
  }

  // Redirect to dashboard if accessing auth pages with valid token
  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/auth/:path*'],
}
```

## TailwindCSS Setup

### tailwind.config.ts

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
}

export default config
```

## Testing Patterns

### Component Test (components/tasks/TaskItem.test.tsx)

```tsx
import { render, screen, fireEvent } from '@testing-library/react'
import TaskItem from './TaskItem'

describe('TaskItem', () => {
  const mockTask = {
    id: 1,
    user_id: 1,
    description: 'Test task',
    completed: false,
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
  }

  const mockOnToggle = jest.fn()
  const mockOnDelete = jest.fn()
  const mockOnEdit = jest.fn()

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

  it('calls onToggle when checkbox is clicked', () => {
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

    expect(mockOnToggle).toHaveBeenCalledWith(1)
  })
})
```

## Best Practices

### 1. Component Organization
- Use Server Components by default
- Mark Client Components with 'use client'
- Keep components small and focused
- Extract reusable UI components to components/ui/

### 2. State Management
- Use React hooks for local state
- Use custom hooks for shared logic
- Consider Zustand or Context for global state if needed
- Keep API calls in lib/api/ not in components

### 3. Error Handling
- Always handle loading and error states
- Show user-friendly error messages
- Use try/catch for async operations
- Add error boundaries for component errors

### 4. Performance
- Use React.memo for expensive components
- Implement debouncing for search/filter inputs
- Use Next.js Image component for images
- Lazy load components with dynamic imports

### 5. Accessibility
- Use semantic HTML elements
- Add ARIA labels where needed
- Ensure keyboard navigation works
- Test with screen readers

### 6. Styling
- Use TailwindCSS utility classes
- Extract common styles to @apply directives
- Use dark mode support if needed
- Keep responsive design in mind

### 7. Security
- Never store sensitive data in localStorage (except tokens)
- Always validate user input
- Sanitize HTML content
- Use HTTPS in production

## Common Pitfalls to Avoid

1. **Don't use 'use client' everywhere** - Prefer Server Components
2. **Don't fetch in Client Components** - Use Server Components or API routes
3. **Don't forget loading states** - Always show feedback to users
4. **Don't skip error handling** - Handle network failures gracefully
5. **Don't commit .env.local** - Use .env.example as template
6. **Don't inline API calls** - Use lib/api/ modules
7. **Don't forget to clean up** - Use cleanup functions in useEffect

## Environment Variables

Required variables in `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
NEXT_PUBLIC_ENVIRONMENT=development
```

## Build and Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## Next.js Configuration

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: [], // Add image domains if needed
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
}

module.exports = nextConfig
```

## Documentation

- Next.js: https://nextjs.org/docs
- React: https://react.dev
- Better Auth: https://better-auth.com/docs
- TailwindCSS: https://tailwindcss.com/docs
- TypeScript: https://www.typescriptlang.org/docs
