import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { useTranslation } from '@/hooks/useTranslation';
import { useVoiceRecording } from '@/hooks/useVoiceRecording';
import { askCropQuestion, clearConversationHistory } from '@/lib/gemini';
import { MessageCircle, X, Mic, Send, Bot, User, Trash2 } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export default function ChatBot() {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const {
    isRecording,
    transcript,
    startRecording,
    stopRecording,
    setTranscript,
    language,
    setLanguage,
  } = useVoiceRecording();

  // welcome message only when opening first time
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: '1',
          text: t('chat_greeting'),
          isUser: false,
          timestamp: new Date(),
        },
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  useEffect(() => {
    if (transcript && !isRecording) {
      setInputMessage(transcript);
      setTranscript('');
    }
  }, [transcript, isRecording, setTranscript]);

  // always scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [messages, isOpen]);

  const sendMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await askCropQuestion(message);
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      const errorText = error?.message || "I'm having trouble connecting right now. Please try again later.";
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: errorText,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = () => sendMessage(inputMessage);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    t('quick_crop_health'),
    t('quick_fertilizer'),
    t('quick_weather'),
  ];

  const handleClearHistory = async () => {
    try {
      await clearConversationHistory();
      setMessages([{
        id: '1',
        text: t('chat_greeting'),
        isUser: false,
        timestamp: new Date(),
      }]);
    } catch (err) {
      console.error('Failed to clear history:', err);
    }
  };

  return (
    <>
      {/* Toggle Button (Fixed on Desktop & Mobile) */}
      <div className={`fixed bottom-6 right-6 z-40 transition-all duration-300 ${isOpen ? 'opacity-0 pointer-events-none md:opacity-100 md:pointer-events-auto' : 'opacity-100'}`}>
        <Button
          onClick={() => setIsOpen(true)}
          className="w-14 h-14 md:w-16 md:h-16 rounded-full shadow-lg hover:shadow-xl transition-transform hover:scale-105 bg-primary hover:bg-primary/90 flex items-center justify-center"
          aria-label="Open Chat"
        >
          <MessageCircle className="h-6 w-6 md:h-7 md:w-7 text-white" />
        </Button>
      </div>

      {/* Chat Panel Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-end md:items-end justify-center md:right-6 md:bottom-24 md:left-auto md:w-auto md:h-auto pointer-events-none">
          {/* 
              Mobile: Full screen / Large Modal 
              Desktop: Popover Card 
          */}
          <Card className="pointer-events-auto w-full h-[100dvh] md:w-[450px] md:h-[600px] md:rounded-xl shadow-2xl flex flex-col animate-in slide-in-from-bottom-10 fade-in duration-300 border-0 md:border">

            {/* Header */}
            <CardHeader className="flex-shrink-0 bg-primary text-primary-foreground p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                    <Bot className="text-white h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg leading-none">{t('crop_assistant')}</h3>
                    <p className="text-xs text-primary-foreground/80 mt-1">{t('ai_powered')}</p>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  <Button variant="ghost" size="icon" onClick={handleClearHistory} title={t('clear_history')} className="text-primary-foreground hover:bg-white/20">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)} className="text-primary-foreground hover:bg-white/20">
                    <X className="h-6 w-6" />
                  </Button>
                </div>
              </div>
            </CardHeader>

            {/* Messages Area */}
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/20">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm shadow-sm ${message.isUser
                      ? 'bg-primary text-primary-foreground rounded-br-none'
                      : 'bg-white text-foreground border rounded-bl-none'
                      }`}
                  >
                    {message.text}
                    <div className={`text-[10px] mt-1 text-right ${message.isUser ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-white border rounded-2xl rounded-bl-none px-4 py-3 shadow-sm">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                      <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </CardContent>

            {/* Input Area */}
            <div className="p-4 bg-background border-t">
              {/* Quick Questions Chips */}
              {messages.length < 3 && (
                <div className="flex gap-2 overflow-x-auto pb-3 no-scrollbar mb-2">
                  {quickQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(q)}
                      className="flex-shrink-0 text-xs bg-muted/50 hover:bg-muted border rounded-full px-3 py-1.5 transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}

              <div className="flex gap-2 items-center">
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="h-10 text-xs rounded-md border bg-background px-2 w-[80px]"
                >
                  <option value="en-US">EN</option>
                  <option value="hi-IN">हिंदी</option>
                  <option value="pa-IN">ਪં</option>
                </select>

                <div className="flex-1 relative">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={t('chat_input')}
                    className="pr-10"
                  />
                  <Button
                    size="icon"
                    variant="ghost"
                    className={`absolute right-1 top-1 h-8 w-8 ${isRecording ? 'text-red-500 animate-pulse' : 'text-muted-foreground'}`}
                    onClick={isRecording ? stopRecording : startRecording}
                  >
                    <Mic className="h-4 w-4" />
                  </Button>
                </div>

                <Button size="icon" onClick={handleSend} disabled={!inputMessage.trim() || isLoading}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>

          </Card>
        </div>
      )}
    </>
  );
}
