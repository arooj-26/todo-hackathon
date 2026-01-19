/**
 * Landing Page - TodoFlow
 * Welcome page with feature cards and sign in/up options
 */
'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  CheckSquare, MessageSquare, Repeat, Bell, TrendingUp, Cloud,
  Users, Zap, Calendar, Target, Shield, Sparkles
} from 'lucide-react'

export default function LandingPage() {
  const features = [
    {
      title: 'AI-Powered Chatbot',
      description: 'Interact with your tasks naturally using our intelligent chatbot. Just chat to create, update, or search tasks.',
      icon: MessageSquare,
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Recurring Tasks',
      description: 'Set up tasks that repeat daily, weekly, monthly, or with custom patterns. Never miss a routine task again.',
      icon: Repeat,
      gradient: 'from-blue-500 to-indigo-500',
    },
    {
      title: 'Smart Reminders',
      description: 'Get notified at the right time with flexible reminder options. Never forget important deadlines.',
      icon: Bell,
      gradient: 'from-pink-500 to-rose-500',
    },
    {
      title: 'Priority Management',
      description: 'Organize tasks by priority levels (High, Medium, Low) to focus on what matters most.',
      icon: Target,
      gradient: 'from-indigo-500 to-purple-500',
    },
    {
      title: 'Real-time Sync',
      description: 'Built on Kafka and Dapr for scalable, event-driven task updates across your team.',
      icon: Users,
      gradient: 'from-blue-600 to-cyan-500',
    },
    {
      title: 'Cloud-Native',
      description: 'Deployed on Kubernetes with microservices architecture for reliability and scalability.',
      icon: Cloud,
      gradient: 'from-purple-600 to-blue-600',
    },
  ]

  const stats = [
    { label: 'Tasks Managed', value: '10k+', gradient: 'from-pink-400 to-purple-400' },
    { label: 'Uptime', value: '99.9%', gradient: 'from-purple-400 to-blue-400' },
    { label: 'AI Assistant', value: '24/7', gradient: 'from-blue-400 to-cyan-400' },
  ]

  const technologies = [
    'Kubernetes', 'Dapr', 'Apache Kafka', 'PostgreSQL',
    'Next.js', 'FastAPI', 'Docker', 'Microservices'
  ]

  return (
    <div style={{
      minHeight: '100vh',
      position: 'relative',
      background: 'linear-gradient(135deg, rgb(88 28 135) 0%, rgb(109 40 217) 50%, rgb(29 78 216) 100%)'
    }}>
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* Logo */}
            <div className="flex justify-center mb-6">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-2xl">
                <CheckSquare className="w-12 h-12 text-white" strokeWidth={2.5} />
              </div>
            </div>

            <h1 className="text-5xl md:text-6xl font-extrabold text-white mb-6">
              Manage Tasks with
              <span className="block bg-gradient-to-r from-pink-400 to-purple-300 bg-clip-text text-transparent mt-2">
                AI-Powered Intelligence
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-white/80 mb-8 max-w-3xl mx-auto">
              The modern todo app that understands you. Chat naturally, set recurring tasks, and never miss a deadline.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/auth/signup">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="btn-gradient-pink w-full sm:w-auto px-8 py-4 text-white font-semibold rounded-xl shadow-lg"
                >
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Get Started Free
                  </span>
                </motion.button>
              </Link>
              <Link href="/auth/signin">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="w-full sm:w-auto px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-semibold rounded-xl border-2 border-white/20 hover:bg-white/20 transition-all"
                >
                  Sign In
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold text-white mb-4">
            Powerful Features for Modern Task Management
          </h2>
          <p className="text-xl text-white/70">
            Everything you need to stay organized and productive
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="card-dark p-6 space-y-4 cursor-pointer"
            >
              {/* Icon */}
              <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${feature.gradient} text-white shadow-lg`}>
                <feature.icon className="w-8 h-8" strokeWidth={2} />
              </div>

              {/* Title */}
              <h3 className="text-xl font-bold text-white">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-white/60 leading-relaxed text-sm">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="glass-dark rounded-2xl p-12"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center text-white">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="space-y-2"
              >
                <div className={`text-5xl font-bold bg-gradient-to-r ${stat.gradient} bg-clip-text text-transparent`}>
                  {stat.value}
                </div>
                <div className="text-lg text-white/70">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Tech Stack Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-bold text-white mb-4">
            Built with Modern Technologies
          </h2>
          <p className="text-xl text-white/70">
            Enterprise-grade architecture for reliability and performance
          </p>
        </motion.div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {technologies.map((tech, index) => (
            <motion.div
              key={tech}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
              viewport={{ once: true }}
              whileHover={{ scale: 1.05, borderColor: 'rgba(255, 255, 255, 0.3)' }}
              className="flex items-center justify-center p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 transition-all duration-200"
            >
              <span className="text-sm font-semibold text-white">{tech}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to supercharge your productivity?
          </h2>
          <p className="text-xl text-white/70 mb-8">
            Join thousands of users managing their tasks smarter with AI
          </p>
          <Link href="/auth/signup">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-gradient-pink px-10 py-5 text-white text-lg font-semibold rounded-xl shadow-2xl"
            >
              <span className="flex items-center gap-2">
                <Zap className="w-6 h-6" />
                Start Free Today
              </span>
            </motion.button>
          </Link>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="text-center py-8 text-white/50 text-sm border-t border-white/10">
        © 2024 TodoFlow. Built with Next.js, FastAPI, Kafka & Kubernetes.
      </div>
    </div>
  )
}
