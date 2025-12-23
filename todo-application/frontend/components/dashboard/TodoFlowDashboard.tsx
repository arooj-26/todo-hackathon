'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, CheckSquare, CalendarDays, TrendingUp, LogOut, Plus,
  Trash2, Calendar, Flame, Pencil, Clock, Target, Zap
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { toast, Toaster } from 'sonner'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { cn } from '@/lib/utils'
import { getTasks, createTask, toggleTaskCompletion, deleteTask, updateTask } from '@/lib/api/tasks'
import { Task, Priority } from '@/types/task'
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
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [activeNav, setActiveNav] = useState('dashboard')
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [isEditTaskOpen, setIsEditTaskOpen] = useState(false)

  useEffect(() => {
    if (user) {
      loadTasks()
    }
  }, [user])

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
      })
      setTasks((prev) => [newTask, ...prev])
      setIsAddTaskOpen(false)
      setNewTaskDescription('')
      setNewTaskPriority('medium')
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
      })
      setTasks((prev) => prev.map((task) => (task.id === editingTask.id ? updatedTask : task)))
      setIsEditTaskOpen(false)
      setEditingTask(null)
      setNewTaskDescription('')
      setNewTaskPriority('medium')
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
    setIsEditTaskOpen(true)
  }

  const totalTasks = tasks.length
  const completedTasks = tasks.filter((t) => t.completed).length
  const pendingTasks = totalTasks - completedTasks
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0
  const highPriority = tasks.filter((t) => t.priority === 'high' && !t.completed).length
  const mediumPriority = tasks.filter((t) => t.priority === 'medium' && !t.completed).length
  const lowPriority = tasks.filter((t) => t.priority === 'low' && !t.completed).length

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

  return (
    <div className="flex h-screen w-full bg-gradient-to-br from-slate-50 via-purple-50/30 to-pink-50/20">
      <Toaster position="top-right" richColors expand={true} />

      {/* LEFT SIDEBAR - FIXED WIDTH */}
      <aside className="w-72 bg-white/80 backdrop-blur-xl border-r border-purple-100/50 flex flex-col overflow-y-auto shadow-2xl">
        {/* Logo */}
        <div className="p-6 border-b border-purple-100/50">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
              <CheckSquare className="w-6 h-6 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                TodoFlow
              </h1>
              <p className="text-xs text-gray-500 font-medium">Task Management Pro</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-5 py-3.5 rounded-xl text-sm font-semibold transition-all",
                activeNav === item.id
                  ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg"
                  : "text-gray-700 hover:bg-purple-50 hover:text-purple-700"
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </button>
          ))}
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-purple-100/50">
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gradient-to-br from-purple-50 to-pink-50 mb-3">
            <div className="w-11 h-11 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center shadow-md">
              <span className="text-white text-base font-bold">
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
          <Button variant="outline" className="w-full" onClick={onSignOut}>
            <LogOut className="w-4 h-4 mr-2" />
            Logout
          </Button>
        </div>
      </aside>

      {/* RIGHT MAIN CONTENT - FLEXIBLE WIDTH */}
      <main className="flex-1 overflow-y-auto">
        <div className="px-8 py-8 w-full">

          {/* Header */}
          <div className="mb-8 text-center">
            <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Welcome back, {user?.email?.split('@')[0] || 'User'}! ✨
            </h2>
            <p className="text-gray-600 text-lg">Here's what's happening with your tasks today.</p>
          </div>

          {/* Stats Grid - 4 Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="border-0 shadow-xl bg-gradient-to-br from-blue-50 to-blue-100/50">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-bold text-blue-900">Total Tasks</CardTitle>
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg">
                    <CheckSquare className="h-6 w-6 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold text-blue-700">{totalTasks}</div>
                <p className="text-xs text-blue-600 mt-1">All tasks in workspace</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-gradient-to-br from-green-50 to-green-100/50">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-bold text-green-900">Completed</CardTitle>
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg">
                    <TrendingUp className="h-6 w-6 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold text-green-700">{completedTasks}</div>
                <p className="text-xs text-green-600 mt-1">{completionRate}% completion rate</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-gradient-to-br from-orange-50 to-orange-100/50">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-bold text-orange-900">Pending</CardTitle>
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg">
                    <Clock className="h-6 w-6 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold text-orange-700">{pendingTasks}</div>
                <p className="text-xs text-orange-600 mt-1">Tasks to complete</p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-xl bg-gradient-to-br from-red-50 to-red-100/50">
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-sm font-bold text-red-900">High Priority</CardTitle>
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex items-center justify-center shadow-lg">
                    <Flame className="h-6 w-6 text-white" strokeWidth={2.5} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold text-red-700">{highPriority}</div>
                <p className="text-xs text-red-600 mt-1">Urgent tasks</p>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <Card className="border-0 shadow-xl bg-white/90">
              <CardHeader>
                <CardTitle className="text-lg">Progress Overview</CardTitle>
              </CardHeader>
              <CardContent>
                {totalTasks > 0 ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie data={chartData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[200px] flex items-center justify-center text-gray-400">
                    <div className="text-center">
                      <CheckSquare className="w-12 h-12 mx-auto mb-2 opacity-20" />
                      <p className="text-sm">No tasks yet</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="lg:col-span-2 border-0 shadow-xl bg-white/90">
              <CardHeader>
                <CardTitle className="text-lg">Priority Breakdown</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-xl bg-red-50 border border-red-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
                      <Flame className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-sm font-bold text-red-900">High Priority</span>
                  </div>
                  <span className="text-2xl font-bold text-red-700">{highPriority}</span>
                </div>
                <div className="flex items-center justify-between p-4 rounded-xl bg-yellow-50 border border-yellow-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-yellow-500 rounded-lg flex items-center justify-center">
                      <Target className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-sm font-bold text-yellow-900">Medium Priority</span>
                  </div>
                  <span className="text-2xl font-bold text-yellow-700">{mediumPriority}</span>
                </div>
                <div className="flex items-center justify-between p-4 rounded-xl bg-green-50 border border-green-200">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                      <CheckSquare className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-sm font-bold text-green-900">Low Priority</span>
                  </div>
                  <span className="text-2xl font-bold text-green-700">{lowPriority}</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Task List */}
          <Card className="border-0 shadow-2xl bg-white/95">
            <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50">
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl">Your Tasks</CardTitle>
                <Button onClick={() => setIsAddTaskOpen(true)} className="bg-gradient-to-r from-purple-600 to-pink-600">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Task
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {isLoading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-4 border-purple-200 border-t-purple-600"></div>
                </div>
              ) : tasks.length === 0 ? (
                <div className="text-center py-12">
                  <CheckSquare className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                  <h3 className="text-xl font-bold text-gray-900 mb-2">No tasks yet</h3>
                  <p className="text-gray-600 mb-4">Create your first task!</p>
                  <Button onClick={() => setIsAddTaskOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Create Task
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className={cn(
                        "flex items-center gap-4 p-4 rounded-xl border-2 transition-all",
                        task.completed
                          ? "bg-gray-50 border-gray-200"
                          : "bg-white border-purple-200 hover:border-purple-400 hover:shadow-md"
                      )}
                    >
                      <Checkbox
                        checked={task.completed}
                        onCheckedChange={() => handleToggleTask(task.id)}
                        className="h-5 w-5"
                      />
                      <div className="flex-1">
                        <p className={cn("font-semibold", task.completed ? "line-through text-gray-400" : "text-gray-900")}>
                          {task.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(task.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <Badge className={cn(
                        task.priority === 'high' && "bg-red-500",
                        task.priority === 'medium' && "bg-yellow-500",
                        task.priority === 'low' && "bg-green-500"
                      )}>
                        {task.priority.toUpperCase()}
                      </Badge>
                      <Button variant="ghost" size="icon" onClick={() => openEditDialog(task)}>
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => handleDeleteTask(task.id)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Dialogs */}
      <Dialog open={isAddTaskOpen} onOpenChange={setIsAddTaskOpen}>
        <DialogContent>
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
                className="w-full h-10 rounded-md border px-3"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsAddTaskOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Creating...' : 'Create'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={isEditTaskOpen} onOpenChange={setIsEditTaskOpen}>
        <DialogContent>
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
                className="w-full h-10 rounded-md border px-3"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setIsEditTaskOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Updating...' : 'Update'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Chatbot - Fixed on right */}
      <FloatingChatWidget userId={user.id} onTasksUpdate={loadTasks} />
    </div>
  )
}
