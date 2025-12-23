'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, Calendar, CalendarDays, Flag, ListTodo } from 'lucide-react'

interface Category {
  id: string
  name: string
  count: number
  icon: React.ReactNode
  color: string
  bgColor: string
}

interface CategorySidebarProps {
  activeCategory?: string
  onCategoryChange?: (categoryId: string) => void
  categories?: Category[]
}

const defaultCategories: Category[] = [
  {
    id: 'all',
    name: 'All Tasks',
    count: 32,
    icon: <ListTodo className="w-5 h-5" />,
    color: 'text-purple-400',
    bgColor: 'bg-purple-500'
  },
  {
    id: 'important',
    name: 'Important',
    count: 8,
    icon: <Flag className="w-5 h-5" />,
    color: 'text-pink-400',
    bgColor: 'bg-pink-500'
  },
  {
    id: 'today',
    name: 'Today',
    count: 5,
    icon: <Calendar className="w-5 h-5" />,
    color: 'text-cyan-400',
    bgColor: 'bg-cyan-500'
  },
  {
    id: 'week',
    name: 'This Week',
    count: 12,
    icon: <CalendarDays className="w-5 h-5" />,
    color: 'text-purple-400',
    bgColor: 'bg-purple-600'
  },
  {
    id: 'completed',
    name: 'Completed',
    count: 47,
    icon: <CheckCircle2 className="w-5 h-5" />,
    color: 'text-emerald-400',
    bgColor: 'bg-emerald-500'
  }
]

export default function CategorySidebar({
  activeCategory = 'all',
  onCategoryChange,
  categories = defaultCategories
}: CategorySidebarProps) {
  return (
    <div className="h-full flex flex-col">
      {/* Categories Section */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-6">Categories</h2>
        <div className="space-y-2">
          {categories.map((category, index) => {
            const isActive = activeCategory === category.id
            return (
              <motion.button
                key={category.id}
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => onCategoryChange?.(category.id)}
                className={`
                  w-full flex items-center justify-between px-4 py-3 rounded-xl
                  transition-all duration-200 group
                  ${
                    isActive
                      ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg'
                      : 'text-gray-300 hover:bg-white/5'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  <span className={isActive ? 'text-white' : category.color}>{category.icon}</span>
                  <span className="font-semibold">{category.name}</span>
                </div>

                {/* Count Badge */}
                <span
                  className={`
                    px-3 py-1 rounded-full text-sm font-bold
                    ${
                      isActive
                        ? 'bg-white/20 text-white'
                        : `${category.bgColor}/20 ${category.color}`
                    }
                  `}
                >
                  {category.count}
                </span>
              </motion.button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
