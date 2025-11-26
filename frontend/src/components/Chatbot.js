import { useState } from 'react';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';
import { toast } from 'sonner';
import axiosInstance from '@/utils/axios';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: 'Hi! 👋 How can I help you with CiteSight today?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessageToWebhook = async (message) => {
    try {
      const response = await axiosInstance.post('/chatbot-webhook', {
        message: message,
        timestamp: new Date().toISOString(),
        user_info: {
          page: window.location.pathname,
          referrer: document.referrer || 'direct'
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Webhook error:', error);
      throw error;
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim()) return;

    // Add user message to chat
    const userMessage = {
      type: 'user',
      text: inputMessage,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Send to webhook
      const response = await sendMessageToWebhook(inputMessage);
      
      console.log('Webhook response:', response);
      
      // Extract bot reply from various possible response formats
      let botReply = 'Thank you for your message! Our team will get back to you soon.';
      
      if (response) {
        // Try different response formats
        if (response.reply) {
          botReply = response.reply;
        } else if (response.message) {
          botReply = response.message;
        } else if (response.text) {
          botReply = response.text;
        } else if (response.response) {
          botReply = response.response;
        } else if (typeof response === 'string') {
          botReply = response;
        } else if (response.data) {
          // Handle nested data
          botReply = response.data.reply || response.data.message || response.data.text || botReply;
        }
      }
      
      // Add bot response
      const botMessage = {
        type: 'bot',
        text: botReply,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, botMessage]);
      toast.success('Message sent successfully!');
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage = {
        type: 'bot',
        text: 'Sorry, I encountered an error. Please try again or contact support@citesight.com',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: 'numeric',
      hour12: true
    }).format(date);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Window */}
      {isOpen && (
        <div 
          className="mb-4 bg-white rounded-2xl shadow-2xl w-96 h-[500px] flex flex-col overflow-hidden border border-slate-200"
          data-testid="chatbot-window"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Bot size={24} />
              </div>
              <div>
                <h3 className="font-bold">CiteSight Assistant</h3>
                <p className="text-xs text-blue-100">Always here to help</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-white/20 p-2 rounded-lg transition-colors"
              data-testid="close-chatbot"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'bot' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-slate-200 text-slate-700'
                }`}>
                  {message.type === 'bot' ? <Bot size={18} /> : <User size={18} />}
                </div>
                <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                  <div
                    className={`inline-block px-4 py-2 rounded-2xl max-w-[80%] ${
                      message.type === 'bot'
                        ? 'bg-white text-slate-800 border border-slate-200'
                        : 'bg-blue-600 text-white'
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{message.text}</p>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <Bot size={18} className="text-blue-600" />
                </div>
                <div className="bg-white px-4 py-2 rounded-2xl border border-slate-200">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-slate-200">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
                data-testid="chat-input"
              />
              <button
                type="submit"
                disabled={isLoading || !inputMessage.trim()}
                className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="send-message-button"
              >
                <Send size={20} />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-gradient-to-r from-blue-600 to-blue-700 text-white w-16 h-16 rounded-full shadow-2xl hover:shadow-blue-500/50 transition-all hover:scale-110 flex items-center justify-center"
        data-testid="chatbot-toggle"
      >
        {isOpen ? <X size={28} /> : <MessageCircle size={28} />}
        
        {/* Notification Dot */}
        {!isOpen && (
          <span className="absolute top-1 right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
        )}
      </button>
    </div>
  );
};

export default Chatbot;
