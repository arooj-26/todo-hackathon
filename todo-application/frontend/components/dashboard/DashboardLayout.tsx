'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import DashboardHeader from './DashboardHeader'
import CategorySidebar from './CategorySidebar'
import Statistics from './Statistics'
import SearchBar from './SearchBar'
import AddTaskButton from './AddTaskButton'
import TaskCard, { Priority } from './TaskCard'

interface Task {
  id: number
  title: string
  description: string
  priority: Priority
  dueDate: string
  progress: number
  completed?: boolean
}

// Mock data for demo
const mockTasks: Task[] = [
  {
    id: 1,
    title: 'Complete project proposal',
    description: 'Finish and submit the Q1 project proposal to management team',
    priority: 'high',
    dueDate: 'Today',
    progress: 75,
    completed: false
  },
  {
    id: 2,
    title: 'Review pull requests',
    description: 'Review and merge pending pull requests in the main repository',
    priority: 'medium',
    dueDate: 'Tomorrow',
    progress: 50,
    completed: false
  },
  {
    id: 3,
    title: 'Update documentation',
    description: 'Update API documentation with new endpoints and examples',
    priority: 'low',
    dueDate: 'This Week',
    progress: 90,
    completed: false
  }
]

export default function DashboardLayout() {
  const [activeCategory, setActiveCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [tasks, setTasks] = useState<Task[]>(mockTasks)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const handleToggleTask = (id: number) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    )
  }

  const handleAddTask = () => {
    // This will be implemented when we integrate with the backend
    console.log('Add new task')
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <DashboardHeader
        userName="John Doe"
        onMenuClick={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Desktop */}
        <aside className="hidden lg:flex lg:flex-col w-80 sidebar-dark p-6">
          <CategorySidebar
            activeCategory={activeCategory}
            onCategoryChange={setActiveCategory}
          />
          <Statistics completionPercentage={76} streakDays={12} />
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
                className="fixed left-0 top-0 bottom-0 w-80 sidebar-dark p-6 z-50 lg:hidden flex flex-col"
              >
                <CategorySidebar
                  activeCategory={activeCategory}
                  onCategoryChange={(cat) => {
                    setActiveCategory(cat)
                    setIsSidebarOpen(false)
                  }}
                />
                <Statistics completionPercentage={76} streakDays={12} />
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
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

            {/* Tasks List */}
            <div className="space-y-4">
              {tasks
                .filter((task) =>
                  task.title.toLowerCase().includes(searchQuery.toLowerCase())
                )
                .map((task, index) => (
                  <TaskCard
                    key={task.id}
                    {...task}
                    index={index}
                    onToggle={handleToggleTask}
                  />
                ))}
            </div>

            {/* Empty State */}
            {tasks.length === 0 && (
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-center py-16"
              >
                <p className="text-white/40 text-lg">
                  No tasks found. Create your first task!
                </p>
              </motion.div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
