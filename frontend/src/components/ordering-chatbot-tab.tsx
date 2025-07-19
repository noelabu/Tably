import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send as SendIcon } from 'lucide-react';

interface OrderingChatbotTabProps {
  chatMessages: any[];
  inputMessage: string;
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSendMessage: () => void;
  onSuggestedResponse: (response: string) => void;
  suggestedResponses: string[];
}

const OrderingChatbotTab: React.FC<OrderingChatbotTabProps> = ({
  chatMessages,
  inputMessage,
  onInputChange,
  onSendMessage,
  onSuggestedResponse,
  suggestedResponses,
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
              {message.content}
            </div>
          </div>
        ))}
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
        placeholder="Type your message..."
        onKeyPress={(e) => e.key === 'Enter' && onSendMessage()}
        className="flex-1"
      />
      <Button onClick={onSendMessage} className="bg-primary hover:bg-primary/90">
        <SendIcon className="w-4 h-4" />
      </Button>
    </div>
  </div>
);

export default OrderingChatbotTab; 