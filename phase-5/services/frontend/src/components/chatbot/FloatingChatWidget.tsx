/**
 * Floating Chat Widget - AI-Powered Task Assistant
 * Integrates chatbot functionality into the Todo application
 */
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Sparkles, RotateCcw } from 'lucide-react';
import { sendChatMessage, ChatMessage, ChatResponse } from '@/lib/api/chatbot/api';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface FloatingChatWidgetProps {
  userId?: number; // User ID to associate conversation with specific user
  onTasksUpdate?: () => void; // Callback to refresh tasks when chatbot creates/updates them
}

export default function FloatingChatWidget({ userId, onTasksUpdate }: FloatingChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Get user-specific localStorage key
  const getConversationKey = () => userId ? `chatbot_conversation_id_${userId}` : 'chatbot_conversation_id';

  // Load conversation ID from localStorage on mount or when userId changes
  useEffect(() => {
    if (userId) {
      const savedConversationId = localStorage.getItem(getConversationKey());
      if (savedConversationId) {
        const parsedId = parseInt(savedConversationId, 10);
        if (!isNaN(parsedId)) {
          setConversationId(parsedId);
        } else {
          setConversationId(null);
        }
      } else {
        setConversationId(null);
      }
    }
  }, [userId]);

  // Save conversation ID to localStorage when it changes
  useEffect(() => {
    if (userId && conversationId !== null) {
      localStorage.setItem(getConversationKey(), conversationId.toString());
    }
  }, [conversationId, userId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue,
    };

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response: ChatResponse = await sendChatMessage({
        message: inputValue,
        conversationId,
      });

      if (response.error) {
        // If conversation not found, clear stale conversation_id and retry
        if (response.error.includes('Conversation not found')) {
          console.log('⚠️ Stale conversation detected, clearing and starting new conversation...');
          localStorage.removeItem(getConversationKey());
          setConversationId(null);

          // Retry with new conversation
          const retryResponse: ChatResponse = await sendChatMessage({
            message: inputValue,
            conversationId: null,
          });

          if (retryResponse.error) {
            setError(retryResponse.error);
            return;
          }

          // Handle successful retry response
          if (retryResponse.conversation_id) {
            setConversationId(retryResponse.conversation_id);
          }

          const assistantMessage: ChatMessage = {
            role: 'assistant',
            content: retryResponse.response,
          };
          setMessages(prev => [...prev, assistantMessage]);

          if (retryResponse.tool_calls && retryResponse.tool_calls.length > 0) {
            console.log('✅ Triggering task refresh...');
            if (onTasksUpdate) {
              onTasksUpdate();
            }
          }
          return;
        }

        // Other errors
        setError(response.error);
        return;
      }

      // Update conversation ID if new
      if (response.conversation_id && response.conversation_id !== conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
      };
      setMessages(prev => [...prev, assistantMessage]);

      // If chatbot performed task operations, refresh the task list
      console.log('🤖 Chatbot response:', response);
      console.log('🔧 Tool calls:', response.tool_calls);
      console.log('🔄 onTasksUpdate exists?', !!onTasksUpdate);

      if (response.tool_calls && response.tool_calls.length > 0) {
        console.log('✅ Triggering task refresh...');
        if (onTasksUpdate) {
          onTasksUpdate();
        }
      } else {
        console.log('⚠️ No tool calls found, dashboard will not refresh');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewConversation = () => {
    setConversationId(null);
    setMessages([]);
    if (userId) {
      localStorage.removeItem(getConversationKey());
    }
    setError(null);
  };

  return (
    <>
      {/* Floating Chat Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            className="fixed bottom-6 right-6 z-50"
          >
            <Button
              onClick={() => setIsOpen(true)}
              className="h-14 w-14 rounded-full shadow-lg bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 group"
              size="icon"
            >
              <MessageCircle className="w-6 h-6 group-hover:scale-110 transition-transform" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-green-500 rounded-full border-2 border-white"></span>
            </Button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 z-50 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-200"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="text-white font-semibold text-lg">AI Task Assistant</h3>
                  <p className="text-purple-100 text-xs">Powered by AI</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleNewConversation}
                  className="text-white hover:bg-white/20 h-8 w-8"
                  title="New Conversation"
                >
                  <RotateCcw className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:bg-white/20 h-8 w-8"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Sparkles className="w-8 h-8 text-purple-600" />
                  </div>
                  <h4 className="text-gray-900 font-semibold mb-2">Welcome! I'm your AI assistant</h4>
                  <p className="text-gray-600 text-sm mb-4">I can help you manage your tasks naturally.</p>
                  <div className="text-left bg-white rounded-lg p-4 space-y-2">
                    <p className="text-xs font-semibold text-gray-700 mb-2">Try saying:</p>
                    <div className="space-y-1.5">
                      <div className="text-xs text-purple-600 bg-purple-50 rounded px-3 py-1.5">
                        "Add buy groceries to my list"
                      </div>
                      <div className="text-xs text-purple-600 bg-purple-50 rounded px-3 py-1.5">
                        "Show me all my tasks"
                      </div>
                      <div className="text-xs text-purple-600 bg-purple-50 rounded px-3 py-1.5">
                        "Mark the first task as done"
                      </div>
                      <div className="text-xs text-purple-600 bg-purple-50 rounded px-3 py-1.5">
                        "Delete the meeting task"
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={cn(
                    "flex",
                    message.role === 'user' ? "justify-end" : "justify-start"
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[80%] rounded-2xl px-4 py-2.5",
                      message.role === 'user'
                        ? "bg-purple-600 text-white"
                        : "bg-white text-gray-900 border border-gray-200"
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  </div>
                </motion.div>
              ))}

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-purple-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </motion.div>
              )}

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-red-800 text-sm">
                    <strong>Error:</strong> {error}
                  </p>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Container */}
            <div className="p-4 bg-white border-t border-gray-200">
              <div className="flex gap-2">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading}
                  rows={1}
                  className="flex-1 resize-none rounded-lg border border-gray-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputValue.trim()}
                  className="bg-purple-600 hover:bg-purple-700 h-10 w-10 p-0"
                  size="icon"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
