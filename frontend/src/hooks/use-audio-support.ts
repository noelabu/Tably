import { useState, useEffect } from 'react';
import { AudioUtils } from '@/services/voice-ordering';

interface AudioSupportStatus {
  isSupported: boolean;
  hasPermission: boolean;
  isLoading: boolean;
  error: string | null;
  support: {
    getUserMedia: boolean;
    audioContext: boolean;
    webSocket: boolean;
    mediaRecorder: boolean;
  };
}

export const useAudioSupport = () => {
  const [status, setStatus] = useState<AudioSupportStatus>({
    isSupported: false,
    hasPermission: false,
    isLoading: true,
    error: null,
    support: {
      getUserMedia: false,
      audioContext: false,
      webSocket: false,
      mediaRecorder: false,
    },
  });

  useEffect(() => {
    const checkSupport = async () => {
      try {
        setStatus(prev => ({ ...prev, isLoading: true, error: null }));

        // Check browser support
        const support = AudioUtils.checkAudioSupport();
        const isSupported = Object.values(support).every(Boolean);

        if (!isSupported) {
          setStatus({
            isSupported: false,
            hasPermission: false,
            isLoading: false,
            error: 'Browser does not support required audio features',
            support,
          });
          return;
        }

        // Check microphone permission
        let hasPermission = false;
        try {
          hasPermission = await AudioUtils.requestMicrophonePermission();
        } catch (error) {
          console.error('Permission check failed:', error);
        }

        setStatus({
          isSupported,
          hasPermission,
          isLoading: false,
          error: hasPermission ? null : 'Microphone permission required',
          support,
        });

      } catch (error) {
        setStatus(prev => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Unknown error checking audio support',
        }));
      }
    };

    checkSupport();
  }, []);

  const requestPermission = async (): Promise<boolean> => {
    try {
      setStatus(prev => ({ ...prev, isLoading: true, error: null }));
      
      const hasPermission = await AudioUtils.requestMicrophonePermission();
      
      setStatus(prev => ({
        ...prev,
        hasPermission,
        isLoading: false,
        error: hasPermission ? null : 'Microphone permission denied',
      }));

      return hasPermission;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to request permission';
      setStatus(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      return false;
    }
  };

  return {
    ...status,
    requestPermission,
  };
};