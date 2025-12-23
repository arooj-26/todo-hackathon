/**
 * Task list component
 */
'use client'

import { Task } from '@/types/task'
import TaskItem from './TaskItem'
import { TaskListSkeleton } from '../ui/Skeleton'

interface TaskListProps {
  tasks: Task[]
  isLoading?: boolean
  onToggle: (taskId: number) => Promise<void>
  onDelete: (taskId: number) => Promise<void>
  onEdit?: (taskId: number, description: string) => Promise<void>
}

export default function TaskList({ tasks, isLoading = false, onToggle, onDelete, onEdit }: TaskListProps) {
  if (isLoading) {
    return <TaskListSkeleton count={5} />
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-900/20 border-2 border-dashed border-gray-800">
        <div className="w-12 h-12 mx-auto mb-4 border-2 border-gray-800 flex items-center justify-center">
          <svg
            className="text-gray-600"
            width="24"
            height="24"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="square"
              strokeLinejoin="miter"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
        <p className="font-mono text-xs text-gray-600 uppercase tracking-widest mb-2">[EMPTY]</p>
        <p className="text-sm text-gray-500">NO TASKS FOUND</p>
      </div>
    )
  }

  // Separate completed and incomplete tasks
  const incompleteTasks = tasks.filter(task => !task.completed)
  const completedTasks = tasks.filter(task => task.completed)

  return (
    <div className="space-y-8">
      {incompleteTasks.length > 0 && (
        <div>
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-3 h-3 bg-lime-400"></div>
            <h3 className="font-mono text-xs text-white uppercase tracking-widest">ACTIVE [{incompleteTasks.length}]</h3>
            <div className="flex-1 h-px bg-gray-800"></div>
          </div>
          <div className="space-y-2">
            {incompleteTasks.map((task, index) => (
              <div key={task.id} style={{ animationDelay: `${index * 0.05}s` }} className="animate-slide-up">
                <TaskItem
                  task={task}
                  onToggle={onToggle}
                  onDelete={onDelete}
                  onEdit={onEdit}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {completedTasks.length > 0 && (
        <div>
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-3 h-3 bg-gray-700"></div>
            <h3 className="font-mono text-xs text-gray-600 uppercase tracking-widest">COMPLETED [{completedTasks.length}]</h3>
            <div className="flex-1 h-px bg-gray-900"></div>
          </div>
          <div className="space-y-2">
            {completedTasks.map((task, index) => (
              <div key={task.id} style={{ animationDelay: `${index * 0.05}s` }} className="animate-slide-up">
                <TaskItem
                  task={task}
                  onToggle={onToggle}
                  onDelete={onDelete}
                  onEdit={onEdit}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
