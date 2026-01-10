/**
 * Root layout component for Next.js 14 App Router.
 *
 * This layout wraps all pages and provides:
 * - Global providers (TanStack Query)
 * - Navigation header
 * - Sidebar (future)
 * - Global styles
 */

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Link from 'next/link';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Todo Chatbot',
  description: 'Intelligent task management with AI-powered assistance',
};

/**
 * Root layout component.
 *
 * Provides application structure with navigation and providers.
 *
 * @param props - Layout props
 * @returns Root layout
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-gray-50">
            {/* Navigation header */}
            <header className="bg-white border-b border-gray-200">
              <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                  <div className="flex">
                    {/* Logo */}
                    <Link
                      href="/"
                      className="flex items-center px-2 text-xl font-bold text-blue-600 hover:text-blue-700"
                    >
                      Todo Chatbot
                    </Link>

                    {/* Navigation links */}
                    <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                      <Link
                        href="/"
                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 border-b-2 border-blue-500 hover:border-blue-700"
                      >
                        Tasks
                      </Link>
                      <Link
                        href="/chat"
                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 border-b-2 border-transparent hover:border-gray-300 hover:text-gray-700"
                      >
                        Chat
                      </Link>
                      <Link
                        href="/calendar"
                        className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 border-b-2 border-transparent hover:border-gray-300 hover:text-gray-700"
                      >
                        Calendar
                      </Link>
                    </div>
                  </div>

                  {/* Right side navigation */}
                  <div className="flex items-center gap-4">
                    {/* Search bar placeholder - actual functionality in page components */}
                    <div className="hidden md:block w-64">
                      {/* Search component will be integrated at page level */}
                    </div>

                    {/* User menu (future) */}
                    <button
                      type="button"
                      className="p-2 rounded-full text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <span className="sr-only">User menu</span>
                      <svg
                        className="h-6 w-6"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              </nav>
            </header>

            {/* Main content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              {children}
            </main>

            {/* Footer */}
            <footer className="bg-white border-t border-gray-200 mt-auto">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <p className="text-center text-sm text-gray-500">
                  &copy; 2024 Todo Chatbot. Built with Next.js, FastAPI, and
                  Kafka.
                </p>
              </div>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}
