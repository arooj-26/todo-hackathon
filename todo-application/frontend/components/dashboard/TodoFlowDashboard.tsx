'use client'

import { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, CheckSquare, CalendarDays, TrendingUp, LogOut, Plus,
  Trash2, Calendar, Flame, Pencil, Clock, Target, Zap, Search, Filter, CalendarIcon,
  ArrowUpDown, ArrowUp, ArrowDown, Menu, X
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { toast, Toaster } from 'sonner'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { cn } from '@/lib/utils'
import { getTasks, createTask, toggleTaskCompletion, deleteTask, updateTask } from '@/lib/api/tasks'
import { Task, Priority, Recurrence } from '@/types/task'
import FloatingChatWidget from '@/components/chatbot/FloatingChatWidget'

interface TodoFlowDashboardProps {
  user: any
  onSignOut: () => void
}

export default function TodoFlowDashboard({ user, onSignOut }: TodoFlowDashboardProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false)
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [newTaskPriority, setNewTaskPriority] = useState<Priority>('medium')
  const [newTaskDueDate, setNewTaskDueDate] = useState<string | null>(null)
  const [newTaskRecurrence, setNewTaskRecurrence] = useState<Recurrence>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [activeNav, setActiveNav] = useState('dashboard')
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [isEditTaskOpen, setIsEditTaskOpen] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  // Filtering, searching, and sorting
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed' | 'overdue'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<'date' | 'priority' | 'alphabetical'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  useEffect(() => {
    if (user) loadTasks()
  }, [user])

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && user) loadTasks()
    }
    document.addEventListener('visibilitychange', handleVisibilityChange)
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
  }, [user])

  useEffect(() => {
    if (!user) return
    const intervalId = setInterval(() => loadTasks(), 30000)
    return () => clearInterval(intervalId)
  }, [user])

  useEffect(() => {
    document.body.style.overflow = isSidebarOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [isSidebarOpen])

  const loadTasks = async () => {
    try {
      setIsLoading(true)
      const data = await getTasks(user.id)
      setTasks(data)
    } catch (error: any) {
      toast.error('Failed to load tasks')
    } finally {
      setIsLoading(false)
    }
  }

  const handleToggleTask = async (taskId: number) => {
    try {
      const updatedTask = await toggleTaskCompletion(user.id, taskId)
      setTasks((prev) => prev.map((task) => (task.id === taskId ? updatedTask : task)))
      toast.success(updatedTask.completed ? '✅ Task completed!' : '🔄 Task reopened')
    } catch (error) {
      toast.error('Failed to update task')
    }
  }

  const handleDeleteTask = async (taskId: number) => {
    try {
      await deleteTask(user.id, taskId)
      setTasks((prev) => prev.filter((task) => task.id !== taskId))
      toast.success('🗑️ Task deleted')
    } catch (error) {
      toast.error('Failed to delete task')
    }
  }

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTaskDescription.trim()) {
      toast.error('Please enter a task description')
      return
    }
    try {
      setIsSubmitting(true)
      const newTask = await createTask(user.id, {
        description: newTaskDescription.trim(),
        priority: newTaskPriority,
        due_date: newTaskDueDate,
        recurrence: newTaskRecurrence,
      })
      setTasks((prev) => [newTask, ...prev])
      setIsAddTaskOpen(false)
      setNewTaskDescription('')
      setNewTaskPriority('medium')
      setNewTaskDueDate(null)
      setNewTaskRecurrence(null)
      toast.success('✨ Task created!')
    } catch (error) {
      toast.error('Failed to create task')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleEditTask = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingTask || !newTaskDescription.trim()) return
    try {
      setIsSubmitting(true)
      const updatedTask = await updateTask(user.id, editingTask.id, {
        description: newTaskDescription.trim(),
        priority: newTaskPriority,
        due_date: newTaskDueDate,
        recurrence: newTaskRecurrence,
      })
      setTasks((prev) => prev.map((task) => (task.id === editingTask.id ? updatedTask : task)))
      setIsEditTaskOpen(false)
      setEditingTask(null)
      setNewTaskDescription('')
      setNewTaskPriority('medium')
      setNewTaskDueDate(null)
      setNewTaskRecurrence(null)
      toast.success('✏️ Task updated!')
    } catch (error) {
      toast.error('Failed to update task')
    } finally {
      setIsSubmitting(false)
    }
  }

  const openEditDialog = (task: Task) => {
    setEditingTask(task)
    setNewTaskDescription(task.description)
    setNewTaskPriority(task.priority)
    setNewTaskDueDate(task.due_date || null)
    setNewTaskRecurrence(task.recurrence)
    setIsEditTaskOpen(true)
  }

  const filteredAndSortedTasks = useMemo(() => {
    let result = [...tasks]
    if (searchQuery) {
      result = result.filter(task =>
        task.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }
    if (filter === 'pending') result = result.filter(task => !task.completed)
    else if (filter === 'completed') result = result.filter(task => task.completed)
    else if (filter === 'overdue') {
      result = result.filter(task =>
        !task.completed && task.due_date && new Date(task.due_date) < new Date()
      )
    }
    result.sort((a, b) => {
      let comparison = 0
      if (sortBy === 'date') {
        if (a.due_date && !b.due_date) return -1
        if (!a.due_date && b.due_date) return 1
        if (!a.due_date && !b.due_date) return 0
        comparison = new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
      } else if (sortBy === 'priority') {
        const priorityOrder = { high: 3, medium: 2, low: 1 }
        comparison = priorityOrder[b.priority] - priorityOrder[a.priority]
      } else if (sortBy === 'alphabetical') {
        comparison = a.description.localeCompare(b.description)
      }
      return sortOrder === 'asc' ? comparison : -comparison
    })
    return result
  }, [tasks, filter, searchQuery, sortBy, sortOrder])

  const totalTasks = tasks.length
  const completedTasks = tasks.filter((t) => t.completed).length
  const pendingTasks = totalTasks - completedTasks
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
  const highPriority = tasks.filter((t) => t.priority === 'high' && !t.completed).length
  const mediumPriority = tasks.filter((t) => t.priority === 'medium' && !t.completed).length
  const lowPriority = tasks.filter((t) => t.priority === 'low' && !t.completed).length
  const overdueTasks = tasks.filter((t) =>
    !t.completed && t.due_date && new Date(t.due_date) < new Date()
  ).length

  const chartData = [
    { name: 'Completed', value: completedTasks, color: '#10b981' },
    { name: 'Pending', value: pendingTasks, color: '#f59e0b' },
  ]

  const navItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'tasks', icon: CheckSquare, label: 'All Tasks' },
    { id: 'calendar', icon: CalendarDays, label: 'Calendar' },
    { id: 'analytics', icon: TrendingUp, label: 'Analytics' },
  ]

  const SidebarContent = ({ onNavClick }: { onNavClick?: () => void }) => (
    <>
      {/* Logo */}
      <div className="p-5 border-b border-purple-100/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0">
            <CheckSquare className="w-5 h-5 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              TodoFlow
            </h1>
            <p className="text-xs text-gray-500 font-medium">Task Management Pro</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => { setActiveNav(item.id); onNavClick?.() }}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all",
              activeNav === item.id
                ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg"
                : "text-gray-700 hover:bg-purple-50 hover:text-purple-700"
            )}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {item.label}
          </button>
        ))}
      </nav>

      {/* User Profile */}
      <div className="p-4 border-t border-purple-100/50">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 mb-3">
          <div className="w-9 h-9 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-md flex-shrink-0">
            <span className="text-white text-sm font-bold">
              {user?.email?.[0]?.toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-gray-900 truncate">
              {user?.email?.split('@')[0] || 'User'}
            </p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
        </div>
        <Button variant="outline" className="w-full text-sm" onClick={onSignOut}>
          <LogOut className="w-4 h-4 mr-2" />
          Logout
        </Button>
      </div>
    </>
  )

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-slate-50 via-purple-50/30 to-pink-50/20 overflow-hidden">
      <Toaster position="top-right" richColors expand={true} />

      {/* DESKTOP SIDEBAR */}
      <aside className="hidden lg:flex lg:flex-col w-64 xl:w-72 bg-white/80 backdrop-blur-xl border-r border-purple-100/50 overflow-y-auto shadow-2xl flex-shrink-0">
        <SidebarContent />
      </aside>

      {/* MOBILE SIDEBAR OVERLAY */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            key="mobile-sidebar-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 lg:hidden"
          >
            {/* Backdrop */}
            <div
              className="absolute inset-0 bg-black/50"
              onClick={() => setIsSidebarOpen(false)}
            />
            {/* Sidebar Panel */}
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'tween', duration: 0.25, ease: 'easeInOut' }}
              className="absolute left-0 top-0 h-full w-72 max-w-[85vw] bg-white flex flex-col shadow-2xl overflow-y-auto"
            >
              <div className="flex items-center justify-between p-4 border-b border-purple-100/50">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                    <CheckSquare className="w-4 h-4 text-white" strokeWidth={2.5} />
                  </div>
                  <span className="font-bold text-gray-800">TodoFlow</span>
                </div>
                <button
                  onClick={() => setIsSidebarOpen(false)}
                  className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <X className="w-5 h-5 text-gray-600" />
                </button>
              </div>
              <SidebarContent onNavClick={() => setIsSidebarOpen(false)} />
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>

      {/* MAIN CONTENT */}
      <main className="flex-1 overflow-y-auto min-w-0">
        {/* Mobile top bar */}
        <div className="lg:hidden flex items-center justify-between px-4 py-3 bg-white/80 backdrop-blur-xl border-b border-purple-100/50 sticky top-0 z-30">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 rounded-xl hover:bg-purple-50 transition-colors"
          >
            <Menu className="w-5 h-5 text-gray-700" />
          </button>
          <h1 className="text-lg font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            TodoFlow
          </h1>
          <button
            onClick={() => setIsAddTaskOpen(true)}
            className="p-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-md"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        <div className="px-4 py-4 md:px-6 md:py-6 lg:px-8 lg:py-8 w-full">

          {/* Header */}
          <div className="mb-6 md:mb-8 text-center">
            <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Welcome back, {user?.email?.split('@')[0] || 'User'}! ✨
            </h2>
            <p className="text-gray-600 text-sm md:text-base">Here's what's happening with your tasks today.</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 md:gap-4 lg:gap-6 mb-6 md:mb-8">
            <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100/50">
              <CardHeader className="pb-1 pt-4 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs font-bold text-blue-900">Total Tasks</CardTitle>
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md flex-shrink-0">
                    <CheckSquare className="h-4 w-4 md:h-5 md:w-5 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4">
                <div className="text-2xl md:text-3xl font-bold text-blue-700">{totalTasks}</div>
                <p className="text-xs text-blue-600 mt-0.5">All tasks</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100/50">
              <CardHeader className="pb-1 pt-4 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs font-bold text-green-900">Completed</CardTitle>
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-md flex-shrink-0">
                    <TrendingUp className="h-4 w-4 md:h-5 md:w-5 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4">
                <div className="text-2xl md:text-3xl font-bold text-green-700">{completedTasks}</div>
                <p className="text-xs text-green-600 mt-0.5">{completionRate}% rate</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100/50">
              <CardHeader className="pb-1 pt-4 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs font-bold text-orange-900">Pending</CardTitle>
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-md flex-shrink-0">
                    <Clock className="h-4 w-4 md:h-5 md:w-5 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4">
                <div className="text-2xl md:text-3xl font-bold text-orange-700">{pendingTasks}</div>
                <p className="text-xs text-orange-600 mt-0.5">To complete</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-red-50 to-red-100/50">
              <CardHeader className="pb-1 pt-4 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs font-bold text-red-900">High Priority</CardTitle>
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center shadow-md flex-shrink-0">
                    <Flame className="h-4 w-4 md:h-5 md:w-5 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4">
                <div className="text-2xl md:text-3xl font-bold text-red-700">{highPriority}</div>
                <p className="text-xs text-red-600 mt-0.5">Urgent tasks</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg bg-gradient-to-br from-rose-50 to-rose-100/50 col-span-2 md:col-span-1">
              <CardHeader className="pb-1 pt-4 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-xs font-bold text-rose-900">Overdue</CardTitle>
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gradient-to-br from-rose-500 to-rose-600 flex items-center justify-center shadow-md flex-shrink-0">
                    <Calendar className="h-4 w-4 md:h-5 md:w-5 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4">
                <div className="text-2xl md:text-3xl font-bold text-rose-700">{overdueTasks}</div>
                <p className="text-xs text-rose-600 mt-0.5">Past due</p>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 mb-6 md:mb-8">
            <Card className="border-0 shadow-xl bg-white/90">
              <CardHeader>
                <CardTitle className="text-base md:text-lg">Progress Overview</CardTitle>
              </CardHeader>
              <CardContent>
                {totalTasks > 0 ? (
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie data={chartData} cx="50%" cy="50%" innerRadius={50} outerRadius={70} paddingAngle={5} dataKey="value">
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[180px] flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <CheckSquare className="w-10 h-10 mx-auto mb-2 opacity-20" />
                      <p className="text-sm">No tasks yet</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="md:col-span-1 lg:col-span-2 border-0 shadow-xl bg-white/90">
              <CardHeader>
                <CardTitle className="text-base md:text-lg">Priority Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-xl bg-red-50 border border-red-200">
                  <div className="flex items-center gap-2 md:gap-3">
                    <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Flame className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm font-bold text-red-900">High Priority</span>
                  </div>
                  <span className="text-xl md:text-2xl font-bold text-red-700">{highPriority}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-yellow-50 border border-yellow-200">
                  <div className="flex items-center gap-2 md:gap-3">
                    <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Target className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm font-bold text-yellow-900">Medium Priority</span>
                  </div>
                  <span className="text-xl md:text-2xl font-bold text-yellow-700">{mediumPriority}</span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-xl bg-green-50 border border-green-200">
                  <div className="flex items-center gap-2 md:gap-3">
                    <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center flex-shrink-0">
                      <CheckSquare className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm font-bold text-green-900">Low Priority</span>
                  </div>
                  <span className="text-xl md:text-2xl font-bold text-green-700">{lowPriority}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Task List */}
          <Card className="border-0 shadow-2xl bg-white/95">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-t-xl">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <CardTitle className="text-lg md:text-xl">Your Tasks</CardTitle>
                <div className="flex gap-2">
                  <div className="relative flex-1 sm:flex-none">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="Search tasks..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 text-sm"
                    />
                  </div>
                  <Button
                    onClick={() => setIsAddTaskOpen(true)}
                    className="hidden sm:flex bg-gradient-to-r from-purple-600 to-pink-600 flex-shrink-0"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Task
                  </Button>
                </div>
              </div>

              {/* Filter and Sort */}
              <div className="flex flex-wrap gap-2 mt-3">
                <div className="flex items-center gap-1.5">
                  <Filter className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                  <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value as any)}
                    className="h-8 rounded-md border px-2 text-xs bg-white"
                  >
                    <option value="all">All</option>
                    <option value="pending">Pending</option>
                    <option value="completed">Completed</option>
                    <option value="overdue">Overdue</option>
                  </select>
                </div>

                <div className="flex items-center gap-1.5">
                  <ArrowUpDown className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" />
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="h-8 rounded-md border px-2 text-xs bg-white"
                  >
                    <option value="date">Due Date</option>
                    <option value="priority">Priority</option>
                    <option value="alphabetical">A–Z</option>
                  </select>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="h-8 text-xs px-2"
                >
                  {sortOrder === 'asc' ? <ArrowUp className="w-3.5 h-3.5 mr-1" /> : <ArrowDown className="w-3.5 h-3.5 mr-1" />}
                  {sortOrder === 'asc' ? 'Asc' : 'Desc'}
                </Button>
              </div>
            </CardHeader>

            <CardContent className="p-4 md:p-6">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-10 w-10 border-4 border-purple-200 border-t-purple-600"></div>
                </div>
              ) : filteredAndSortedTasks.length === 0 ? (
                <div className="text-center py-10 md:py-12">
                  <CheckSquare className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-lg font-bold text-gray-900 mb-2">No tasks found</h3>
                  <p className="text-gray-600 text-sm mb-4">
                    {searchQuery || filter !== 'all'
                      ? 'Try changing your search or filter'
                      : 'Create your first task!'}
                  </p>
                  <Button onClick={() => setIsAddTaskOpen(true)} size="sm">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Task
                  </Button>
                </div>
              ) : (
                <div className="space-y-2 md:space-y-3">
                  {filteredAndSortedTasks.map((task) => (
                    <div
                      key={task.id}
                      className={cn(
                        "flex items-start gap-3 p-3 md:p-4 rounded-xl border-2 transition-all",
                        task.completed
                          ? "bg-gray-50 border-gray-200"
                          : "bg-white border-purple-200 hover:border-purple-400 hover:shadow-md"
                      )}
                    >
                      <Checkbox
                        checked={task.completed}
                        onCheckedChange={() => handleToggleTask(task.id)}
                        className="h-5 w-5 mt-0.5 flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <p className={cn("font-semibold text-sm md:text-base break-words", task.completed ? "line-through text-gray-400" : "text-gray-900")}>
                          {task.description}
                        </p>
                        <div className="flex flex-wrap items-center gap-2 mt-1">
                          {task.due_date && (
                            <div className="flex items-center gap-1 text-xs text-gray-500">
                              <CalendarIcon className="w-3 h-3 flex-shrink-0" />
                              <span>
                                {new Date(task.due_date).toLocaleDateString()}
                                {new Date(task.due_date) < new Date() && !task.completed && (
                                  <span className="ml-1 text-red-500">(Overdue)</span>
                                )}
                              </span>
                            </div>
                          )}
                          {task.recurrence && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
                              {task.recurrence}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 flex-shrink-0">
                        <Badge className={cn(
                          "text-xs hidden sm:inline-flex",
                          task.priority === 'high' && "bg-red-500",
                          task.priority === 'medium' && "bg-yellow-500",
                          task.priority === 'low' && "bg-green-500"
                        )}>
                          {task.priority.toUpperCase()}
                        </Badge>
                        <Button variant="ghost" size="icon" onClick={() => openEditDialog(task)} className="h-8 w-8">
                          <Pencil className="w-3.5 h-3.5" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDeleteTask(task.id)} className="h-8 w-8">
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Add Task Dialog */}
      <Dialog open={isAddTaskOpen} onOpenChange={setIsAddTaskOpen}>
        <DialogContent className="w-[95vw] max-w-md mx-auto">
          <DialogHeader>
            <DialogTitle>Add New Task</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddTask} className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Description</label>
              <Input
                value={newTaskDescription}
                onChange={(e) => setNewTaskDescription(e.target.value)}
                placeholder="What needs to be done?"
                autoFocus
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Priority</label>
              <select
                value={newTaskPriority}
                onChange={(e) => setNewTaskPriority(e.target.value as Priority)}
                className="w-full h-10 rounded-md border px-3 text-sm"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Due Date (Optional)</label>
              <Input
                type="date"
                value={newTaskDueDate || ''}
                onChange={(e) => setNewTaskDueDate(e.target.value || null)}
                className="w-full"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Recurrence (Optional)</label>
              <select
                value={newTaskRecurrence || ''}
                onChange={(e) => setNewTaskRecurrence(e.target.value as Recurrence || null)}
                className="w-full h-10 rounded-md border px-3 text-sm"
              >
                <option value="">No recurrence</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <DialogFooter className="flex-col sm:flex-row gap-2">
              <Button type="button" variant="outline" onClick={() => setIsAddTaskOpen(false)} className="w-full sm:w-auto">Cancel</Button>
              <Button type="submit" disabled={isSubmitting} className="w-full sm:w-auto">
                {isSubmitting ? 'Creating...' : 'Create'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Task Dialog */}
      <Dialog open={isEditTaskOpen} onOpenChange={setIsEditTaskOpen}>
        <DialogContent className="w-[95vw] max-w-md mx-auto">
          <DialogHeader>
            <DialogTitle>Edit Task</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditTask} className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Description</label>
              <Input
                value={newTaskDescription}
                onChange={(e) => setNewTaskDescription(e.target.value)}
                placeholder="What needs to be done?"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Priority</label>
              <select
                value={newTaskPriority}
                onChange={(e) => setNewTaskPriority(e.target.value as Priority)}
                className="w-full h-10 rounded-md border px-3 text-sm"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Due Date (Optional)</label>
              <Input
                type="date"
                value={newTaskDueDate || ''}
                onChange={(e) => setNewTaskDueDate(e.target.value || null)}
                className="w-full"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Recurrence (Optional)</label>
              <select
                value={newTaskRecurrence || ''}
                onChange={(e) => setNewTaskRecurrence(e.target.value as Recurrence || null)}
                className="w-full h-10 rounded-md border px-3 text-sm"
              >
                <option value="">No recurrence</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <DialogFooter className="flex-col sm:flex-row gap-2">
              <Button type="button" variant="outline" onClick={() => setIsEditTaskOpen(false)} className="w-full sm:w-auto">Cancel</Button>
              <Button type="submit" disabled={isSubmitting} className="w-full sm:w-auto">
                {isSubmitting ? 'Updating...' : 'Update'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <FloatingChatWidget userId={user?.id} onTasksUpdate={loadTasks} />
    </div>
  )
}
