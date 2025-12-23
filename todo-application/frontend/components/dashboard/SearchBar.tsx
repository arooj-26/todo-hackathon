'use client'

import { Search } from 'lucide-react'
import { motion } from 'framer-motion'

interface SearchBarProps {
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
}

export default function SearchBar({
  value = '',
  onChange,
  placeholder = 'Search tasks...'
}: SearchBarProps) {
  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="relative"
    >
      <div className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40">
        <Search className="w-5 h-5" />
      </div>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        placeholder={placeholder}
        className="
          w-full pl-12 pr-4 py-3.5
          bg-white/5 border border-white/10
          rounded-2xl
          text-white placeholder:text-white/40
          focus:outline-none focus:border-purple-500/50 focus:bg-white/10
          transition-all duration-200
        "
      />
    </motion.div>
  )
}
