/**
 * Chat Interface Component
 *
 * Provides the main conversational UI for task management.
 */
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { sendMessage, ChatMessage, ChatResponse } from '../services/api';

interface ChatInterfaceProps {
  userId: string;
}

export default function ChatInterface({ userId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation ID from localStorage on mount
  useEffect(() => {
    const savedConversationId = localStorage.getItem('conversation_id');
    if (savedConversationId) {
      setConversationId(savedConversationId);
    }
  }, []);

  // Save conversation ID to localStorage when it changes
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem('conversation_id', conversationId);
    }
  }, [conversationId]);

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
      const response: ChatResponse = await sendMessage({
        userId,
        message: inputValue,
        conversationId,
      });

      if (response.error) {
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
    localStorage.removeItem('conversation_id');
    setError(null);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>Todo AI Assistant</h1>
        <button onClick={handleNewConversation} className="new-conversation-btn">
          New Conversation
        </button>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome! I'm your task management assistant.</h2>
            <p>Try saying:</p>
            <ul>
              <li>"Add buy groceries to my list"</li>
              <li>"Show me all my tasks"</li>
              <li>"Mark the first task as done"</li>
              <li>"Delete the meeting task"</li>
            </ul>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            <div className="message-role">{message.role === 'user' ? 'You' : 'Assistant'}</div>
            <div className="message-content">{message.content}</div>
          </div>
        ))}

        {isLoading && (
          <div className="message assistant">
            <div className="message-role">Assistant</div>
            <div className="message-content loading">
              <span className="loading-dots">●●●</span>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          disabled={isLoading}
          rows={3}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>

      <style jsx>{`
        .chat-interface {
          display: flex;
          flex-direction: column;
          height: 100vh;
          max-width: 800px;
          margin: 0 auto;
          background: #f5f5f5;
        }

        .chat-header {
          background: #4a90e2;
          color: white;
          padding: 1rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .chat-header h1 {
          margin: 0;
          font-size: 1.5rem;
        }

        .new-conversation-btn {
          background: white;
          color: #4a90e2;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }

        .new-conversation-btn:hover {
          background: #f0f0f0;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          background: white;
        }

        .welcome-message {
          text-align: center;
          color: #666;
          padding: 2rem;
        }

        .welcome-message h2 {
          color: #333;
          margin-bottom: 1rem;
        }

        .welcome-message ul {
          text-align: left;
          display: inline-block;
          margin-top: 1rem;
        }

        .welcome-message li {
          margin: 0.5rem 0;
          color: #4a90e2;
        }

        .message {
          margin-bottom: 1rem;
          padding: 0.75rem;
          border-radius: 8px;
        }

        .message.user {
          background: #e3f2fd;
          margin-left: 20%;
        }

        .message.assistant {
          background: #f5f5f5;
          margin-right: 20%;
        }

        .message-role {
          font-weight: 600;
          font-size: 0.85rem;
          color: #666;
          margin-bottom: 0.25rem;
        }

        .message-content {
          line-height: 1.5;
          white-space: pre-wrap;
        }

        .loading-dots {
          animation: loading 1.4s infinite;
        }

        @keyframes loading {
          0%, 60%, 100% { opacity: 1; }
          30% { opacity: 0.3; }
        }

        .error-message {
          background: #ffebee;
          color: #c62828;
          padding: 1rem;
          border-radius: 4px;
          margin: 1rem 0;
        }

        .input-container {
          padding: 1rem;
          background: white;
          border-top: 1px solid #ddd;
          display: flex;
          gap: 0.5rem;
        }

        .input-container textarea {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-family: inherit;
          font-size: 1rem;
          resize: none;
        }

        .input-container textarea:focus {
          outline: none;
          border-color: #4a90e2;
        }

        .input-container button {
          background: #4a90e2;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }

        .input-container button:hover:not(:disabled) {
          background: #357abd;
        }

        .input-container button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}
