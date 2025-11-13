import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Bot, User, CheckCircle, Tag } from 'lucide-react';
import { sendChatMessage } from '../../services/api';

function ChatInterface({ sessionId, onQueryComplete }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I can help you analyze your balance sheet. Ask me questions about your financial data.',
      metadata: {}
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await sendChatMessage(sessionId, input, chatHistory);
      
      if (response.success) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: response.answer,
          metadata: {
            citations: response.citations || [],
            routeInfo: response.route_info,
            grounded: response.grounding_check?.is_grounded,
            pipeline: response.pipeline
          }
        }]);
        if (onQueryComplete) onQueryComplete();
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: 'Sorry, I encountered an error: ' + (response.error || 'Unknown error'),
          metadata: {}
        }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error: ' + error.message,
        metadata: {}
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[700px]">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center gap-2">
        <MessageCircle className="h-6 w-6 text-blue-600" />
        <h2 className="text-2xl font-semibold text-gray-800">Intelligent RAG Chat</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Bot className="h-5 w-5 text-blue-600" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-50 text-gray-800 border border-gray-200'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              
              {message.role === 'assistant' && message.metadata && (
                <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                  {message.metadata.citations && message.metadata.citations.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {message.metadata.citations.map((citation, idx) => (
                        <span 
                          key={idx}
                          className="inline-flex items-center space-x-1 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full"
                        >
                          <Tag className="h-3 w-3" />
                          <span>{citation}</span>
                        </span>
                      ))}
                    </div>
                  )}
                  
                  {message.metadata.grounded && (
                    <div className="flex items-center space-x-1 text-xs text-green-600">
                      <CheckCircle className="h-3 w-3" />
                      <span>Verified & Grounded</span>
                    </div>
                  )}
                  
                  {message.metadata.pipeline && (
                    <div className="text-xs text-gray-500">
                      Pipeline: {message.metadata.pipeline}
                    </div>
                  )}
                </div>
              )}
            </div>
            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="h-5 w-5 text-gray-600" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <Bot className="h-5 w-5 text-blue-600" />
            </div>
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <p className="text-sm text-gray-600">Thinking...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSend} className="border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your balance sheet..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-2 transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInterface;

