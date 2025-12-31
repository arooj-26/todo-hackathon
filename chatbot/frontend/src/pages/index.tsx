/**
 * Main page for the Todo AI Dashboard with ChatKit
 */
'use client';

import React, { useState, useEffect } from 'react';
import Dashboard from '../components/Dashboard';
import { getChatKitConfig } from '../lib/chatkit-config';

export default function Home() {
  const [userId, setUserId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // Get ChatKit configuration
  const chatKitConfig = getChatKitConfig();

  // Get or create user ID
  useEffect(() => {
    let savedUserId = localStorage.getItem('user_id');
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

    if (!savedUserId || !uuidRegex.test(savedUserId)) {
      // Generate a simple UUID v4
      savedUserId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
      localStorage.setItem('user_id', savedUserId);
    }

    setUserId(savedUserId);
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <div style={{
          fontSize: '3rem',
          marginBottom: '1rem',
          animation: 'pulse 2s infinite'
        }}>
          📋
        </div>
        <p style={{ fontSize: '1.25rem', fontWeight: 500 }}>
          Loading Todo AI Dashboard...
        </p>
        {chatKitConfig.enabled && (
          <p style={{ fontSize: '0.875rem', opacity: 0.9, marginTop: '0.5rem' }}>
            ChatKit integration enabled
          </p>
        )}
        <style>{`
          @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
          }
        `}</style>
      </div>
    );
  }

  return <Dashboard userId={userId} />;
}
