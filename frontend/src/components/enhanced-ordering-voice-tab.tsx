"use client";

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Mic, MicOff, Volume2, VolumeX, Loader2, MessageCircle } from 'lucide-react';
import { useAuthStore } from '@/stores/auth.store';
import { useCartStore, type VoiceCartEvent } from '@/stores/cart.store';
import { voiceOrderingService, AudioUtils, type VoiceSession } from '@/services/voice-ordering';
import { useAudioSupport } from '@/hooks/use-audio-support';


interface EnhancedOrderingVoiceTabProps {
  businessId: string;
  onError?: (error: string) => void;
  onSessionStart?: () => void;
  onSessionEnd?: () => void;
}


const EnhancedOrderingVoiceTab: React.FC<EnhancedOrderingVoiceTabProps> = ({ 
  businessId, 
  onError,
  onSessionStart,
  onSessionEnd
}) => {
  // State management
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const [currentSession, setCurrentSession] = useState<VoiceSession | null>(null);
  const [conversationHistory, setConversationHistory] = useState<Array<{ type: 'user' | 'assistant', content: string, timestamp: Date }>>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [debugMode, setDebugMode] = useState(false);

  // Refs for audio handling
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioWorkletRef = useRef<AudioWorkletNode | null>(null);
  const recordingChunksRef = useRef<Blob[]>([]);
  
  // Audio queue system for fluid playback
  const audioQueueRef = useRef<Array<{ data: string; sampleRate: number }>>([]);
  const isPlayingQueueRef = useRef(false);
  const currentSourceRef = useRef<AudioBufferSourceNode | null>(null);
  
  // Get auth token
  const token = useAuthStore((state) => state.tokens?.access_token || '');
  
  // Cart store for voice synchronization
  const { syncFromVoice, setBusinessId } = useCartStore();
  
  // Audio support check
  const audioSupport = useAudioSupport();

  // Set business ID in cart store when component mounts
  useEffect(() => {
    setBusinessId(businessId);
  }, [businessId, setBusinessId]);

  // Create voice session
  const createVoiceSession = useCallback(async (): Promise<VoiceSession> => {
    const response = await voiceOrderingService.createSession(token, {
      business_id: businessId,
      debug: debugMode,
    });
    console.log('Voice session created:', response);

    return response;
  }, [businessId, token, debugMode]);

  // Setup WebSocket connection
  const setupWebSocket = useCallback((session: VoiceSession) => {
    console.log('Setting up WebSocket for session:', session.session_id);
    const wsUrl = voiceOrderingService.getWebSocketUrl(session.session_id);
    console.log('WebSocket URL:', wsUrl);
    
    const ws = voiceOrderingService.createWebSocketConnection(session.session_id);

    ws.onopen = () => {
      console.log('WebSocket connected successfully');
      setConnectionStatus('connected');
      setConversationHistory(prev => [...prev, {
        type: 'assistant',
        content: 'Voice session connected! I\'m ready to help you place your order.',
        timestamp: new Date()
      }]);
    };

    ws.onmessage = async (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('Received WebSocket message:', data.type, data);
        
        switch (data.type) {
          case 'session_ready':
            console.log('Voice session ready:', data.message);
            setConversationHistory(prev => [...prev, {
              type: 'assistant',
              content: data.message,
              timestamp: new Date()
            }]);
            
            // Send an initial trigger to start the conversation
            setTimeout(() => {
              if (ws.readyState === WebSocket.OPEN) {
                console.log('Sending initial trigger');
                ws.send(JSON.stringify({
                  type: 'start_conversation',
                  message: 'Hello'
                }));
              }
            }, 1000);
            break;
            
          case 'audio_output':
            console.log('Received audio_output:', {
              muted: isMuted,
              hasAudioData: !!data.audio_data,
              audioDataLength: data.audio_data?.length,
              sampleRate: data.sample_rate
            });
            if (!isMuted && data.audio_data) {
              console.log('Playing audio from base64, length:', data.audio_data.length);
              await playAudioFromBase64(data.audio_data, data.sample_rate || 24000);
            } else {
              console.log('Skipping audio playback - muted or no data');
            }
            break;
            
          case 'text_output':
            setConversationHistory(prev => [...prev, {
              type: 'assistant',
              content: data.content,
              timestamp: new Date()
            }]);
            break;
            
          case 'cart_updated':
            console.log('Received cart update:', data);
            try {
              // Sync cart with voice agent updates
              syncFromVoice(data as VoiceCartEvent);
              
              // Add cart update to conversation history for user visibility
              const actionText = data.action === 'add' ? 'Added to cart' : 
                                data.action === 'remove' ? 'Removed from cart' : 
                                data.action === 'update' ? 'Updated cart' : 
                                data.action === 'clear' ? 'Cleared cart' : 'Cart updated';
              
              const itemText = data.item ? `: ${data.item.name} (${data.item.quantity}x)` : '';
              const totalText = ` | Total: $${data.cart_total?.toFixed(2) || '0.00'}`;
              
              setConversationHistory(prev => [...prev, {
                type: 'assistant',
                content: `${actionText}${itemText}${totalText}`,
                timestamp: new Date()
              }]);
              
            } catch (error) {
              console.error('Error handling cart update:', error);
            }
            break;
            
          case 'pong':
            console.log('Received pong');
            break;
            
          case 'heartbeat':
            console.log('Received heartbeat');
            break;
            
          default:
            console.log('Unknown message type:', data.type);
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      console.error('WebSocket readyState:', ws.readyState);
      console.error('WebSocket URL was:', wsUrl);
      setConnectionStatus('error');
      setErrorMessage(`WebSocket connection error: ${error}`);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnectionStatus('disconnected');
      setIsSessionActive(false);
      setIsRecording(false);
    };

    wsRef.current = ws;
  }, [isMuted]);

  // Add audio chunk to queue for fluid playback
  const enqueueAudio = useCallback((base64Data: string, sampleRate: number = 24000) => {
    audioQueueRef.current.push({ data: base64Data, sampleRate });
    console.log('Audio chunk enqueued. Queue length:', audioQueueRef.current.length);
    
    // Start processing queue if not already playing
    if (!isPlayingQueueRef.current) {
      processAudioQueue();
    }
  }, []);

  // Process audio queue for seamless playback
  const processAudioQueue = useCallback(async () => {
    if (isPlayingQueueRef.current || audioQueueRef.current.length === 0) {
      return;
    }

    isPlayingQueueRef.current = true;
    setIsPlaying(true);

    try {
      // Create audio context if needed
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        console.log('Created new AudioContext');
      }

      const audioContext = audioContextRef.current;
      
      // Resume audio context if suspended
      if (audioContext.state === 'suspended') {
        console.log('Resuming suspended AudioContext');
        await audioContext.resume();
      }

      let startTime = audioContext.currentTime;
      const sources: AudioBufferSourceNode[] = [];

      // Process all chunks in queue
      while (audioQueueRef.current.length > 0) {
        const chunk = audioQueueRef.current.shift()!;
        
        try {
          // Decode base64 to binary
          const bytes = AudioUtils.base64ToArrayBuffer(chunk.data);
          
          // Convert PCM to Float32Array
          const float32Data = AudioUtils.pcmToFloat32(bytes);
          
          // Create audio buffer
          const audioBuffer = audioContext.createBuffer(1, float32Data.length, chunk.sampleRate);
          audioBuffer.copyToChannel(float32Data, 0);
          
          // Create source and schedule playback
          const source = audioContext.createBufferSource();
          source.buffer = audioBuffer;
          source.connect(audioContext.destination);
          
          // Schedule this chunk to play immediately after the previous one
          source.start(startTime);
          startTime += audioBuffer.duration;
          
          sources.push(source);
          currentSourceRef.current = source;
          
          console.log(`Audio chunk scheduled at ${startTime - audioBuffer.duration}, duration: ${audioBuffer.duration}s`);
          
        } catch (chunkError) {
          console.error('Error processing audio chunk:', chunkError);
        }
      }

      // Set up completion handler for the last source
      if (sources.length > 0) {
        const lastSource = sources[sources.length - 1];
        lastSource.onended = () => {
          console.log('Audio queue playback completed');
          isPlayingQueueRef.current = false;
          currentSourceRef.current = null;
          setIsPlaying(false);
          
          // Check if more audio was queued while playing
          if (audioQueueRef.current.length > 0) {
            console.log('More audio queued, continuing playback...');
            processAudioQueue();
          }
        };
      }

    } catch (error) {
      console.error('Error processing audio queue:', error);
      isPlayingQueueRef.current = false;
      setIsPlaying(false);
    }
  }, []);

  // Stop current audio playback
  const stopAudioPlayback = useCallback(() => {
    if (currentSourceRef.current) {
      try {
        currentSourceRef.current.stop();
        currentSourceRef.current = null;
      } catch (error) {
        console.warn('Error stopping audio source:', error);
      }
    }
    
    // Clear queue and reset state
    audioQueueRef.current = [];
    isPlayingQueueRef.current = false;
    setIsPlaying(false);
    console.log('Audio playback stopped and queue cleared');
  }, []);

  // Legacy function for backward compatibility (now uses queue)
  const playAudioFromBase64 = useCallback(async (base64Data: string, sampleRate: number = 24000) => {
    enqueueAudio(base64Data, sampleRate);
  }, [enqueueAudio]);

  // Create ref to track recording state to avoid stale closures
  const isRecordingRef = useRef(false);
  
  // Setup audio recording
  const setupAudioRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });

      audioStreamRef.current = stream;

      // Create audio context for processing
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      const audioContext = audioContextRef.current;
      const source = audioContext.createMediaStreamSource(stream);

      // Create ScriptProcessorNode for real-time audio processing
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      
      // Store processor ref for cleanup
      const processorRef = processor;
      
      processor.onaudioprocess = (event) => {
        // Use ref to avoid stale closure
        if (!isRecordingRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

        const inputBuffer = event.inputBuffer;
        const channelData = inputBuffer.getChannelData(0);
        
        // Convert to PCM16
        const pcmData = AudioUtils.float32ToPcm(channelData);
        const base64Data = AudioUtils.arrayBufferToBase64(pcmData);

        // Send to WebSocket
        console.log('Sending audio data, length:', base64Data.length);
        wsRef.current.send(JSON.stringify({
          type: 'audio_input',
          audio_data: base64Data,
          format: 'pcm16',
          sample_rate: 16000
        }));
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      return () => {
        processorRef.disconnect();
        source.disconnect();
        stream.getTracks().forEach(track => track.stop());
      };

    } catch (error) {
      console.error('Error setting up audio recording:', error);
      throw new Error('Failed to access microphone. Please check permissions.');
    }
  }, []);

  // Start voice session
  const startVoiceSession = useCallback(async () => {
    try {
      setIsConnecting(true);
      setErrorMessage(null);
      setConnectionStatus('connecting');

      // Check audio support
      if (!audioSupport.isSupported) {
        throw new Error('Your browser does not support voice features');
      }

      if (!audioSupport.hasPermission) {
        const hasPermission = await audioSupport.requestPermission();
        if (!hasPermission) {
          throw new Error('Microphone permission is required for voice ordering');
        }
      }

      // Initialize AudioContext early to enable playback (requires user interaction)
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        console.log('AudioContext created during user interaction');
        // Resume immediately if suspended
        if (audioContextRef.current.state === 'suspended') {
          await audioContextRef.current.resume();
          console.log('AudioContext resumed');
        }
      }

      // Create session
      const session = await createVoiceSession();
      setCurrentSession(session);

      // Setup WebSocket
      setupWebSocket(session);

      // Setup audio recording (but don't fail if it doesn't work immediately)
      try {
        await setupAudioRecording();
      } catch (audioError) {
        console.warn('Audio setup failed, but WebSocket connection will remain:', audioError);
        setErrorMessage('Audio setup failed. Please check microphone permissions.');
      }

      setIsSessionActive(true);
      onSessionStart?.();

    } catch (error) {
      console.error('Error starting voice session:', error);
      const errorMsg = error instanceof Error ? error.message : 'Failed to start voice session';
      setErrorMessage(errorMsg);
      setConnectionStatus('error');
      onError?.(errorMsg);
    } finally {
      setIsConnecting(false);
    }
  }, [createVoiceSession, setupWebSocket, setupAudioRecording, onSessionStart, onError, audioSupport]);

  // End voice session
  const endVoiceSession = useCallback(async () => {
    try {
      // Stop recording
      setIsRecording(false);

      // Stop any ongoing audio playback
      stopAudioPlayback();

      // Close WebSocket
      if (wsRef.current) {
        // Only send end_session message if WebSocket is in OPEN state
        if (wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'end_session' }));
        }
        wsRef.current.close();
        wsRef.current = null;
      }

      // Stop audio stream
      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop());
        audioStreamRef.current = null;
      }

      // Close audio context
      if (audioContextRef.current) {
        await audioContextRef.current.close();
        audioContextRef.current = null;
      }

      // Delete session
      if (currentSession) {
        await voiceOrderingService.endSession(token, currentSession.session_id);
      }

      setIsSessionActive(false);
      setCurrentSession(null);
      setConnectionStatus('disconnected');
      onSessionEnd?.();

    } catch (error) {
      console.error('Error ending voice session:', error);
    }
  }, [currentSession, token, onSessionEnd, stopAudioPlayback]);

  // Toggle recording
  const toggleRecording = useCallback(() => {
    setIsRecording(prev => {
      const newValue = !prev;
      isRecordingRef.current = newValue; // Update ref for audio processor
      return newValue;
    });
    
    if (!isRecording) {
      console.log('Starting microphone recording');
      setConversationHistory(prev => [...prev, {
        type: 'user',
        content: '[Started speaking...]',
        timestamp: new Date()
      }]);
    } else {
      console.log('Stopping microphone recording');
      setConversationHistory(prev => [...prev, {
        type: 'user',
        content: '[Stopped speaking]',
        timestamp: new Date()
      }]);
    }
  }, [isRecording]);

  // Cleanup on unmount - use ref to avoid stale closure
  const isSessionActiveRef = useRef(isSessionActive);
  isSessionActiveRef.current = isSessionActive;
  
  useEffect(() => {
    return () => {
      // Only cleanup when component actually unmounts and session is active
      if (isSessionActiveRef.current && wsRef.current) {
        console.log('Component unmounting - cleaning up voice session');
        // Close WebSocket immediately to prevent backend errors
        if (wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.close();
        }
        wsRef.current = null;
      }
    };
  }, []); // Empty dependency array - only run on mount/unmount

  // Send periodic ping to keep connection alive
  useEffect(() => {
    if (!isSessionActive || !wsRef.current) return;

    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // 30 seconds

    return () => clearInterval(pingInterval);
  }, [isSessionActive]);

  return (
    <div className="h-full flex flex-col space-y-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <h2 className="text-2xl font-semibold text-foreground">Voice Ordering</h2>
        <p className="text-muted-foreground">
          Have a natural conversation with our AI assistant to place your order
        </p>
        
        {/* Connection Status */}
        <div className="flex items-center justify-center space-x-2">
          <Badge variant={
            connectionStatus === 'connected' ? 'default' : 
            connectionStatus === 'connecting' ? 'secondary' : 
            connectionStatus === 'error' ? 'destructive' : 'outline'
          }>
            {connectionStatus === 'connected' && '🟢 Connected'}
            {connectionStatus === 'connecting' && '🟡 Connecting...'}
            {connectionStatus === 'disconnected' && '⚫ Disconnected'}
            {connectionStatus === 'error' && '🔴 Error'}
          </Badge>
          
          {isPlaying && (
            <Badge variant="secondary">
              🔊 Playing Response
            </Badge>
          )}
          
        </div>
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <Alert variant="destructive">
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      {/* Audio Support Alert */}
      {audioSupport.error && (
        <Alert variant="destructive">
          <AlertDescription>
            {audioSupport.error}
            {!audioSupport.hasPermission && (
              <Button
                variant="outline"
                size="sm"
                onClick={audioSupport.requestPermission}
                className="ml-2"
                disabled={audioSupport.isLoading}
              >
                {audioSupport.isLoading ? 'Checking...' : 'Grant Permission'}
              </Button>
            )}
          </AlertDescription>
        </Alert>
      )}

      {/* Main Controls */}
      <div className="flex-1 flex flex-col items-center justify-center space-y-8">
        {!isSessionActive ? (
          /* Start Session Button */
          <Button
            onClick={startVoiceSession}
            disabled={isConnecting || !token || !audioSupport.isSupported || audioSupport.isLoading}
            className="w-40 h-40 rounded-full bg-primary hover:bg-primary/90 flex items-center justify-center text-white"
          >
            {isConnecting ? (
              <Loader2 className="w-20 h-20 animate-spin" />
            ) : (
              <div className="text-center">
                <Mic className="w-16 h-16 mx-auto mb-2" />
                <span className="text-sm">Start Voice Chat</span>
              </div>
            )}
          </Button>
        ) : (
          /* Voice Controls */
          <div className="flex flex-col items-center space-y-6">
            {/* Recording Button */}
            <Button
              onClick={toggleRecording}
              className={`w-32 h-32 rounded-full ${
                isRecording 
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                  : 'bg-green-500 hover:bg-green-600'
              } flex items-center justify-center text-white`}
            >
              {isRecording ? (
                <MicOff className="w-16 h-16" />
              ) : (
                <Mic className="w-16 h-16" />
              )}
            </Button>

            <div className="text-center space-y-2">
              <p className="text-lg font-medium">
                {isRecording ? 'Listening... Speak naturally' : 'Tap to speak'}
              </p>
              <p className="text-sm text-muted-foreground">
                Say something like "I'd like a burger and fries"
              </p>
            </div>

            {/* Control Buttons */}
            <div className="flex space-x-4">
              <Button
                variant="outline"
                onClick={() => setIsMuted(!isMuted)}
                className="flex items-center space-x-2"
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                <span>{isMuted ? 'Unmute' : 'Mute'}</span>
              </Button>


              {isPlaying && (
                <Button
                  variant="outline"
                  onClick={stopAudioPlayback}
                  className="flex items-center space-x-2"
                >
                  <VolumeX className="w-4 h-4" />
                  <span>Stop Audio</span>
                </Button>
              )}

              <Button
                variant="destructive"
                onClick={endVoiceSession}
                className="flex items-center space-x-2"
              >
                <MicOff className="w-4 h-4" />
                <span>End Session</span>
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <h3 className="font-semibold mb-3 flex items-center space-x-2">
              <MessageCircle className="w-4 h-4" />
              <span>Conversation</span>
            </h3>
            <div className="space-y-3 max-h-40 overflow-y-auto">
              {conversationHistory.slice(-5).map((msg, index) => (
                <div key={index} className={`text-sm ${
                  msg.type === 'user' ? 'text-blue-600' : 'text-green-600'
                }`}>
                  <span className="font-medium">
                    {msg.type === 'user' ? 'You: ' : 'Assistant: '}
                  </span>
                  <span>{msg.content}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Debug Toggle */}
      <div className="text-center">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setDebugMode(!debugMode)}
          className="text-xs text-muted-foreground"
        >
          Debug: {debugMode ? 'ON' : 'OFF'}
        </Button>
      </div>
    </div>
  );
};

export default EnhancedOrderingVoiceTab;