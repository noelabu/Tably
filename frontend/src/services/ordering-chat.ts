import { apiService } from './api';

export interface ChatMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export interface ChatRequest {
  message: string;
  context?: string;
  business_id?: string;
}

export interface ChatResponse {
  response: string;
  request_id: string;
  timestamp: string;
  agent_type: string;
}

export interface StreamingChatResponse {
  content: string;
  type: 'message' | 'done' | 'error';
  error?: string;
}

export class OrderingChatService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async sendMessage(message: string, context?: string, businessId?: string): Promise<ChatResponse> {
    const request: ChatRequest = {
      message,
      context,
      business_id: businessId
    };

    return apiService.withAuth(this.token).post<ChatResponse>('/api/v1/ordering/chat', request);
  }

  async *streamMessage(message: string, context?: string, businessId?: string): AsyncGenerator<StreamingChatResponse, void, unknown> {
    const request: ChatRequest = {
      message,
      context,
      business_id: businessId
    };

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ordering/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response body');
      }

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data.trim()) {
              try {
                const parsed = JSON.parse(data) as StreamingChatResponse;
                yield parsed;
                
                if (parsed.type === 'done' || parsed.type === 'error') {
                  return;
                }
              } catch (e) {
                console.error('Error parsing streaming response:', e);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      yield {
        content: 'Sorry, there was an error processing your request.',
        type: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  async getSupportedLanguages() {
    return apiService.withAuth(this.token).get('/api/v1/ordering/supported-languages');
  }

  async getOrderFlowHelp() {
    return apiService.withAuth(this.token).get('/api/v1/ordering/order-flow-help');
  }
}