import React from 'react';
import { Button } from '@/components/ui/button';
import { Mic } from 'lucide-react';

interface OrderingVoiceTabProps {
  isListening: boolean;
  transcribedText: string;
  toggleVoiceListening: () => void;
}

const OrderingVoiceTab: React.FC<OrderingVoiceTabProps> = ({ isListening, transcribedText, toggleVoiceListening }) => (
  <div className="h-full flex flex-col items-center justify-center space-y-8">
    <div className="text-center space-y-4">
      <h2 className="text-2xl font-semibold text-foreground">Voice Ordering</h2>
      <p className="text-muted-foreground">
        Tap the microphone and tell us what you'd like to order
      </p>
    </div>
    {/* Microphone Button */}
    <Button
      onClick={toggleVoiceListening}
      className={`w-32 h-32 rounded-full ${
        isListening ? 'bg-red-500 hover:bg-red-600 animate-pulse' : 'bg-primary hover:bg-primary/90'
      } flex items-center justify-center text-white text-4xl`}
    >
      <Mic className="w-16 h-16" />
    </Button>
    {/* Transcribed Text */}
    <div className="text-lg text-muted-foreground min-h-[2rem]">
      {transcribedText}
    </div>
  </div>
);

export default OrderingVoiceTab; 