/**
 * Chatbot API client service for AI-powered task management
 */
import { getChatbotApiUrl } from '@/lib/config';

// Use runtime URL detection instead of build-time environment variable
function getChatbotUrl(): string {
  return getChatbotApiUrl();
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result: Record<string, any>;
}

export interface ChatResponse {
  conversation_id: number | null;
  response: string;
  tool_calls: ToolCall[];
  error: string | null;
}

export interface SendMessageParams {
  message: string;
  conversationId?: number | null;
}

/**
 * Send a message to the chatbot endpoint.
 * User ID is automatically extracted from JWT token on the backend.
 */
export async function sendChatMessage(params: SendMessageParams): Promise<ChatResponse> {
  const { message, conversationId } = params;

  const requestBody = {
    message,
    conversation_id: conversationId || null,
  };

  // Get JWT token from localStorage
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  if (!token) {
    return {
      conversation_id: conversationId || null,
      response: '',
      tool_calls: [],
      error: 'Not authenticated. Please log in.',
    };
  }

  try {
    const response = await fetch(`${getChatbotUrl()}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data: ChatResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Chatbot API Error:', error);

    // Return error response
    return {
      conversation_id: conversationId || null,
      response: '',
      tool_calls: [],
      error: error instanceof Error ? error.message : 'Failed to send message',
    };
  }
}

/**
 * Fetch conversation list for the authenticated user.
 * User ID is automatically extracted from JWT token.
 */
export async function getChatConversations() {
  // Get JWT token from localStorage
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  if (!token) {
    console.error('No authentication token found');
    return { conversations: [], count: 0 };
  }

  try {
    const response = await fetch(`${getChatbotUrl()}/api/conversations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Chatbot API Error:', error);
    return { conversations: [], count: 0 };
  }
}
