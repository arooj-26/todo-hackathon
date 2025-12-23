'use client'

import { motion } from 'framer-motion'
import { TrendingUp, Flame } from 'lucide-react'

interface StatisticsProps {
  completionPercentage?: number
  streakDays?: number
}

export default function Statistics({
  completionPercentage = 76,
  streakDays = 12
}: StatisticsProps) {
  return (
    <div className="mt-auto px-4 py-6 border-t border-white/5">
      <h2 className="text-sm font-semibold text-white/60 mb-4">Statistics</h2>

      <div className="space-y-4">
        {/* Completion Percentage */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-2 text-cyan-400">
            <TrendingUp className="w-4 h-4" />
            <span className="text-sm text-white/70">Completion</span>
          </div>
          <div className="text-4xl font-bold text-white">
            {completionPercentage}%
          </div>
        </motion.div>

        {/* Streak */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-2 text-pink-400">
            <Flame className="w-4 h-4" />
            <span className="text-sm text-white/70">Streak</span>
          </div>
          <div className="text-4xl font-bold text-white">{streakDays}d</div>
        </motion.div>
      </div>
    </div>
  )
}
