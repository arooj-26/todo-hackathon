/**
 * Landing Page - TodoFlow Theme (Dark Purple/Pink Gradient)
 * Welcome page with feature showcase and auth options
 * Shows dashboard for authenticated users
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import FloatingChatWidget from '@/components/chatbot/FloatingChatWidget';
import { useAuthContext } from '@/components/auth/AuthProvider';
import { TaskList } from '@/components/TaskList';
import { TaskForm } from '@/components/TaskForm';
import { useTasks, type TaskCreate } from '@/hooks/useTasks';

export default function LandingPage() {
  const [isSignUpOpen, setIsSignUpOpen] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const { user, isAuthenticated, isLoading, signOut } = useAuthContext();
  const { createTask, isCreating } = useTasks();

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{
        background: 'linear-gradient(135deg, rgb(88 28 135) 0%, rgb(109 40 217) 50%, rgb(29 78 216) 100%)'
      }}>
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // Show Dashboard for authenticated users
  if (isAuthenticated && user) {
    return (
      <div className="min-h-screen" style={{
        background: 'linear-gradient(135deg, rgb(88 28 135) 0%, rgb(109 40 217) 50%, rgb(29 78 216) 100%)'
      }}>
        {/* Header */}
        <header className="border-b border-white/10 backdrop-blur-sm bg-white/5">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg">
                  <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24" className="text-white">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
                <h1 className="text-xl font-bold text-white">TodoFlow</h1>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-white/70 text-sm">{user.email}</span>
                <button
                  onClick={() => signOut()}
                  className="px-4 py-2 text-sm text-white/80 hover:text-white border border-white/20 rounded-lg hover:bg-white/10 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome & Add Task */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-white">Welcome back!</h2>
              <p className="text-white/60 mt-1">Manage your tasks and stay productive</p>
            </div>
            <button
              onClick={() => setShowTaskForm(!showTaskForm)}
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-xl hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg"
            >
              {showTaskForm ? 'Hide Form' : '+ New Task'}
            </button>
          </div>

          {/* Task Form */}
          {showTaskForm && (
            <div className="mb-8 p-6 rounded-2xl backdrop-blur-lg bg-white/10 border border-white/20">
              <h3 className="text-xl font-semibold text-white mb-4">Create New Task</h3>
              <TaskForm
                onSubmit={(task: TaskCreate) => {
                  createTask(task, {
                    onSuccess: () => setShowTaskForm(false)
                  });
                }}
                onCancel={() => setShowTaskForm(false)}
                isLoading={isCreating}
              />
            </div>
          )}

          {/* Task List */}
          <div className="rounded-2xl backdrop-blur-lg bg-white/10 border border-white/20 p-6">
            <TaskList />
          </div>
        </main>

        {/* Chatbot Widget */}
        <FloatingChatWidget />
      </div>
    );
  }

  const features = [
    {
      title: 'AI-Powered Chatbot',
      description: 'Interact with your tasks naturally using our intelligent chatbot. Just chat to create, update, or search tasks.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      gradient: 'from-purple-500 to-pink-500',
    },
    {
      title: 'Recurring Tasks',
      description: 'Set up tasks that repeat daily, weekly, monthly, or with custom patterns. Never miss a routine task again.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      ),
      gradient: 'from-blue-500 to-indigo-500',
    },
    {
      title: 'Smart Reminders',
      description: 'Get notified at the right time with flexible reminder options. Never forget important deadlines.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      ),
      gradient: 'from-pink-500 to-rose-500',
    },
    {
      title: 'Priority Management',
      description: 'Organize tasks by priority levels (High, Medium, Low) to focus on what matters most.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      gradient: 'from-indigo-500 to-purple-500',
    },
    {
      title: 'Real-time Sync',
      description: 'Built on Kafka and Dapr for scalable, event-driven task updates across your team.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
      gradient: 'from-blue-600 to-cyan-500',
    },
    {
      title: 'Cloud-Native',
      description: 'Deployed on Kubernetes with microservices architecture for reliability and scalability.',
      icon: (
        <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
        </svg>
      ),
      gradient: 'from-purple-600 to-blue-600',
    },
  ];

  return (
    <div style={{
      minHeight: '100vh',
      position: 'relative',
      background: 'linear-gradient(135deg, rgb(88 28 135) 0%, rgb(109 40 217) 50%, rgb(29 78 216) 100%)'
    }}>
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            {/* Logo */}
            <div className="flex justify-center mb-6">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-2xl">
                <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24" className="text-white">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
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
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={() => setIsSignUpOpen(true)}
                className="btn-gradient-pink w-full sm:w-auto px-8 py-4 text-white font-semibold rounded-xl transform hover:scale-105 transition-all duration-200"
              >
                Get Started Free
              </button>
              <Link
                href="/auth/signin"
                className="w-full sm:w-auto px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-semibold rounded-xl border-2 border-white/20 hover:bg-white/20 transform hover:scale-105 transition-all duration-200 text-center"
              >
                Sign In
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-white mb-4">
            Powerful Features for Modern Task Management
          </h2>
          <p className="text-xl text-white/70">
            Everything you need to stay organized and productive
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="card-dark p-6 space-y-4 hover:scale-105 transition-transform duration-300"
            >
              {/* Icon */}
              <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${feature.gradient} text-white shadow-lg`}>
                {feature.icon}
              </div>

              {/* Title */}
              <h3 className="text-xl font-bold text-white">
                {feature.title}
              </h3>

              {/* Description */}
              <p className="text-white/60 leading-relaxed text-sm">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Stats Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="glass-dark rounded-2xl p-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center text-white">
            <div className="space-y-2">
              <div className="text-5xl font-bold bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text text-transparent">10k+</div>
              <div className="text-lg text-white/70">Tasks Managed</div>
            </div>
            <div className="space-y-2">
              <div className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">99.9%</div>
              <div className="text-lg text-white/70">Uptime</div>
            </div>
            <div className="space-y-2">
              <div className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">24/7</div>
              <div className="text-lg text-white/70">AI Assistant</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tech Stack Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">
            Built with Modern Technologies
          </h2>
          <p className="text-xl text-white/70">
            Enterprise-grade architecture for reliability and performance
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {['Kubernetes', 'Dapr', 'Apache Kafka', 'PostgreSQL', 'Next.js', 'FastAPI', 'Docker', 'Microservices'].map((tech) => (
            <div
              key={tech}
              className="flex items-center justify-center p-4 bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all duration-200"
            >
              <span className="text-sm font-semibold text-white">{tech}</span>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-bold text-white mb-6">
          Ready to supercharge your productivity?
        </h2>
        <p className="text-xl text-white/70 mb-8">
          Join thousands of users managing their tasks smarter with AI
        </p>
        <button
          onClick={() => setIsSignUpOpen(true)}
          className="btn-gradient-pink px-10 py-5 text-white text-lg font-semibold rounded-xl transform hover:scale-105 transition-all duration-200"
        >
          Start Free Today
        </button>
      </div>

      {/* Footer */}
      <div className="text-center py-8 text-white/50 text-sm border-t border-white/10">
        © 2024 TodoFlow. Built with Next.js, FastAPI, Kafka & Kubernetes.
      </div>

      {/* Sign Up Modal */}
      {isSignUpOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="card-dark max-w-md w-full p-8 relative">
            <button
              onClick={() => setIsSignUpOpen(false)}
              className="absolute top-4 right-4 text-white/60 hover:text-white"
            >
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="text-center mb-6">
              <div className="w-14 h-14 mx-auto rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg mb-4">
                <svg width="28" height="28" fill="none" stroke="currentColor" viewBox="0 0 24 24" className="text-white">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">
                Welcome to TodoFlow
              </h2>
              <p className="text-white/60">
                Sign up to start managing your tasks
              </p>
            </div>

            <div className="space-y-4">
              <input
                type="email"
                placeholder="Email address"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all"
              />
              <input
                type="password"
                placeholder="Password"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all"
              />
              <button className="btn-gradient-pink w-full py-3 rounded-lg font-semibold text-white transform hover:scale-105 transition-all duration-200">
                Create Account
              </button>

              <p className="text-center text-sm text-white/60">
                Already have an account?{' '}
                <Link href="/auth/signin" className="font-semibold text-purple-400 hover:text-pink-400 transition-colors">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Chatbot Widget */}
      <FloatingChatWidget />
    </div>
  );
}
