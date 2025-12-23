'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search } from 'lucide-react'
import DashboardHeader from './DashboardHeader'
import CategorySidebar from './CategorySidebar'
import Statistics from './Statistics'
import SearchBar from './SearchBar'
import AddTaskButton from './AddTaskButton'
import TaskCard, { Priority } from './TaskCard'
import { Task } from '@/types/task'
import { getTasks, createTask, toggleTaskCompletion } from '@/lib/api/tasks'
import { useAuthContext } from '@/components/auth/AuthProvider'

interface DashboardLayoutNewProps {
  user: any
}

export default function DashboardLayoutNew({ user }: DashboardLayoutNewProps) {
  const { signOut } = useAuthContext()
  const [activeCategory, setActiveCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoadingTasks, setIsLoadingTasks] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [showAddTaskModal, setShowAddTaskModal] = useState(false)
  const [isCreatingTask, setIsCreatingTask] = useState(false)

  // Add Task Form State
  const [taskDescription, setTaskDescription] = useState('')
  const [taskPriority, setTaskPriority] = useState<Priority>('medium')
  const [taskError, setTaskError] = useState<string | null>(null)

  useEffect(() => {
    if (user) {
      fetchTasks()
    }
  }, [user])

  const fetchTasks = async () => {
    if (!user) return
    setIsLoadingTasks(true)
    setError(null)
    try {
      const data = await getTasks(user.id)
      setTasks(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch tasks')
    } finally {
      setIsLoadingTasks(false)
    }
  }

  const handleToggleTask = async (id: number) => {
    if (!user) return
    try {
      const updatedTask = await toggleTaskCompletion(user.id, id)
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? updatedTask : task))
      )
    } catch (err) {
      console.error('Failed to toggle task', err)
    }
  }

  const handleAddTask = () => {
    setShowAddTaskModal(true)
    setTaskDescription('')
    setTaskPriority('medium')
    setTaskError(null)
  }

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!taskDescription.trim()) {
      setTaskError('Task description is required')
      return
    }

    if (!user) return
    setIsCreatingTask(true)
    setTaskError(null)

    try {
      const newTask = await createTask(user.id, {
        description: taskDescription.trim(),
        priority: taskPriority
      })
      setTasks((prev) => [newTask, ...prev])
      setShowAddTaskModal(false)
      setTaskDescription('')
      setTaskPriority('medium')
    } catch (err: any) {
      setTaskError(err.response?.data?.detail || 'Failed to create task')
    } finally {
      setIsCreatingTask(false)
    }
  }

  // Convert backend task to frontend task format
  const convertToDisplayTask = (task: Task) => {
    const priorityMap: Record<string, Priority> = {
      high: 'high',
      medium: 'medium',
      low: 'low'
    }

    const createdDate = new Date(task.created_at)
    const today = new Date()
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    const nextWeek = new Date(today)
    nextWeek.setDate(nextWeek.getDate() + 7)

    let dueDate = 'Today'
    if (createdDate < today) {
      dueDate = 'Today'
    } else if (createdDate < tomorrow) {
      dueDate = 'Tomorrow'
    } else if (createdDate < nextWeek) {
      dueDate = 'This Week'
    } else {
      dueDate = createdDate.toLocaleDateString()
    }

    const progress = task.completed ? 100 : Math.floor(Math.random() * 90) + 10

    return {
      id: task.id,
      title: task.description.length > 50 ? task.description.substring(0, 50) : task.description,
      description: task.description,
      priority: priorityMap[task.priority] || 'medium',
      dueDate,
      progress,
      completed: task.completed
    }
  }

  // Filter tasks based on active category
  const getFilteredTasks = () => {
    let filtered = tasks

    if (activeCategory === 'important') {
      filtered = tasks.filter((t) => t.priority === 'high')
    } else if (activeCategory === 'today') {
      filtered = tasks.filter((t) => !t.completed)
    } else if (activeCategory === 'week') {
      filtered = tasks.filter((t) => !t.completed)
    } else if (activeCategory === 'completed') {
      filtered = tasks.filter((t) => t.completed)
    }

    if (searchQuery) {
      filtered = filtered.filter((task) =>
        task.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    return filtered
  }

  const displayTasks = getFilteredTasks().map(convertToDisplayTask)

  // Calculate statistics
  const completedTasks = tasks.filter((t) => t.completed)
  const completionPercentage =
    tasks.length > 0 ? Math.round((completedTasks.length / tasks.length) * 100) : 0

  // Calculate categories with counts
  const categories = [
    {
      id: 'all',
      name: 'All Tasks',
      count: tasks.length,
      icon: <span>📋</span>,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500'
    },
    {
      id: 'important',
      name: 'Important',
      count: tasks.filter((t) => t.priority === 'high').length,
      icon: <span>🔥</span>,
      color: 'text-pink-400',
      bgColor: 'bg-pink-500'
    },
    {
      id: 'today',
      name: 'Today',
      count: tasks.filter((t) => !t.completed).length,
      icon: <span>📅</span>,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500'
    },
    {
      id: 'week',
      name: 'This Week',
      count: tasks.filter((t) => !t.completed).length,
      icon: <span>📆</span>,
      color: 'text-purple-400',
      bgColor: 'bg-purple-600'
    },
    {
      id: 'completed',
      name: 'Completed',
      count: completedTasks.length,
      icon: <span>✅</span>,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500'
    }
  ]

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <DashboardHeader
        userName={user?.email || 'User'}
        onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
        onSignOut={signOut}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Desktop */}
        <aside className="hidden lg:flex lg:flex-col w-72 bg-gray-900/50 border-r border-white/5 p-6">
          <CategorySidebar
            activeCategory={activeCategory}
            onCategoryChange={setActiveCategory}
            categories={categories}
          />
          <Statistics
            completionPercentage={completionPercentage}
            streakDays={12}
          />
        </aside>

        {/* Sidebar - Mobile */}
        <AnimatePresence>
          {isSidebarOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsSidebarOpen(false)}
                className="fixed inset-0 bg-black/50 z-40 lg:hidden"
              />
              <motion.aside
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                className="fixed left-0 top-0 bottom-0 w-72 bg-gray-900 p-6 z-50 lg:hidden flex flex-col border-r border-white/10"
              >
                <CategorySidebar
                  activeCategory={activeCategory}
                  onCategoryChange={(cat) => {
                    setActiveCategory(cat)
                    setIsSidebarOpen(false)
                  }}
                  categories={categories}
                />
                <Statistics
                  completionPercentage={completionPercentage}
                  streakDays={12}
                />
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto bg-gradient-to-b from-gray-800/30 to-gray-900/50">
          <div className="max-w-6xl mx-auto p-6 space-y-6">
            {/* Header Section */}
            <div className="flex items-center justify-between gap-4 flex-wrap">
              <motion.h1
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                className="text-3xl font-bold text-white"
              >
                Active Tasks
              </motion.h1>
              <AddTaskButton onClick={handleAddTask} />
            </div>

            {/* Search Bar */}
            <SearchBar value={searchQuery} onChange={setSearchQuery} />

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ y: -10, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                className="bg-red-500/10 border border-red-500/50 rounded-2xl p-4"
              >
                <p className="text-red-400 text-sm">{error}</p>
              </motion.div>
            )}

            {/* Loading State */}
            {isLoadingTasks ? (
              <div className="flex items-center justify-center py-16">
                <div className="w-12 h-12 border-4 border-t-purple-500 border-r-pink-500 border-b-purple-500 border-l-pink-500 rounded-full animate-spin"></div>
              </div>
            ) : (
              <>
                {/* Tasks List */}
                <div className="space-y-4">
                  {displayTasks.map((task, index) => (
                    <TaskCard
                      key={task.id}
                      {...task}
                      index={index}
                      onToggle={handleToggleTask}
                    />
                  ))}
                </div>

                {/* Empty State */}
                {displayTasks.length === 0 && (
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="text-center py-16"
                  >
                    <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-purple-500/10 flex items-center justify-center flex-shrink-0">
                      <svg
                        className="w-6 h-6 text-purple-400 flex-shrink-0"
                        width="24"
                        height="24"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                        />
                      </svg>
                    </div>
                    <p className="text-white/40 text-lg font-medium">
                      {searchQuery
                        ? 'No tasks found matching your search'
                        : 'No tasks yet. Create your first task!'}
                    </p>
                  </motion.div>
                )}
              </>
            )}
          </div>
        </main>
      </div>

      {/* Add Task Modal */}
      <AnimatePresence>
        {showAddTaskModal && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowAddTaskModal(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 20 }}
                onClick={(e) => e.stopPropagation()}
                className="w-full max-w-md bg-gray-800 rounded-2xl shadow-2xl overflow-hidden pointer-events-auto border border-white/10"
              >
                {/* Modal Header */}
                <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-700 border-b border-white/10">
                  <h2 className="text-xl font-bold text-white">Add New Task</h2>
                  <motion.button
                    whileHover={{ scale: 1.1, rotate: 90 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setShowAddTaskModal(false)}
                    className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <X className="w-5 h-5 text-white" />
                  </motion.button>
                </div>

                {/* Modal Content */}
                <form onSubmit={handleCreateTask} className="p-6 space-y-4">
                  <div>
                    <input
                      type="text"
                      value={taskDescription}
                      onChange={(e) => setTaskDescription(e.target.value)}
                      placeholder="What needs to be done?"
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      disabled={isCreatingTask}
                      autoFocus
                    />
                  </div>

                  <div>
                    <select
                      value={taskPriority}
                      onChange={(e) => setTaskPriority(e.target.value as Priority)}
                      disabled={isCreatingTask}
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                    >
                      <option value="low">Low Priority</option>
                      <option value="medium">Medium Priority</option>
                      <option value="high">High Priority</option>
                    </select>
                  </div>

                  {taskError && (
                    <div className="bg-red-500/10 border border-red-500/50 rounded-xl px-4 py-2">
                      <p className="text-red-400 text-sm">{taskError}</p>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={isCreatingTask || !taskDescription.trim()}
                    className="w-full px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold rounded-xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  >
                    {isCreatingTask ? 'Adding...' : 'Add Task'}
                  </button>
                </form>
              </motion.div>
            </div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
