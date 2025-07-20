import { apiService, ApiError } from './api';

export interface VoiceSession {
  session_id: string;
  business_id: string;
  websocket_url: string;
  message: string;
  instructions: {
    websocket: string;
    audio_format: string;
    stop_session: string;
    manual_stop: string;
  };
}

export interface VoiceSessionRequest {
  business_id: string;
  debug?: boolean;
}

export interface VoiceSessionInfo {
  session_id: string;
  business_id: string;
  created_at: string;
  debug: boolean;
  status: string;
  websocket_url: string;
}

export interface AudioChunkRequest {
  session_id: string;
  audio_data: string;
  format?: string;
  sample_rate?: number;
}

export interface VoiceHealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  active_sessions: number;
  features: string[];
  endpoints: {
    create_session: string;
    websocket: string;
    audio_http: string;
  };
  error?: string;
}

export class VoiceOrderingService {
  private baseUrl = '/api/v1/restaurant-voice';

  /**
   * Create a new voice ordering session
   */
  async createSession(token: string, request: VoiceSessionRequest): Promise<VoiceSession> {
    try {
      return await apiService.authPost<VoiceSession>(`${this.baseUrl}/sessions`, token, request);
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message || 'Failed to create voice session');
      }
      throw error;
    }
  }

  /**
   * Get information about a voice ordering session
   */
  async getSession(token: string, sessionId: string): Promise<VoiceSessionInfo> {
    try {
      return await apiService.authGet<VoiceSessionInfo>(`${this.baseUrl}/sessions/${sessionId}`, token);
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message || 'Failed to get voice session');
      }
      throw error;
    }
  }

  /**
   * End a voice ordering session
   */
  async endSession(token: string, sessionId: string): Promise<{ message: string }> {
    try {
      return await apiService.authDelete<{ message: string }>(`${this.baseUrl}/sessions/${sessionId}`, token);
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message || 'Failed to end voice session');
      }
      throw error;
    }
  }

  /**
   * List all active voice ordering sessions
   */
  async listSessions(token: string): Promise<{
    active_sessions: number;
    session_ids: string[];
    sessions: Record<string, VoiceSessionInfo>;
  }> {
    try {
      return await apiService.authGet(`${this.baseUrl}/sessions`, token);
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message || 'Failed to list sessions');
      }
      throw error;
    }
  }

  /**
   * Send an audio chunk to a voice session (HTTP alternative to WebSocket)
   */
  async sendAudioChunk(token: string, sessionId: string, request: AudioChunkRequest): Promise<{ message: string }> {
    try {
      return await apiService.authPost<{ message: string }>(`${this.baseUrl}/sessions/${sessionId}/audio`, token, request);
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message || 'Failed to send audio chunk');
      }
      throw error;
    }
  }

  /**
   * Check the health of the voice ordering service
   */
  async checkHealth(): Promise<VoiceHealthResponse> {
    try {
      return await apiService.get<VoiceHealthResponse>(`${this.baseUrl}/health`);
    } catch (error) {
      if (error instanceof ApiError) {
        throw new Error(error.message || 'Failed to check health');
      }
      throw error;
    }
  }

  /**
   * Get WebSocket URL for a session
   */
  getWebSocketUrl(sessionId: string): string {
    const baseWsUrl = process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') || 'ws://localhost:8000';
    return `${baseWsUrl}${this.baseUrl}/ws/${sessionId}`;
  }

  /**
   * Create a WebSocket connection for real-time voice streaming
   */
  createWebSocketConnection(sessionId: string): WebSocket {
    const wsUrl = this.getWebSocketUrl(sessionId);
    return new WebSocket(wsUrl);
  }
}

// Audio utility functions for voice processing
export class AudioUtils {
  /**
   * Convert PCM16 ArrayBuffer to Float32Array
   */
  static pcmToFloat32(buffer: ArrayBuffer): Float32Array {
    const int16Array = new Int16Array(buffer);
    const float32Array = new Float32Array(int16Array.length);
    for (let i = 0; i < int16Array.length; i++) {
      float32Array[i] = int16Array[i] / 32768;
    }
    return float32Array;
  }

  /**
   * Convert Float32Array to PCM16 ArrayBuffer
   */
  static float32ToPcm(float32Array: Float32Array): ArrayBuffer {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      int16Array[i] = Math.round(float32Array[i] * 32767);
    }
    return int16Array.buffer;
  }

  /**
   * Convert ArrayBuffer to Base64 string
   */
  static arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Convert Base64 string to ArrayBuffer
   */
  static base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }

  /**
   * Check if browser supports required audio APIs
   */
  static checkAudioSupport(): {
    getUserMedia: boolean;
    audioContext: boolean;
    webSocket: boolean;
    mediaRecorder: boolean;
  } {
    return {
      getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
      audioContext: !!(window.AudioContext || (window as any).webkitAudioContext),
      webSocket: !!window.WebSocket,
      mediaRecorder: !!window.MediaRecorder,
    };
  }

  /**
   * Request microphone permissions
   */
  static async requestMicrophonePermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('Microphone permission denied:', error);
      return false;
    }
  }

  /**
   * Get optimal audio configuration for voice recording
   */
  static getAudioConstraints(): MediaStreamConstraints {
    return {
      audio: {
        sampleRate: 16000,
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      }
    };
  }
}

// Export singleton instance
export const voiceOrderingService = new VoiceOrderingService();