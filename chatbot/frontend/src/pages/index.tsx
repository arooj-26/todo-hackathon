/**
 * Main page for the Todo AI Chatbot
 */
'use client';

import React, { useState, useEffect } from 'react';
import ChatInterface from '../components/ChatInterface';

export default function Home() {
  const [userId, setUserId] = useState<string>('');

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
  }, []);

  if (!userId) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        <p>Loading...</p>
      </div>
    );
  }

  return <ChatInterface userId={userId} />;
}
