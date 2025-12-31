/**
 * Chat Interface Component using OpenAI ChatKit Web Component
 *
 * Provides the main conversational UI for task management with OpenAI ChatKit integration.
 */
'use client';

import React, { useState, useEffect, useRef } from 'react';
import type { OpenAIChatKit, ChatKitOptions } from '@openai/chatkit';
import { sendMessage, ChatMessage, ChatResponse } from '../services/api';
import { getChatKitConfig, getTaskSuggestions, formatChatKitError } from '../lib/chatkit-config';

// Extend JSX to include the openai-chatkit custom element
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'openai-chatkit': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    }
  }
}

interface ChatInterfaceProps {
  userId: string;
}

export default function ChatInterface({ userId }: ChatInterfaceProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatkitRef = useRef<OpenAIChatKit | null>(null);

  // ChatKit configuration
  const chatKitConfig = getChatKitConfig();
  const hasValidDomainKey = chatKitConfig.enabled;
  const suggestions = getTaskSuggestions();

  const handleNewConversation = () => {
    const chatkit = chatkitRef.current;
    if (chatkit) {
      chatkit.setThreadId(null);
    }
    setError(null);
  };

  // SECURITY FIX: Reset conversation state when userId changes
  // This prevents conversation leakage between different user accounts
  useEffect(() => {
    const chatkit = chatkitRef.current;
    if (chatkit && chatkit.setThreadId) {
      // Clear any existing thread/conversation ID when switching users
      chatkit.setThreadId(null);
      setError(null);
    }
  }, [userId]); // Run whenever userId changes

  // Initialize ChatKit when component mounts
  useEffect(() => {
    if (!hasValidDomainKey) return;

    const initChatKit = () => {
      const chatkitElement = document.getElementById('chatkit-instance') as OpenAIChatKit | null;
      if (!chatkitElement || !chatkitElement.setOptions) {
        setTimeout(initChatKit, 100);
        return;
      }

      // CRITICAL: Reset thread ID when userId changes to prevent conversation leakage between accounts
      // This ensures each user starts with a fresh conversation state
      chatkitElement.setThreadId(null);

      chatkitRef.current = chatkitElement;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

      const options: ChatKitOptions = {
        api: {
          url: `${apiUrl}/api/${userId}/chatkit`,
          domainKey: chatKitConfig.domainKey,
        },
        theme: {
          colorScheme: 'light',
          radius: 'round',
          density: 'normal',
          color: {
            accent: {
              primary: chatKitConfig.theme.primaryColor,
              level: 2,
            },
          },
        },
        startScreen: {
          greeting: 'What tasks can I help you with today?',
          prompts: suggestions.slice(0, 4).map(s => ({
            label: s,
            prompt: s,
            icon: 'write',
          })),
        },
        composer: {
          placeholder: 'Ask me to manage your tasks...',
        },
        header: {
          enabled: false, // We use custom header
        },
      };

      chatkitElement.setOptions(options);

      // Handle events
      chatkitElement.addEventListener('chatkit.ready', () => {
        console.log('ChatKit ready');
      });

      chatkitElement.addEventListener('chatkit.error', (event) => {
        setError(formatChatKitError(event.detail.error));
      });

      chatkitElement.addEventListener('chatkit.response.start', () => {
        setIsLoading(true);
      });

      chatkitElement.addEventListener('chatkit.response.end', () => {
        setIsLoading(false);
      });
    };

    // Wait for custom element to be defined
    if (customElements.get('openai-chatkit')) {
      initChatKit();
    } else {
      customElements.whenDefined('openai-chatkit').then(initChatKit);
    }
  }, [hasValidDomainKey, userId, chatKitConfig, suggestions]);

  // Show configuration message if ChatKit is not set up
  if (!hasValidDomainKey) {
    return (
      <div className="chatkit-container">
        <div className="chat-header">
          <h1>Todo AI Dashboard</h1>
        </div>

        <div className="config-message">
          <div className="config-card">
            <h2>🔑 ChatKit Configuration Required</h2>
            <p>To use the Todo AI Dashboard, you need to configure your OpenAI ChatKit domain key.</p>

            <div className="config-steps">
              <h3>Quick Setup:</h3>
              <ol>
                <li>
                  <strong>Get Domain Key:</strong>
                  <br />
                  Visit <a href="https://platform.openai.com/settings/organization/security/domain-allowlist" target="_blank" rel="noopener noreferrer">
                    OpenAI Platform
                  </a> and add your domain (e.g., <code>localhost:3000</code>)
                </li>
                <li>
                  <strong>Copy the key</strong> provided by OpenAI
                </li>
                <li>
                  <strong>Configure .env.local:</strong>
                  <br />
                  <code>NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key-here</code>
                </li>
                <li>
                  <strong>Restart</strong> the development server
                </li>
              </ol>
            </div>

            <div className="config-docs">
              <p>
                📚 See <strong>CHATKIT_QUICKSTART.md</strong> for detailed instructions
              </p>
            </div>
          </div>
        </div>

        <style jsx>{`
          .chatkit-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          .chat-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            color: white;
            padding: 1.25rem 2rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          }

          .chat-header h1 {
            margin: 0;
            font-size: 1.75rem;
            font-weight: 600;
          }

          .config-message {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
          }

          .config-card {
            background: white;
            border-radius: 12px;
            padding: 3rem;
            max-width: 600px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
          }

          .config-card h2 {
            color: #333;
            margin: 0 0 1rem 0;
            font-size: 1.5rem;
          }

          .config-card p {
            color: #666;
            line-height: 1.6;
            margin: 0 0 1.5rem 0;
          }

          .config-steps {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
          }

          .config-steps h3 {
            margin: 0 0 1rem 0;
            color: #333;
            font-size: 1.1rem;
          }

          .config-steps ol {
            margin: 0;
            padding-left: 1.5rem;
          }

          .config-steps li {
            margin: 1rem 0;
            color: #555;
            line-height: 1.8;
          }

          .config-steps code {
            background: #e9ecef;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
            color: #d63384;
          }

          .config-steps a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
          }

          .config-steps a:hover {
            text-decoration: underline;
          }

          .config-docs {
            text-align: center;
            padding: 1rem;
            background: #e7f3ff;
            border-radius: 8px;
          }

          .config-docs p {
            margin: 0;
            color: #0066cc;
          }

          .config-docs strong {
            font-weight: 600;
          }
        `}</style>
      </div>
    );
  }

  // Render ChatKit
  return (
    <div className="chatkit-container">
      <div className="chat-header">
        <h1>Todo AI Dashboard</h1>
        <div className="header-actions">
          <button onClick={handleNewConversation} className="new-conversation-btn">
            New Conversation
          </button>
        </div>
      </div>

      <div className="chatkit-wrapper">
        <openai-chatkit id="chatkit-instance" />

        {error && (
          <div className="chatkit-error">
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>

        <style jsx>{`
          .chatkit-container {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 1200px;
            margin: 0 auto;
            background: #f5f5f5;
          }

          .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.25rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          }

          .chat-header h1 {
            margin: 0;
            font-size: 1.75rem;
            font-weight: 600;
          }

          .header-actions {
            display: flex;
            gap: 0.75rem;
          }

          .new-conversation-btn,
          .toggle-view-btn {
            background: white;
            color: #667eea;
            border: none;
            padding: 0.625rem 1.25rem;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
          }

          .new-conversation-btn:hover,
          .toggle-view-btn:hover {
            background: #f8f9fa;
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }

          .chatkit-wrapper {
            flex: 1;
            position: relative;
            background: white;
            overflow: hidden;
            display: flex;
            flex-direction: column;
          }

          #chatkit-instance,
          openai-chatkit {
            width: 100%;
            height: 100%;
            display: block;
          }

          .chatkit-error {
            position: absolute;
            bottom: 1rem;
            left: 50%;
            transform: translateX(-50%);
            background: #ffebee;
            color: #c62828;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            max-width: 90%;
          }
        `}</style>
    </div>
  );
}
