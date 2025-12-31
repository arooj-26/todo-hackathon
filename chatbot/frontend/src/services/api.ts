/**
 * API client service for communicating with the backend.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  userId: string;
  message: string;
  conversationId?: number | null;
}

/**
 * Send a message to the chat endpoint.
 */
export async function sendMessage(params: SendMessageParams): Promise<ChatResponse> {
  const { userId, message, conversationId } = params;

  const requestBody = {
    message,
    conversation_id: conversationId || null,
  };

  try {
    const response = await fetch(`${API_URL}/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
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
    console.error('API Error:', error);

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
 * Fetch conversation list for a user.
 */
export async function getConversations(userId: string) {
  try {
    const response = await fetch(`${API_URL}/api/${userId}/conversations`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return { conversations: [], count: 0 };
  }
}
