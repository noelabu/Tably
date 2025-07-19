import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send as SendIcon, Loader2, Bot, User } from 'lucide-react';

interface OrderingChatbotTabProps {
  chatMessages: any[];
  inputMessage: string;
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSendMessage: () => void;
  onSuggestedResponse: (response: string) => void;
  suggestedResponses: string[];
  isLoading?: boolean;
  disabled?: boolean;
}

const OrderingChatbotTab: React.FC<OrderingChatbotTabProps> = ({
  chatMessages,
  inputMessage,
  onInputChange,
  onSendMessage,
  onSuggestedResponse,
  suggestedResponses,
  isLoading = false,
  disabled = false,
}) => (
  <div className="flex-1 flex flex-col space-y-4">
    {/* Chat Messages */}
    <ScrollArea className="flex-1 bg-muted rounded-lg p-4">
      <div className="space-y-4">
        {chatMessages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-card text-card-foreground border border-border'
              }`}
            >
              <div className="flex items-start gap-2">
                {message.type === 'bot' && <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                {message.type === 'user' && <User className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                <div className="flex-1 min-w-0">
                  <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                  <p className="text-xs opacity-60 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md bg-card text-card-foreground border border-border rounded-lg px-4 py-2 flex items-center gap-2">
              <Bot className="w-4 h-4 flex-shrink-0" />
              <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
              <span className="text-sm">Typing...</span>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
    {/* Suggested Responses */}
    <div className="flex flex-wrap gap-2">
      {suggestedResponses.map((response, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          onClick={() => onSuggestedResponse(response)}
          className="text-sm"
        >
          {response}
        </Button>
      ))}
    </div>
    {/* Message Input */}
    <div className="flex gap-2">
      <Input
        value={inputMessage}
        onChange={onInputChange}
        placeholder={isLoading ? "Waiting for response..." : "Type your message..."}
        onKeyPress={(e) => e.key === 'Enter' && !isLoading && onSendMessage()}
        disabled={isLoading || disabled}
        className="flex-1"
      />
      <Button 
        onClick={onSendMessage} 
        disabled={isLoading || !inputMessage.trim() || disabled}
        className="bg-primary hover:bg-primary/90"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <SendIcon className="w-4 h-4" />
        )}
      </Button>
    </div>
  </div>
);

export default OrderingChatbotTab; 