'use client'

import { User, Menu, LogOut } from 'lucide-react'
import { motion } from 'framer-motion'

interface DashboardHeaderProps {
  userName?: string
  onMenuClick?: () => void
  onSignOut?: () => void
}

export default function DashboardHeader({
  userName = 'John Doe',
  onMenuClick,
  onSignOut
}: DashboardHeaderProps) {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-700 border-b border-white/10"
    >
      {/* Left: Menu + Logo */}
      <div className="flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onMenuClick}
          className="p-2 text-white hover:bg-white/10 rounded-lg transition-colors"
          aria-label="Toggle menu"
        >
          <Menu className="w-6 h-6" />
        </motion.button>

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center flex-shrink-0">
            <svg
              className="w-4 h-4 text-white flex-shrink-0"
              width="16"
              height="16"
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
          <h1 className="text-2xl font-bold text-white">TodoFlow</h1>
        </div>
      </div>

      {/* Right: User Profile + Sign Out */}
      <div className="flex items-center gap-3">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-3 px-5 py-2.5 rounded-full border-2 border-white/30 bg-white/10 hover:bg-white/20 transition-all text-white"
        >
          <User className="w-5 h-5" />
          <span className="font-medium">{userName}</span>
        </motion.button>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onSignOut}
          className="p-2.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 transition-all"
          title="Sign Out"
        >
          <LogOut className="w-5 h-5" />
        </motion.button>
      </div>
    </motion.header>
  )
}
