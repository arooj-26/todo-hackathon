'use client'

import { Plus } from 'lucide-react'
import { motion } from 'framer-motion'

interface AddTaskButtonProps {
  onClick?: () => void
}

export default function AddTaskButton({ onClick }: AddTaskButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white font-bold rounded-xl flex items-center gap-2 shadow-lg hover:shadow-xl transition-shadow"
    >
      <Plus className="w-5 h-5" />
      Add New Task
    </motion.button>
  )
}
