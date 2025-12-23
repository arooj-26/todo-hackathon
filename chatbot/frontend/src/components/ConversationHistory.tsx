/**
 * Conversation History Component
 *
 * Displays recent conversations for the user.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { getConversations } from '../services/api';

interface Conversation {
  id: string;
  created_at: string;
  updated_at: string;
}

interface ConversationHistoryProps {
  userId: string;
  onSelect: (conversationId: string) => void;
  currentConversationId: string | null;
}

export default function ConversationHistory({
  userId,
  onSelect,
  currentConversationId
}: ConversationHistoryProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadConversations();
  }, [userId]);

  const loadConversations = async () => {
    setIsLoading(true);
    try {
      const data = await getConversations(userId);
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="conversation-history">Loading...</div>;
  }

  return (
    <div className="conversation-history">
      <h3>Recent Conversations</h3>
      {conversations.length === 0 ? (
        <p className="empty-state">No previous conversations</p>
      ) : (
        <ul>
          {conversations.map((conv) => (
            <li
              key={conv.id}
              className={conv.id === currentConversationId ? 'active' : ''}
              onClick={() => onSelect(conv.id)}
            >
              <div className="conversation-date">
                {new Date(conv.updated_at).toLocaleString()}
              </div>
            </li>
          ))}
        </ul>
      )}

      <style jsx>{`
        .conversation-history {
          width: 250px;
          background: #f9f9f9;
          padding: 1rem;
          border-right: 1px solid #ddd;
          overflow-y: auto;
        }

        .conversation-history h3 {
          margin: 0 0 1rem 0;
          font-size: 1rem;
          color: #333;
        }

        .empty-state {
          color: #999;
          font-size: 0.9rem;
          text-align: center;
        }

        .conversation-history ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .conversation-history li {
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          background: white;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .conversation-history li:hover {
          background: #e3f2fd;
        }

        .conversation-history li.active {
          background: #4a90e2;
          color: white;
        }

        .conversation-date {
          font-size: 0.85rem;
        }
      `}</style>
    </div>
  );
}
