'use client'

import { motion } from 'framer-motion'
import { Calendar, Briefcase } from 'lucide-react'

export type Priority = 'high' | 'medium' | 'low'

interface TaskCardProps {
  id: number
  title: string
  description: string
  priority: Priority
  dueDate: string
  progress: number
  completed?: boolean
  onToggle?: (id: number) => void
  index?: number
}

const priorityConfig = {
  high: {
    label: 'High',
    color: 'bg-pink-500',
    textColor: 'text-pink-500',
    borderClass: 'task-border-pink',
    progressClass: 'progress-bar-pink'
  },
  medium: {
    label: 'Medium',
    color: 'bg-indigo-500',
    textColor: 'text-indigo-500',
    borderClass: 'task-border-blue',
    progressClass: 'progress-bar-blue'
  },
  low: {
    label: 'Low',
    color: 'bg-emerald-500',
    textColor: 'text-emerald-500',
    borderClass: 'task-border-green',
    progressClass: 'progress-bar-green'
  }
}

export default function TaskCard({
  id,
  title,
  description,
  priority,
  dueDate,
  progress,
  completed = false,
  onToggle,
  index = 0
}: TaskCardProps) {
  const config = priorityConfig[priority]

  return (
    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ scale: 1.01 }}
      className={`card-dark p-6 ${config.borderClass} group cursor-pointer`}
      onClick={() => onToggle?.(id)}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={(e) => {
            e.stopPropagation()
            onToggle?.(id)
          }}
          className={`
            mt-1 w-6 h-6 rounded-full border-2 flex items-center justify-center
            transition-all duration-200
            ${
              completed
                ? `${config.color} border-transparent`
                : 'border-white/30 hover:border-white/50'
            }
          `}
        >
          {completed && (
            <motion.svg
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="w-4 h-4 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={3}
                d="M5 13l4 4L19 7"
              />
            </motion.svg>
          )}
        </motion.button>

        {/* Task Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-4 mb-2">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                {title}
                <Briefcase className="w-4 h-4 text-white/40" />
              </h3>
              <p className="text-sm text-white/60">{description}</p>
            </div>

            {/* Priority & Due Date */}
            <div className="flex items-center gap-3 flex-shrink-0">
              <motion.span
                whileHover={{ scale: 1.05 }}
                className={`
                  ${config.color} text-white text-xs font-semibold
                  px-4 py-1.5 rounded-full shadow-lg
                `}
              >
                {config.label}
              </motion.span>

              <div className="flex items-center gap-1.5 text-white/50 text-sm">
                <Calendar className="w-4 h-4" />
                <span>{dueDate}</span>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ delay: index * 0.05 + 0.2, duration: 0.6 }}
                className={`h-full ${config.progressClass} rounded-full`}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
